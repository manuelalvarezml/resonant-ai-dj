# R2 — reference-led gray player and low-migration cloud plan

User steer: 2026-09-12. Apply sustainit.space typography/proportions/spacing/vibe
to a dark-gray brutalist player. Prepare the fastest practical cloud path with
little recurring manual work and minimal platform/connection migrations.
This authorizes local design and planning, not provider setup or deployment.

Product-scope addendum D058: preserve the redesigned player's existing playlist
creation and continuous queue playback as the front end of a broader DJ music
workspace. Future whole-playlist audio download belongs in the playlist
ellipsis menu, with rights/availability and size preflight; it is not part of
the verified0.1.1 build, the current JSON export or continuous-mix rendering.

| Stage | Exit | Current state |
|---|---|---|
| A. Reference and scope | Inspect actual site fonts/layout; preserve player behavior | Complete: Geist Mono 200–400 / Martian Mono 200 stylesheet observed; compact mono labels, large light headings, generous whitespace |
| B. Player redesign | Gray design tokens, locally served licensed type, responsive composition | Complete; responsive acceptance under stage D |
| C. Cloud launch plan | Chosen recommendation, ordered build/setup, stable connections, growth and cost tradeoffs | Complete; FAST_CLOUD_LAUNCH.md |
| D. Verification/handoff | Existing tests, desktop/mobile playback/layout, artifact/doc/checkpoints | Complete; E045/EX009, 30 tests,15HTTP checks,1280/390/320 |

Visual translation: light Geist Mono headings around 48–56px versus 12.8–14px
working controls, 10.4–12px secondary labels; preserve the reference's hierarchy
without reproducing its very small 8–10px text. Move the current vertical nav
into a compact masthead, use a generous main listening area beside the queue,
flat concrete grays, off-white type, square edges and thin structural rules.
No copied site graphics, brand text or source music. All controls remain usable.

Cloud direction to verify: one Cloudflare application with Workers Static Assets,
Worker API, D1, private R2 and invite authentication; stable bindings and automated
deployments. Compare durable auth/database choices against foreseeable needs
before settling the recommendation. Prefer fewer provider migrations over
saving a small storage price difference. Existing $5/month frame still applies
until owner changes it; current user accepts setup effort, not unbounded spend.

Resume: read this plan, package AGENTS/WORK_LOG and cloud current records; finish
the pending stage. Record actual failures/tests, do not repeat corpus analysis.

Checkpoint: A–D complete (D057/E045). Current0.1.1 artifact13files/227407bytes;
manifest22e618b77c25de82b5fe0f3011e29fd702ff1c76662db7bcde4085f4debedaa7.
The final design removes the redundant demo hero/action strip entirely so
tracks fit above the desktop transport; metadata still labels generated audio.
Resume only for new changes or approved service work. Cloud recommendation
is [FAST_CLOUD_LAUNCH.md](../../../docs/cloud-library/FAST_CLOUD_LAUNCH.md);
provider/budget/execution acceptance and a revised R2 trial packet come next.
No new analysis or migration is required to continue this local frontend.
