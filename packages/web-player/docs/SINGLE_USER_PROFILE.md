# Single listener saves and playback polish — 2026-10-03

> Latest UI/discovery continuation: [WEB_DISCOVERY_REFINEMENT.md](WEB_DISCOVERY_REFINEMENT.md). Profile architecture below remains current; older layout details and counts are historical.

Implemented and available locally at http://127.0.0.1:4174/. **Not deployed.** The owner's local-review hold remains. This checkpoint supersedes the earlier frontend-only deployment handoff for this revision.

## What is saved

- Loved tracks and named playlists, including track order, additions/removals, rename and deletion.
- Each submitted PlaylistIQ prompt, timestamp, clarification answers, estimator choice, request status, elapsed time and resulting track IDs. A repeated submission has its own history entry. Reusing a saved prompt does not send a request until Find tracks is pressed; Play results reuses saved IDs without inference.
- Playback starts, observed listening seconds, qualified listens, completions and early skips per track. The originating PlaylistIQ request and saved playlist receive their own counters and distinct heard/qualified track sets.
- Listening habits shows top tracks/artists, listening-time-weighted mean BPM, tempo bands and top genres. Your prompts shows recommended/tried/listened counts for each request. History and stats can be downloaded together.

A listen is at least 30 seconds or half a shorter track. A completion requires reaching the end after hearing at least 80%. An early skip is changing tracks after some progress but before 30 seconds. Paused time and seek jumps do not count. URL renewal preserves the listening visit. Progress is not proof of audible speaker output on an interrupted device. The local browser acceptance session contributes test listening time; it is not uploaded to the cloud.

The per-track and per-request counters are aggregates, not a second-by-second event warehouse. Favorite status is saved explicitly; listening time does not claim that someone liked a song.

## Persistence and cost

Local preview uses `output/web-profile/account.json`, ignored by Git, atomically replaced with mode 600. Browser preferences are imported once. Operations first enter a browser outbox, then sync to the local service; reloads and server restarts retain acknowledged saves. Browser cache/outbox also preserves work through temporary server outages. Pending changes retry with bounded backoff and on return/online. Clearing browser storage before sync can still lose unsent changes.

Cloud preparation reuses the **existing DynamoDB on-demand table and API Lambda**. There is no new service, server or subscription. The new GET/POST `/api/profile` routes require the existing session, origin protection and POST CSRF. One owner partition is intentionally shared by all logins using the existing shared password. This is not multi-user isolation.

Transactions use revision conditions and durable operation IDs to merge edits and prevent retry double-counting. Idempotence markers and profile/history rows have no TTL. Reads paginate with Query instead of table Scan. Listening writes are batched around 30 seconds of progress and on pause/visibility changes; nothing runs periodically while idle solely to collect data. No audio, embeddings, API keys or full model-result payloads enter this profile.

AWS usage is still metered: API requests, Lambda work, DynamoDB reads/writes and stored bytes can add small variable charges. No claim of exactly zero incremental cost. DynamoDB on-demand charges for actual requests without provisioned idle capacity: [AWS on-demand documentation](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/on-demand-capacity-mode.html), [AWS pricing-model explanation](https://aws.amazon.com/blogs/database/demystifying-amazon-dynamodb-on-demand-capacity-mode/). No paid request or AWS mutation was performed for these changes.

The existing table has deletion protection and retention, but no newly enabled paid backup feature. Download my history & stats provides a manual portable copy. The local file is separate from cloud state; browser migration imports that browser's old likes/playlists and old prompt reviews, not the entire local server profile.

## UI changes

Expanded-player and queue openings use 560 ms transform animations with eased deceleration; dismissals use roughly 460–480 ms. Reduced-motion preferences skip those animations. The mobile visualization starts at 12.5dvh, is 33.333dvh tall and has 12px left/zero right inset. The mini spectrum begins at approximately 60% of viewport width. Native iOS audio remains outside Web Audio; its progress visualization is not an FFT.

Love/Add to playlist controls are in the expanded player and track options. Ordinary paused mini players have no pause quote. Shuffle displays text. Sort By is a themed floating list with matching 44px options. Queue emphasis uses warm italic title text and a slim marker. Audio features shows only the top five character labels. The house mix uses the same native media element/main player, with artist names, editorial 01/02/03 numbering and clickable transition times.

## Verification and handoff

- Web suite: 156 tests passed (including 13 new profile/listening tests). Initial restricted runs hit four loopback EPERM errors; rerunning with loopback permission passed. One test assumed ordering of simultaneous independent favorites; corrected to compare the unordered set.
- Cloud API/edge: 21 tests passed, including auth/CSRF, cross-session shared profile, transactional conflicts, permanent idempotence and invalid-member rejection.
- Infrastructure assertions: 4 passed. Existing route logical IDs are preserved; profile routes append; only Query permission is added on the existing table.
- Syntax: 79 JavaScript modules. Web build: 43 static files, no audio.
- Browser checks: 393×852 mobile, narrow 320px and desktop; Love/Add playlist, file persistence and reload, top-five features, themed sort, queue drag dismissal, mix playback/seeking/main-player continuity, listening stats and a synthetic PlaylistIQ history/save test. No paid inference in the synthetic check.
- Fixed a browser-discovered aliasing bug: synced preferences must be cloned before handing them to the mutable UI, or later playlist edits can disappear from the diff. A regression test now exercises that exact sequence.
- Physical iPhone touch, locked/background playback and background next-track advancement remain device acceptance. Desktop responsive emulation does not verify iOS.

After explicit owner approval, deploy the updated API bundle and regional routes/IAM, followed by the frontend using the existing serverless workflow. The exporter now packages `profile.mjs` and its shared `profile-model.js`. Regenerate a new candidate with the **actual current state bucket**; the local `output/web-refresh/profile-candidate-20261003*` outputs use `resonant-local-validation` solely to validate packaging and **must not be uploaded**. Retain the frozen media/model release. No worker rebuild, analysis, audio replacement or extra service is needed.

Smoke-test cloud login, Love/playlist save then fresh-session read, prompt history, API-outage pending retry and ranges. Preserve profile rows during rollback; old frontend/API can leave that data unused. Keep the staged server-side password rotation and physical-device checklist from [the web refresh checkpoint](WEB_REFRESH_2026-10-03.md).

Evidence receipt: `output/web-refresh/profile-verification.json`. Screenshots: `profile-mobile-player.jpg` and `profile-mobile-library.jpg` in that directory. The 393px mini spectrum spans x=232.8 to x=320px; the visualization is y=106.5px / h=284px in an 852px viewport. The 320px Sort By trigger and options measured equal width (165.5px). Temporary synthetic browser fixtures were removed before the final build; the test-only playlist was deleted and its Love change restored.
