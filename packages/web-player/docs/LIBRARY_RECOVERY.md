# Chrome library recovery and PlaylistIQ playback — 2026-09-19

## 2026-10-01 — Expanded recovery after the 54-track limit

The old recovery button was deliberately restricted to cached analysis in three flat source folders; it excluded new_albums, nested albums and uncached tracks. It was not a backup of the full browser collection. The owner reported only 54 restored tracks after losing a collection of more than 200.

Recovery now recursively scans the fixed project test_music root, including new_albums, excludes symlinks, deduplicates exact SHA-256, and restores source audio even without analysis. Saved features are attached only when available; missing features are never invented. Existing source bytes are preserved so compatible analysis remains reusable; M4A conversion stays a separate owner action after recovery. Source paths remain absent from public listings. Persistent storage errors stop recovery.

Measured disk inventory: 295 audio files, 255 unique hashes, 59 with valid saved web-feature records, 196 without. With 54 already restored, the next run can add 201, subject to browser audio/storage failures. This restores all available local originals, not an exact reconstruction of the previous 237-track selection; previously unloaded files may be included. Other cached hashes without matching originals in test_music cannot supply playable audio. Playlists/preferences are not reconstructed.

Verification: 92 web tests pass, including recursive uncached recovery, symlink exclusion, hash checking and idempotence; syntax/build pass. Live endpoint reports 255 entries/59 analyzed and no source paths. Server restarted on port 4173. No owner audio imported, converted or analyzed by this repair; reload and click Restore saved batch again.

## Delivered

- Analysis displays one row per identical audio SHA-256. The representative with the most complete saved analysis is preferred. Titles/filenames never establish equality. Stored copies and their IDs remain intact, preserving existing playlists and favorites.
- PlaylistIQ uses that same unique audio pool. Each matching result has an accessible Play button. It loads the ranked matching tracks into the main player and starts the selected result; the player's existing shuffle setting still applies. Unavailable/deleted results are skipped or reported. Playback does not save a new playlist.
- The local **Restore saved batch** action restores known, previously analyzed project audio to the current browser's library, including its saved features. It can be repeated without importing the same content again.
- Loading/importing existing audio reattaches missing cached features and upgrades partial features when a stronger matching record exists. No model inference is required.

## What was missing and what was recovered

Chrome at `http://127.0.0.1:4173/?front=radio` initially held 61 records. The historical source audio and SHA-256-addressed feature cache were still on disk, but the older audio records were missing from this browser library. Disk-side analysis alone does not create playable browser tracks. Browser storage is isolated by profile and exact origin; this investigation does not establish which previous profile/origin held the missing batch or why those browser entries disappeared.

All 37 files in `test_folder_37_tracks_diff_genres` matched their recorded source hashes and complete current cache records. This includes the ten baseline house tracks. Another 17 cached originals were found in `test_tracks_folder_mp3`: **54 unique recovered files**, all with complete cached analysis. Original files were read and left unchanged.

One file was restored using Add music, then the new recovery action restored the other 53. Final Chrome observations:

| Measure | Count |
| --- | ---: |
| Library records | 115 |
| Unique Analysis tracks | 109 |
| Duplicate analysis entries collapsed | 6 |
| Complete unique analyses | 83 |
| Partial unique analyses | 9 |
| Unique tracks without analysis | 17 |
| PlaylistIQ candidates with genre evidence | 88 |

Repeating recovery displayed **0 tracks restored · 54 already in your library**. These are observations for this Chrome profile at this address, not universal catalog counts. The 17 missing and nine partial analyses remain explicit; recovery does not invent missing features. See the [source/hash recovery inventory](LIBRARY_RECOVERY_2026-09-19.json).

## Workflow

1. Start the local player with its existing launcher or `npm run dev` in `packages/web-player`.
2. Open the same Chrome profile and address, `http://127.0.0.1:4173/`.
3. Select **Restore saved batch** in Library or Analysis. The service checks only the project's three established source folders (now inside `test_music/`): `test_folder_37_tracks_diff_genres`, `test_folder_10_house_tracks`, and `test_tracks_folder_mp3`.
4. Files must match a saved cache hash; the browser independently verifies downloaded bytes, skips hashes it already holds, imports audio and attaches the matching features. Failures are reported per file. A partially completed recovery can be retried.
5. For analyzed audio outside those folders, use **Add music** to select the originals. Matching saved features are attached after import. Keep the original audio and `packages/prompt-to-playlist/output/web-features` as separate recovery sources.
6. In PlaylistIQ, submit a request and select **Play** beside any match. Main transport, seeking and queue controls apply normally.

The browser still owns its audio copies, playlists and preferences. This feature recovers known audio and analysis; it does not reconstruct playlists or preferences from a deleted browser profile. It needs the local Node service, not standalone static hosting.

## Technical changes

- `src/model.js`: preserves validated `fileHash` in public local track objects; adds content identity, feature quality and stable representative selection. Previously `validateTrack` dropped the stored hash on load.
- `src/adapters.js`: backfills hashes for older browser entries, preserves IDs, and restores stronger cached features by exact audio identity.
- `src/app.js`: deduplicates Analysis and batch analysis selection, deduplicates PlaylistIQ candidates, connects result playback to the existing Player, restores cache after imports and exposes batch recovery.
- `src/playlistiq.js`: escaped per-match controls and `playPlaylistMatch`, mapping result IDs to playable library entries in rank order.
- `scripts/recovery.mjs` / `scripts/local-features.mjs`: fixed source-folder scan, hash/cache intersection and read-only local recovery endpoints. Client requests cannot choose filesystem paths; listings omit source paths, symlinks are excluded, and original audio is hash-checked again before serving. Requests require a local Host and custom marker; foreign explicit origins are rejected.
- `src/recovery.js`: sequential import, browser-side hash verification, exact-content duplicate skipping, analysis attachment, per-file error collection and repeatable recovery.
- App status JSON and generated Markdown describe the new behavior.

## Verification

- 57 web tests pass, including same-title/different-audio handling, stronger-analysis selection, partial-cache upgrades, hash mismatch rejection, ranked result playback and idempotent batch recovery.
- Syntax checks pass for 35 JavaScript modules.
- Production build and 24-file manifest verification pass; no source audio or private filesystem paths are bundled.
- 15 HTTP preview checks pass. Additional recovery checks confirm 54 unique entries, omitted filesystem paths, and rejection of unmarked/foreign-origin requests.
- Existing Chrome profile: recovered titles visible in Library and Analysis; 109 unique rows, including only one row for each formerly duplicated audio file. My Paradise displays saved House support 71.6%, tempo 130.4 BPM, Eb minor and semantic values.
- One authorized live PlaylistIQ request, “Give me 3 house tracks.”, produced three matching results with three Play controls. Selecting the second result, My Paradise - Edit, started the main player; elapsed time advanced to eight seconds. Playback was then paused. This checks integration, not human musical-quality acceptance.
- No new acoustic analysis, cloud work, audio changes, playlist deletion or model-policy change. No mobile acceptance run in this repair.
