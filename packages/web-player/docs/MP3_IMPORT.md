# M4A import conversion and storage recovery — 2026-10-01

## Delivered behavior

New Add music uploads accept MP3 and M4A. MP3 is kept unchanged; M4A is converted before hashing, duplicate review, metadata probing and browser storage. Other new upload formats are rejected. Existing historical files and Restore saved batch remain readable without automatic conversion.

Analysis has a provisional **Convert M4A to MP3** button beside **Analyze Tracks**. It processes the whole local browser collection sequentially, skips MP3, reports other unsupported formats, preserves track IDs, playlist references and metadata, and clears stale features for changed audio. No whole-library conversion or analysis was launched by the agent.

The installed FFmpeg runs locally with libmp3lame VBR quality 2, one encoder thread, first audio stream and mapped metadata. No new runtime dependency or model is loaded. Endpoint `POST /api/local/convert-m4a?filename=...` requires the existing loopback Host/Origin/header checks; input/output are bounded at 512 MB. Conversion and analysis cannot run concurrently through the service. Converter has a five-minute timeout, disconnect cancellation and temporary-file cleanup. MP3 transcoding is lossy; this is a compatibility choice, not an audio-quality improvement.

Original disk files are never changed. Existing browser replacements atomically back up `{audio, track}` in the existing `audio` object store at `conversion-backup:<track-id>:<old-hash>` before replacing the active copy. Backups include old analysis; no restore UI is implemented yet. These backups consume browser storage and are not independent backups against site-data removal. Changed hashes require fresh analysis and fresh audio embeddings; stale embeddings are not reused across converted audio. Unchanged MP3 files retain their caches.

## Storage fix

Reads and analysis-result saves reopen a closed IndexedDB connection once. Persistent storage failures receive `LIBRARY_STORAGE_UNAVAILABLE`; the analysis queue stops immediately and reports that remaining tracks were not attempted. Ordinary per-track estimator failures still allow the queue to continue. Result saves and conversion recheck the source hash within their write transaction, preventing stale analysis from attaching after another tab replaces the audio. Completed server caches remain recoverable by the same audio hash.

## Verification and incident follow-up

- 90 Node tests pass, including real generated AAC-to-MP3 conversion, preserved duration/title/source bytes, invalid-input rejection, MP3 passthrough, format rejection, transient reconnect, persistent-failure queue stop, atomic backup/identity preservation and stale-hash rejection.
- JavaScript syntax checks and production build pass.
- Live port 4173 conversion of a generated two-second M4A returned MP3, duration 2.020136 seconds.
- Chrome shows the new button beside Analyze Tracks. No user tracks were converted by the agent.
- On reload, Chrome showed zero tracks. A read-only diagnostic confirmed zero rows in `resonant-library-v1/tracks`; this was not just an empty filter. No conversion, record deletion or database migration was performed by this change. The cause of missing browser data is unresolved; the prior connection-closing error alone does not establish it. Existing on-disk feature caches remain. Audio needs restoring through Restore saved batch where available, or re-adding from originals. Do not claim the previous 237-track browser collection is intact or recovered.
- The original failing owner M4A was not retested through all estimators. Compatibility was verified with generated audio and the endpoint; full owner-library analysis remains manual.

## Continuation

Reload other old player tabs to load these fixes. Restore/re-add audio, use Convert M4A to MP3 for historical browser M4A copies, then launch Analyze Tracks. New M4A uploads already convert automatically. Broader format support is deliberately deferred.
