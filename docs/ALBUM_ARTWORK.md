# Album artwork — implementation and deployment

2026-10-17. Stage 5 local processing and the existing shared-library artwork
are implemented. **Shared-library covers and compact UI are live on resonant.lat.**
Personal cloud uploads remain unimplemented; their stored-object lifecycle was
not fabricated. No changes to source audio, acoustic analysis, PlaylistIQ
ranking, DJ transitions, tempo/beat logic or progressive mix playback.

## Completed behavior

- Embedded front artwork first: MP3/ID3, MP4/M4A `covr`, FLAC pictures,
  Ogg picture blocks and WAV/AIFF ID3 through Mutagen. New local import formats
  remain the existing MP3/M4A policy; this task does not expand it.
- The existing M4A conversion deliberately discards attached images. The import
  transaction now retains the original selected M4A in a separate browser
  `audio` entry, `artwork-source:<track-id>`, solely for artwork extraction and
  recovery. The converted playback file, conversion parameters and analysis
  identity are unchanged. Replacing/removing the track replaces/removes this
  auxiliary original too. This can use additional browser storage.
- After the browser audio/track transaction completes, a deferred notification
  queues artwork. It does not await extraction, network lookup or image writes.
  The loopback companion streams a temporary source copy to disk, hashes it,
  durably enqueues it and returns 202. Its separate worker extracts tags and
  covers without decoding PCM or running analysis. Temporary input copies are
  removed after extraction; original library sources are only opened for read.
- A SQLite sidecar contains durable per-track/version work and album records.
  Albums are scoped by trusted caller scope plus Unicode NFC/casefold/whitespace
  normalized album artist (artist fallback) and album. Unknown/compilation
  metadata is source-specific and never sent to an album search.
- All pending files are checked for embedded covers before network fallback.
  A sibling with the same album identity reuses the cover. Conflicting embedded
  covers keep their own track art but leave an artwork-free sibling ambiguous.
  Internet matches are resolved once per album, not once per track.
- Cover and thumbnail are aspect-preserving JPEGs, bounded to 500 and 96 pixels
  on the longest edge, without enlargement or cropping. Content hashes dedupe
  image files. Decode bounds: 12 MiB encoded image and 24 million pixels.
  Oversized/corrupt embedded art can fall through to conservative metadata lookup.
- Missing/ambiguous matches cache for 30 days; successful records persist.
  Transient failures have separate retry state and never become permanent
  “not found.” A process lock serializes workers; the shared persistent request
  clock spaces requests by at least 1.1 seconds. HTTP 429/503 respect
  `Retry-After`, including HTTP dates. A failure backs off from 120 seconds to
  at most one day (or a longer provider deadline), with a six-attempt budget and explicit reset command.
  Provider cooldowns do not busy-wait a worker for long periods.
- Provenance persists source/provider, source audio hash for embedded covers,
  matched artist/album, MusicBrainz group, CAA release/listing/image URL and ID,
  timestamp, match rule, qualitative confidence and image hashes/dimensions.
  `encoded` means embedded evidence; `high` is a unique exact metadata match,
  **not a calibrated probability** or a claim to identify the exact pressing.
- UI uses 52-pixel thumbnails in the library, queue, normal saved playlists,
  fresh PlaylistIQ results and saved prompt results; 40 pixels beside the
  minimized track name. Titles and artists stay on one line with ellipses.
  Titles use 18px desktop / 16px mobile; each cover exceeds the two-line text height. Both spectrograms and their code remain intact. Expanded
  mobile player hides the artwork thumbnail. No large cover was introduced.
  A failed image request reveals the same compact placeholder. Images are lazy
  and same-origin; no third-party image requests originate from the browser.

## Provider decision and requirements, checked 2026-10-17

