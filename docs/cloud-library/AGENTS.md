# Agent takeover for cloud discovery

## 2026-10-02 — First launch simplified to one owner/shared catalog

The owner now requests one shared read-only music library for link visitors, keeping analysis local. A parallel local web preview is implemented at port 4174; current qualified catalog has 187 MP3s. Local preview and code push are authorized; actual cloud publication follows preview review. Multi-tenant accounts and visitor uploads are deferred. [Current implementation and simplified launch plan](../../packages/web-player/docs/WEB_EDITION.md) supersede the earlier first-release scope below.

**Product direction — D058 / CD019 (2026-09-12):** Resonant is now explicitly
the cohesive product shell around the independent player, PlaylistIQ and DJ
engine: native/manual and AI-assisted playlists, continuous in-app playback of
the ordered set and rights-aware whole-playlist file download, followed later
by deterministic mix generation. The download belongs in the playlist ellipsis
menu and includes only owned or otherwise download-authorized audio. It is
separate from JSON export and rendered mixes. This is accepted product/UX scope,
not provider integration, cloud implementation, upload or remote-audio authority.

**Current planning update — D057/CD018 (2026-09-12):** Read
[FAST_CLOUD_LAUNCH.md](FAST_CLOUD_LAUNCH.md) first. For the user’s lower-migration,
lower-manual-work priority, recommend R2 + Workers Static Assets/API + D1 +
Access for the current private1→3→10 audience. Provider acceptance/execution
remain pending; economics2.0 and empirical gates are unchanged. Older B2
recommendations below retain their original lowest-cash/readiness context.


**Readiness: 2026-09-12, revision 1.2 (D055).** Read
[READINESS_WORKPLAN.md](READINESS_WORKPLAN.md) first for this task's checkpoint,
then [OWNER_SPIKE_PACKET.md](OWNER_SPIKE_PACKET.md) and current registers.
The [runbook](SPIKE_RUNBOOK.md) and unsent [interview packet](INTERVIEW_PACKET.md)
complete the local preparation. No provider experiment execution is approved.

Proposed technical scope: one owner, two controlled test identities, B2 US
East, one Access-protected Worker origin, generated fixtures, 1 GB retained /
6 GB ingress / 10 GB egress, eight hours / seven days / $1 inside $5 monthly.
Q017 now has a precise 8 GB AND 500-track proposal, not an owner answer.

**D054 scoped supersession, 2026-09-12:** User now authorizes the local web
player build, ready for later deployment after services are selected. Read
[`../../packages/web-player/AGENTS.md`](../../packages/web-player/AGENTS.md)
and its staged PLAN/WORK_LOG to resume. Player 0.1.0 is complete: 30 tests, 12 production HTTP checks and generated-audio
browser acceptance pass (E042/T028/EX008). Deployment/device limits are documented. Existing statements below holding all implementation now exclude
this isolated local player. Cloud infrastructure, uploads, accounts, remote
audio processing and deployment remain held; cloud evidence gates stay open.

Read the repository's ../../AGENTS.md first. This file adds discovery instructions and cannot loosen its audio, rendering, model, credentials, source-preservation or commit boundaries.

## Authority and current state

The 2026-09-08 request activates full research and local planning/document maintenance. It does not authorize accounts, uploads, remote analysis/rendering, production hosting, automatic MixPlan generation, customer outreach, expenditure or cloud implementation of PlaylistIQ. D043 records this distinction. D046 separately resumes **local** PlaylistIQ evaluation; it does not expand cloud scope. Do useful research/document work without seeking repeated approval.

D045 adds the current affordability constraint: plan the cloud trial in three stages of 1, 3 and at most 10 users. Economics revision 2.0 assumes at most 8GB and 500 selected tracks per user, a $5/month service cap and no automatic paid upgrades. B2 plus Cloudflare Free is the lowest-cash candidate; R2 is the simpler fallback. T025 preparation is draft-ready; actual execution remains authorization-gated.

The local engine and PlaylistIQ evaluation are separate active local tracks. The accepted v2 mix has a +1.04 dBTP warning, and broad listening validation is unfinished. PlaylistIQ 0.3.0 now has a local no-All-In-One descriptor sidecar, completed on ten tracks (E037, 60/60 stages) and 37 tracks (E040, 222/222); it is not connected to the UI catalog and is not a cloud analyzer. Dedicated desktop/mobile apps are deferred. A browser prototype specified here is a design, not a deployed application.

## Minimal read sequence

1. STATUS.md for the recommendation and immediate next task; then UNIT_ECONOMICS.md for the 1/3/10-user cap.
2. registers.json for current gates, risks, questions and dependencies.
3. Relevant report and its source IDs.
4. MAINTENANCE.md before changing records.
5. ../../DECISION_LOG.md and ../../EXPERIMENT_LOG.md when a proposal touches prior engine choices.

Do not load the full audio library or run analysis to reconstruct metadata. No source audio is needed for research. Never print credentials, inspect shell secrets or send library metadata to a third party.

## Evidence rules

Research confidence values describe documentary support, not musical authority. Exact musical authority strings remain encoded_fact, standardized_measurement, deterministic_measurement, benchmark_estimate, user_verified, llm_proposal, executed_action.

Proposed thresholds are hypotheses. Passing a documentation review does not pass an empirical build gate. A source saying a feature exists does not establish latency, correctness or demand. A rejected route is a reasoned recommendation unless an actual attempted experiment is recorded. Do not fabricate interviews, invoices, measured timings or failures.

## Handoffs

Root owns shared registers/events/source IDs and parent logs. Delegate distinct
new documents or read-only audits under current task authority; preserve
concurrent engine, PlaylistIQ and local web-player work. Update the stage
checkpoint after every completion, failure or material steer. No cleanup
monitor or recurring automation is installed.

Update STATUS.md, registers.json, events.jsonl and CHANGELOG.md on material changes. Update the parent documentation set when scope, authorization or project status changes. Retain original event records and superseded conclusions. Record unresolved contradictions explicitly. Do not commit without a user request.
