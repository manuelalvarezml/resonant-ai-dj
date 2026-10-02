# Cloud discovery status

## 2026-10-02 — First launch simplified to one owner/shared catalog

The owner now requests one shared read-only music library for link visitors, keeping analysis local. A parallel local web preview is implemented at port 4174; current qualified catalog has 187 MP3s. Local preview and code push are authorized; actual cloud publication follows preview review. Multi-tenant accounts and visitor uploads are deferred. [Current implementation and simplified launch plan](../../packages/web-player/docs/WEB_EDITION.md) supersede the earlier first-release scope below.

**Product direction revision 1.4 — D058/CD019:** Resonant is now planned as a
unified DJ music workspace. Users build/edit playlists inside the app, listen
to a whole set playlist continuously across owned and supported connected
sources, and may download an ordered package of eligible audio from the
playlist's ellipsis menu. This reduces source-app switching, but remains a
demand/UX hypothesis. Provider playback and download permissions must be
modeled separately; implementation and all empirical gates remain unpassed.

| Field | Current value |
|---|---|
| Revision | 1.4 — unified playlist/listening/download direction |
| As of | 2026-09-12 |
| Authorized work | Public-source research/local planning; D054 independent local web player now implemented |
| Research recommendation | Continue discovery; full cloud build is no-go at present |
| Proposed audience | DJs with owned local files; secondary personal collectors |
| Geography | Undecided; Peru, U.S. and EU are screening branches, not a launch selection |
| Storage shortlist | R2-first for stable connections; B2 retained lowest-cash alternative |
| Provider decision | R2 recommended under D057/CD018; owner acceptance and execution still pending |
| Proposed first value | One place to build/edit and continuously audition a selected DJ crate; owned-track upload, trustworthy metadata and private playback underneath |
| Mix launch | Gated separately on quality, licensing, portability and explicit authorization |
| Playlist implementation | Local player builds/reorders playlists and exports JSON; PlaylistIQ local evaluation is active; cloud account sync, cross-source playback and audio archives are unimplemented |
| Browser player | 0.1.1 gray redesign locally verified, D057/E045/T029/EX009; cloud services remain deferred |
| Dedicated apps | Deferred |
| Empirical cloud evidence | None |
| Customer interviews / paid demand evidence | None |
| Next authorized step | Product documentation is current; after provider/scope acceptance, revise the R2 trial packet. T030 implementation remains unauthorized |
| Next proposed experiment | Generated-fixture owner-only subset of EX003/EX004/EX007; EX001 first-wave drafts separately ready and unsent |
| Technical spike | EX003–EX006 specified; not run and not authorized |

## Most consequential findings

D057/CD018 changes the current planning priority to fewer migrations and stable
connections. [FAST_CLOUD_LAUNCH.md](FAST_CLOUD_LAUNCH.md) recommends R2/Workers/
D1/Access for private1→3→10; defines automated deployments/imports and conditions
for consumer auth/Postgres up front. This is a recommendation, not provider
selection or execution. Older B2 readiness below is preserved history.


D055's packet proposes B2 US East and one Access-protected Worker origin,
exact-version verification with a trusted local fixture operator, 60-second
bearer URLs, all-version cleanup and independent budget controls. Envelope:
1 GB retained, 6 GB ingress, 10 GB egress, eight active hours/seven days/$1
inside $5/month. Q017 remains open with a precise future cap of 8 GB AND
500 tracks. See [owner packet](OWNER_SPIKE_PACKET.md),
[runbook](SPIKE_RUNBOOK.md), [interview packet](INTERVIEW_PACKET.md),
[source review](SOURCE_REVIEW_2026-09-12.md) and [checkpoint](READINESS_WORKPLAN.md).

B2 currently advertises $6.95/TB-month, superseding old $6 guidance. R2 charges more for stored capacity but has no direct egress fee. Neither is a winner before worker-transfer and playback paths are measured. Wasabi's recurring egress policy and early-deletion economics make it a poor default for this proposed active library.

The lean cost revision now models 1, 3 and 10 users at 8GB/500 tracks each. B2 plus Cloudflare Free estimates $0.00, $0.10 and $0.50/month; R2 plus the same control plane estimates $0.00, $0.23 and $1.08/month. These are planning calculations before tax and founder time. A $5/month cap, explicit free-tier headroom and no automatic paid upgrade are now part of the trial specification.

Existing personal lockers and DJ library products establish substantial substitutes, not proof of demand for this service. The likely differentiator is trustworthy crate preparation and repeatable downloadable mixes, which still requires actual listening and workflow evidence.

D058 adds a second, more immediate differentiation hypothesis: one in-app loop
for assembling, continuously auditioning and revising the actual ordered set
playlist. Test context-switching reduction separately from AI novelty. The
secondary whole-playlist file download is for owned/download-authorized tracks;
it does not turn Spotify, SoundCloud or other provider playback into exportable
audio.

The existing MLX analysis path is platform-specific. Essentia and transitive software/model terms need review before a commercial service. Unknown semantic descriptors and final-bus headroom are existing product constraints.

## What happened in this revision

Revision 1.4 adds the unified playlist/listening/download direction and its
rights-aware UX placement. It changes no implementation or gate status.

Revision 1.3 adds the R2-first stable-connection launch recommendation.

Revision 1.2 completes readiness documents, corrects stale PlaylistIQ scope,
records source-path failures and independent protocol-review fixes, and adds
offline checks. All empirical gates remain unpassed and all seven experiments
unrun. Economics revision 2.0 and its workbook are unchanged.


Revision 1.1 corrects the cost view that made a one-time 100-user processing scenario look relevant to the first trial. It adds the 1/3/10-user workbook, free-tier sources, cheapest-stack plan, founder-time budget, F006, R021–R022, P018–P020, CD013 and T025–T026. No cloud or audio experiments were performed. See VERIFICATION.md for actual document/workbook checks.

The next agent should read open questions and continue research that does not require those answers. Do not reinterpret this completed research package as an approved implementation plan.