**MusicBrainz + Cover Art Archive only.** Public read APIs need no API key or
OAuth. MusicBrainz requires a meaningful User-Agent and at most one request per
second. Default `ResonantArtwork/1.0 (+https://resonant.lat)` can be overridden
with `RESONANT_ARTWORK_USER_AGENT` for an operator contact. Before commercial
service activation, review MusicBrainz's applicable service-access terms.
[API](https://musicbrainz.org/doc/MusicBrainz_API),
[rate limits and User-Agent](https://musicbrainz.org/doc/MusicBrainz_API/Rate_Limiting).

The adapter searches release groups using artist and album, accepts exactly one
group with equal normalized full artist credit and full album title, and rejects
truncated result sets and multiple exact groups. It does not strip edition
suffixes, accents, punctuation or artist collaborators to manufacture a match.
CAA must then have exactly one approved front with its supported 500-pixel URL.
The response goes through CAA before its documented Internet Archive redirect.
Redirects are HTTPS and host-allowlisted; arbitrary URLs and ports are rejected.
No scraping, title-based guesses or alternative-provider searches occur.
[Search contract](https://musicbrainz.org/doc/MusicBrainz_API/Search),
[CAA API](https://musicbrainz.org/doc/Cover_Art_Archive/API).

Core MusicBrainz metadata is CC0; cover images are separate and retain their
owners' copyrights. CAA access is not a copyright license for the images.
The track-details artwork line links back to MusicBrainz/CAA; thumbnails name
their provider in a tooltip; stored provenance preserves the underlying release
and image attribution. No supplementary MusicBrainz ratings/tags are used.
[Data license](https://musicbrainz.org/doc/About/Data_License),
[copyright information](https://musicbrainz.org/doc/Copyright_and_DMCA_Compliance).

Last.fm's `album.getInfo` requires an API key, and its API terms section 5.1.8
expressly excludes image/artwork use from the agreement. Its data also requires
credit/backlinks. It therefore does not justify a fallback implementation here.
No Last.fm credentials or other paid provider credentials are required.
[album.getInfo](https://www.last.fm/api/show/album.getInfo),
[API terms](https://www.last.fm/api/tos).

## Run, backfill and resume

From the project root:

```sh
.venv/bin/python -m venv tools/artwork/.venv
tools/artwork/.venv/bin/pip install -r tools/artwork/requirements.txt

# Use an existing catalog/source map; do not regenerate acoustic features.
tools/artwork/.venv/bin/python tools/artwork/cli.py backfill \
  --catalog output/web-release/catalog.json \
  --sources output/web-release/sources.json
tools/artwork/.venv/bin/python tools/artwork/cli.py work

# Repeat work after interruption; cached albums and completed extraction survive.
# Optional bounded online pass, or embedded-only pass:
tools/artwork/.venv/bin/python tools/artwork/cli.py work --limit 2
tools/artwork/.venv/bin/python tools/artwork/cli.py work --offline
tools/artwork/.venv/bin/python tools/artwork/cli.py manifest --scope default

# After resolving a persistent provider outage, reset exhausted attempts only:
tools/artwork/.venv/bin/python tools/artwork/cli.py retry-unavailable
tools/artwork/.venv/bin/python tools/artwork/cli.py work

cd packages/web-player
node scripts/serve.mjs --web --port 4177
```

Default cache: ignored `output/artwork/`; optional global `--cache PATH` must
precede the subcommand. Never use a source-audio directory as the cache. Backfill
reads only explicitly mapped files, verifies their existing SHA-256 identities
and leaves the catalog/features untouched. Changing identity/metadata should
publish a new `source_version`. Source mismatch is a failed job, never a cover
guess. Correct the stored event/version to retry a failed source.

Browser-local imports use scope `local-<port>`; web preview uses `default`.
The local app resumes missing stored-track notifications on startup and every
30 seconds; the companion wakes the durable worker every 30 seconds. Pending
provider work resumes when its persisted deadline is reached. Closing a tab
does not erase queued work. Restart the companion to resume after server exit.

## Integration surface and remaining dependencies

`Store.enqueue_stored(scope, track_id, source_version, source_hash, source_path,
metadata)` is the trusted **stored-object hook**. It only persists a job; it
does not perform provider work. Scope/path/version must come from verified
storage and authorization, not a browser's claim. For a cloud original this
means a verified object version/hash and an authorized local worker copy.

The existing cloud API has playback/accounts/mixes, but no personal upload-intent
or verified upload-completion route. Remaining work belongs to Stage 3/cloud
integration: verified completion → durable dispatch; owner-derived scope;
worker image/dependencies; private derivative storage and authorized image/
manifest delivery; lifecycle deletion/retention and quotas; catalog capability
publication and end-to-end ownership/retry tests for personal uploads. These
personal-upload dependencies are not deployed or verified.
The loopback `/api/artwork/*` routes are **not cloud authentication** and must
not be published as-is. Hosted serverless configuration enables only a validated
immutable manifest and image namespace under signed `/library/artwork/`. The
local intake client stays disabled. This release publishes a frozen default-library
snapshot; it does not run cloud provider jobs or automatically publish local retries.

Shared-file edits are limited to:

- `src/adapters.js`: auxiliary original storage, post-commit notification,
  auxiliary-source cleanup on replacement/removal.
- `src/app.js`: thumbnail slots, provenance line, original-file reference passed
  through import/duplicate review, and artwork client startup.
- `src/web-presentation.js`, `src/profile-views.js`, `src/playlistiq.js`: compact
  result slots; no ranking or ordering logic changes.
- `public/index.html`: separate artwork stylesheet.
- `scripts/serve.mjs`: local companion mount/shutdown.
- `tests/duplicates.test.mjs`: IndexedDB test double supports the new cleanup.

New independent modules: `tools/artwork/{artwork.py,cli.py,requirements.txt,
test_artwork.py,preview-components.mjs}`, `src/artwork.{js,css}`,
`scripts/artwork-service.mjs`, `tests/artwork*.test.mjs`. No dependency changes
to audio/ML environments or the web package; artwork has an isolated Python env.

## Validation checkpoint

See `output/artwork-verification/` for local screenshots and the final receipt.
21 Python tests cover extraction/source preservation, album reuse, conflicting
embedded covers, exact/ambiguous/truncated searches, missing metadata, cached
negatives across restart, version replacement, corruption, worker locks,
rate-limit retry deadlines, retry exhaustion and unsafe URLs. Four UI-unit
tests cover slots/escaping/version binding; the real HTTP test covers 202,
embedded generation, image serving, origin checks and replacement. Full player
suite passes all 192 tests, including the HTTP test; final checks are recorded below.

Browser inspection: actual library thumbnails at desktop 1280 and mobile
390/320; minimized thumbnail + mini spectrogram + controls fit with no document
overflow; expanded main spectrum stays present and artwork hidden. Fresh/saved
result layout is checked using the disposable `preview-components.mjs` harness,
which uses actual library artwork but labelled fixture results and no model
request or profile write. Physical iPhone acceptance remains unverified.

Initial backfill: 187 source hashes verified; 156 tracks use embedded covers.
Live provider requests initially returned HTTP 503 and recovered via persisted
backoff; subsequent real MusicBrainz/CAA image downloads succeeded. Ambiguous,
missing and still-retrying records remain placeholders. Final coverage is in
the receipt; it is not a promise that every album can be identified.

### Final local receipt — 2026-10-17

- Existing-library snapshot: **165/187 ready** (156 embedded; 9 MusicBrainz/CAA),
  20 missing/insufficient-metadata placeholders and 2 provider retries. There are
  74 scoped album records: 57 embedded, 4 CAA (including two without usable
  covers), 11 negative and 2 retry records. This is a dated snapshot; the local
  companion can subsequently advance retries.
- Source SHA-256 after processing: **187/187 exact** against the existing catalog;
  no source mismatch. Pre-existing tracked diffs outside the documented artwork
  edits compared byte-for-byte equal to the pre-task patch snapshot.
- **21 Python artwork tests; 192 player tests; 6 board tests** pass. Final narrow
  UI/import regression also passed after adding client single-flight protection.
- **103 JavaScript modules** pass syntax checks. Local and web builds contain
  61 and 59 static assets; every manifest SHA-256 independently verified and no
  source audio included. The older `scripts/verify-build.mjs` still rejects
  pre-existing `src/vendor/hls.LICENSE` by extension; left unchanged because this
  is unrelated to artwork/progressive mix ownership. This legacy check is not
  reported as passing.
- Actual app: 1280px desktop and 390/320px web mobile layouts, including compact
  cover + miniature spectrum + playback control, without document overflow.
  Expanded 320px view retains its live main spectrum with no artwork display.
  Fresh and saved result components rendered six real covers in a labelled
  390px fixture with no model request. Fixture scores are not matching evidence.
- Generated MP3 and M4A were imported via the UI on isolated port 4178 (including
  Keep both duplicate review). Both post-storage jobs completed from embedded
  covers; provenance hashes match each original fixture, dimensions are 500/96,
  and both displayed images survive page reload. No acoustic analysis ran.
- Main preview remains **http://127.0.0.1:4177/**, paused. Temporary import and
  component servers were stopped; pre-existing ports/servers were preserved.
- Physical iPhone, production cloud delivery, personal upload authorization and
  uploaded-object event wiring remain unverified. Nothing was deployed or committed.

## Owner layout refinement and Git scope — 2026-10-17

The owner added queue covers and requested Spotify-like cover/text proportions
before committing and pushing. Library/result/queue titles now use one-line
ellipses and smaller type; artists also ellipsize. Covers are 52px in rows and
40px in the minimized player. Verified at 1280, 390 and 320px: no document
overflow, queue text block 43px desktop / 40px mobile, library text block below
52px, minimized text 33px with its 40px cover and existing 58px-wide spectrum.
Expanded player retains its spectrogram and hides artwork. The 19 relevant
UI/import tests, 103-module syntax check and both builds pass.

The Git commit isolates artwork edits from substantial pre-existing uncommitted
work. The broader readiness document and project-board system are themselves
untracked prior work; their local artwork updates remain preserved locally
rather than adding unrelated plans or the entire board to this commit. This
checkpoint carries the committed artwork plan, completed work and dependencies.
No deployment is included in the requested commit/push.

The isolated staged commit also passes **178 player tests**, **97 JavaScript
module syntax checks**, and local/web builds (56/54 assets). Those counts exclude
the separate uncommitted transition work present in the main working preview.

## Shared-library deployment — 2026-10-17

The owner subsequently authorized deployment. This supersedes the earlier local-only
receipts above. Built from the verified October 13 live app, applying only the
reviewed artwork overlay. All 56 previous app files matched their live S3 bytes.
The later local transition, tempo and progressive-mix work was not published.

- Live app: `b33e6123d52b049e19015827d90fae834cd77dcd70dd4589a102b5e58e69c833`.
- Previous app/rollback: `9b2f72178c4f9994ccf6bc8f28b27e6ae3cee2ef8a5bcd6286e4d3eaf1917dd0`.
- Artwork manifest: `f67960ecc3b6362f92c1e57d11fdbd6d5b07ae04faaa88ed30c565409a88205a`.
- Music/model release stays `4a4bb92196ed75cc95ac19ec6a25bd5062ed31cdabb0eb30ebca0f83d5b5ff57`.
- API/PlaylistIQ aliases **11/11**, mix **5**, unchanged. No backend or edge-policy deployment.
- 165/187 tracks ready: 156 embedded and 9 CAA. The other 22 remain placeholders.
  118 deduplicated image objects, 58 app assets and one manifest: 177 immutable
  objects verified by SHA-256, plus two conditional entry-point writes; 5,148,113 bytes.
- Private `/library/*` signed-cookie protection covers manifests/images. Both
  embedded and CAA 500/96 derivatives match locally exported bytes; unsigned
  access fails with 403. No new credential required and no cloud intake endpoint.
- Live smoke verified 13 exact app assets, unchanged catalog and exact 1024-byte
  MP3 range, plus unsigned-audio denial. Actual authenticated browser playback
  progressed; compact library thumbnails loaded. Main and mini spectrograms retained.
- 26 Python tests (21 processing + 5 export), 35 relevant player tests against
  the exact deployed candidate, and 47 deployed JavaScript syntax checks passed.
  Browser viewports 1280/390/320 checked; physical iPhone acceptance remains pending.

New deployment integration is confined to `src/artwork.js` (validated private
manifest/images, no hosted enqueue), `src/adapters.js` (validated config),
`src/app.js` (hosted artwork startup), the artwork test, and
`tools/artwork/export-hosted.py` with five export tests. The exporter verifies
source identities and hashes, requires the entire reviewed app overlay, and
emits a `publishKeys` allowlist that excludes source media, catalog pages and
acoustic analysis. Existing base inventory is retained only for later tooling.
Do not pass the complete inventory to a generic uploader.

Reproduction uses the frozen verified live candidate and reviewed overlay, not
the mixed working tree:

```sh
tools/artwork/.venv/bin/python tools/artwork/export-hosted.py \
  --base output/mix-refinement-20261013/candidate \
  --app-source output/artwork-deploy-20261017/app-overlay \
  --cache output/artwork --output output/artwork-deploy-20261017/new-candidate
```

Private receipts and screenshots: `output/artwork-deploy-20261017/`.
`release/` is the published candidate; earlier draft directories are not releases.
`before/` and `rollback-deployment.json` retain the prior entry bytes/tuple,
`published-pointers.json` the new S3 versions, and `deployed.json` the final tuple.
CloudFront invalidation completed. A local receipt serialization error occurred
after both pointers succeeded; recovery verified their versions/checksums and
reused the same invalidation caller reference without rewriting either pointer.
`output/serverless-cloud/active-deployment.json` now records this release.

Remaining: implement the actual personal-upload lifecycle, then wire verified
stored-object dispatch, owner-derived scope, private per-owner derivatives,
retention/quotas and end-to-end isolation/retry checks. Future local backfills
require another reviewed snapshot publication to update the hosted library.
