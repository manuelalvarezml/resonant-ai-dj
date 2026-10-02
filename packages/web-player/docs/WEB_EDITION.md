# Shared-library web edition — 2026-10-02

## Decision and scope

Keep local and web editions in the existing private `manuelalvarezml/resonant-ai-dj` repository. One shared player source avoids duplicated fixes and divergent ranking. Separate runtime configuration, catalogs, ports and build outputs keep owner tools out of the visitor edition.

The owner maintains one shared music collection. Visitors load that same collection; there are no separate user uploads, tenants or per-user analysis jobs in this release. Playlists and favorites are personal browser preferences, not shared edits to the owner's library. Cloud publication follows local preview acceptance; no provider resources or audio upload to a cloud service have been executed by this task.

## What is implemented

- Local player: `http://127.0.0.1:4173`; layouts 1 and 3. Old `?front=radio` links now select layout 3. Option 2 is removed from controls in both editions; its shared CSS foundation remains necessary for layout 3.
- Web preview: `http://127.0.0.1:4174`; layout 3 only. No Add music, Restore saved batch, Analyze Tracks, conversion, specialist-upgrade or delete-track controls. Owner analysis/conversion/recovery/render endpoints return 404 in this server mode.
- Analysis remains a read-only features view. App Status is replaced by brief white cards with black text: Inside Resonant, How to use, What works today, What's next.
- One fixed, already rendered DJ mix. The retained v3 artifact uses the v2 three-track plan, duration 609.1 seconds. The two transition intervals are **203.65–232.74 s (3:23–3:52)** and **407.29–436.38 s (6:47–7:16)**. Start times come from the retained FFmpeg graph; the plan's 29.09-second overlaps provide their ends. No duplicate renders or render controls in the web edition; originals remain on disk.
- Shared catalog and HTTP playback use stable hash IDs and range requests. The existing Python planner receives only tracks admitted to the published catalog; client-supplied metadata is replaced with the server's canonical values. MuQ text inference and LLM planning still run when a playlist is requested; audio analysis never runs in this web mode.
- Visitors' favorites/playlists persist in browser localStorage under the HTTP edition's own origin, independent of the owner app.

## Catalog admission and actual count

Admission requires `selected-estimators-v3-character120`, complete overall status, all eleven required stages passed/warning, MP3 codec in ffprobe evidence, matching source hash and an MP3 source file. Warning means an estimator's normal limitations, not a failed stage. Partial and older completed records do not qualify.

Audit found 193 current complete records, but only **187 fully analyzed MP3s** qualified and were located: 179 on disk plus eight exact browser-only converted copies. The release does not manufacture a 200+ count by including partial analysis. A future successful local retry can increase it.

Owner preparation: start local server, open `/prepare-web.html` on **127.0.0.1:4173 in the Chrome profile containing the library**, and select Prepare web library. Existing source hashes are reused; browser-only eligible bytes are checked against the server cache and copied to ignored `output/web-release/audio`. This is a local copy, not cloud upload or reanalysis. Local originals remain unchanged.

At web-server startup, the catalog builder scans test_music plus those staged copies, deduplicates hashes, checks admission, and writes ignored `catalog.json` and private `sources.json` under `output/web-release`. The latter contains local paths and must never be published. Public feature responses omit audio embeddings, process metrics and local paths; full cache records stay available to the planner server.

## Run and build

From `packages/web-player`:

```
npm run dev          # owner edition, 4173
npm run dev:web      # parallel web edition, 4174
npm test
npm run check
npm run build
npm run build:web    # separate dist-web; no audio bundled
```

`node scripts/serve.mjs --web --dist --port 4174` previews the built web assets. The service rebuilds its catalog at startup. Git checkout alone does not include the private audio, model weights, feature caches, Python environment, retained rendered mix or provider credentials: these are deployment inputs maintained separately. No frontend build should contain API credentials.

## Verification and limitations

95 Node tests pass, including strict admission, retired-layout migration, public-feature redaction and cloud-track feature preservation. Syntax/build checks pass. HTTP checks verify 187 tracks across two pages, MP3 byte-range response 206, six blocked local/status routes, and one mix with two transitions. Chrome verifies 187 tracks, correct controls/layout, guide cards and timestamps. A live birthday-house request returned three ranked matches; the first played through the main player.

The first browser check exposed an existing unbound-native-fetch problem in the previously unused HTTP adapter. Wrapping the default fetch call fixed catalog loading; the local IndexedDB adapter is unchanged by that repair.

This remains a loopback preview. It is not safe to expose this development server directly to the Internet: HTTPS deployment origin handling, abuse limits, scoped planner job access, durable prompt jobs and production process supervision are still launch work. The preview reuses the local Python environment and cache locations. No claim of cloud readiness is made from passing local checks.

## Simplified cloud launch plan

1. **Accept the preview and freeze the catalog.** Confirm the 187-track selection, playback, phone layout, mix and PlaylistIQ behavior. Export the exact selected MP3 bytes, full versioned feature records and embeddings as one hashed release. Omit private source paths and failed records. Keep a manifest and rollback copy.
2. **Host one shared read-only library.** Use the previously proposed private R2 object store for audio and large analysis artifacts. Static assets and the small catalog can be served behind one HTTPS app origin. D1/multi-tenant accounts are unnecessary for this first immutable shared collection; add a database only when server-synced editing is required.
3. **Host prompt planning separately from audio analysis.** Deploy a Node/Python container or VM for the current planner and MuQ text encoder, with provider keys only on the server and the frozen catalog/embeddings mounted read-only. Benchmark its RAM and latency before choosing the compute tier. Do not move all eleven audio estimators into the web service. Persist jobs, restrict their access, bound concurrency and rate-limit/cap LLM calls so a shared link cannot create unbounded spending.
4. **Publish and verify.** Owner-only import/deploy tools verify hashes and publish an immutable release. Visitors holding the shared app link get the same catalog, without upload or administrative access. Verify HTTPS, audio ranges/seeking, mobile playback, request failures, restore/rollback, secrets and actual monthly budget before sending the link. Provider setup, cloud transfers and paid compute remain the next deployment stage, after preview review; the earlier $5 planning cap has not been silently increased.

This scope supersedes the old 1→3→10 multi-tenant launch for this first shared demo, while preserving that design as future history. Repository push is code publication to the existing private repo, not a deployment of music.
