# Discovery and conditional delivery plan

## Decision structure

Research revision 1.0 is complete as a desk-research package. Discovery as a product-validation phase is not complete. The current decision is continue discovery and no full cloud build.

Maintain three distinct authorization points:
1. Desk research and local planning artifacts: authorized by D043.
2. A capped experiment using specified non-sensitive fixtures or consenting participants: not yet authorized.
3. Production-capable implementation and external beta: not yet authorized.

A spike can gather evidence for unpassed gates. It requires a separate bounded authorization, not a claim that all full-build gates already passed. No account, resource, upload, remote analysis, automatic plan generator or customer message is authorized by a task row in this document.

## Gate applicability

All gate definitions/statuses live in registers.json. G001–G004, G007–G010 govern a private library launch. G005 applies when analysis is included, and G006 applies when mixes are included. For a metadata-only/playback pilot, a formal scoped decision may mark analysis/mix-specific requirements not applicable for that release while preserving their unpassed status for the full product.

The current dependency graph represents the full product, including analysis and mixes. A narrower approved release needs its own explicit gate-applicability record and revised task dependencies. Do not silently skip a failed gate.

## Ordered discovery work

| Step / task | Concrete output | Completion evidence | Current state |
|---|---|---|---|
| T001–T002 | Provider comparison and source inventory | Sources, units, gaps and experiment plan | Research complete |
| T003 | Segments, MVP and interview/onboarding protocol | Falsifiable questions, sample/denominator plan | Draft complete; no demand evidence |
| T004 | Entity, geography, audience and budget | Owner steer with exact scope | Open |
| T005 | Rights and software/model review | Written allowed-use matrix and unresolved exceptions | Packet ready; not cleared |
| T006 | Architecture/data/API/job draft | Boundaries, state machines and race invariants | Draft complete |
| T007 | Unit economics | Editable formulas, sensitivity inputs, verification | Scenario complete; unmeasured inputs |
| T008 | Interviews | Consented anonymized notes and contrary evidence | Not run |
| T009 | Spike authorization brief | Provider/region, fixtures, bytes, money/time cap, cleanup plan | Not authorized |
| T010–T011 | Upload/playback/private access spike | Raw timings, checksums, browser versions and request/byte costs | Not run |
| T012 | Commercial-license/target-runtime analysis | Exact artifacts, runtime/quality/cost comparisons | Not run |
| T013–T014 | Local quality and cloud reproducibility | Approved headroom plus broader listening/manifest evidence | Local work remains separate; cloud not run |
| T015 | Recovery and failure injection | Crash/replay/delete/restore results and ledger reconciliation | Not run |
| T016 | Observed onboarding and paid demand | Cohort funnel, support minutes, retention and cancellations | Not run |
| T017 | Build/no-build review | Gate applicability, measured economics and explicit decision | Blocked by missing evidence |

Scope in T009 must specify the original fixture source, permitted processing/retention, provider and region, maximum total upload bytes, maximum job count/runtime, maximum spend, stop conditions and cleanup evidence. A provider free tier does not waive this boundary. Send no recruitment/vendor/legal messages unless that outreach is explicitly authorized.

## Proposed experiment details

EX003 upload comparison: same files and client/network settings against B2/R2, cold and resumed sessions. Collect at least 30 successful file transfers per selected size class and at least 10 interruption cases per browser/network pattern, subject to a final approved byte cap. Measure full SHA-256 match, throughput, bytes resent, orphan-part cleanup and actual billing counters. If the dataset budget cannot support the sample, report the smaller coverage.

EX004 playback/security: at least two synthetic tenants and 100 play/seek trials per supported browser/path/network profile for initial p95 estimates. Record failures and confidence limitations; tail estimates from 100 observations remain noisy. Check expired/malformed links, wrong IDs, deleted/quarantined objects, cache isolation, 206/416 behavior and codec-specific seek positions. All unauthorized successes are hard failures.

EX005 analysis portability: choose exact licensed fixtures and pinned candidate runtimes before testing. Measure wall time, peak RSS, scratch, thread count, CPU/GPU time, worker output bytes and estimate disagreements. Compare with approved reference annotations or human review where available, not just another model. A synthetic tone does not validate musical key/downbeat/structure quality. Do not use the existing real pool without separate authorization.

EX006 render: finish local headroom policy first. Test identical plan/input/environment runs, explicit duration and sample-alignment checks, output true peak and version/hash equality. Blinded listening should compare the accepted baseline, bounded proposed styles and an appropriate manual reference. Proposed initial coverage: at least ten distinct transitions and five listeners for usability direction, followed by a broader genre/corpus gate if scope expands. This is a proposed protocol, not existing validation.

EX007 resilience: crash before/after object completion, before/after DB publication, during render and after cancel. Replay events and billable acknowledgements. Delete sources/accounts during pending/running jobs, restore backups and verify tombstones. Track cleanup cost and user-visible results. Repeat provider throttling/outage simulations with bounded retries.

## Conditional build slices

These are future agent task specifications. No code paths are created by this report.

| Slice | Prerequisites | Implementation acceptance | Rollback/stop condition |
|---|---|---|---|
| B01 Account/library foundation | Approved scope, entity/privacy/auth choice | Tenant membership, immutable IDs, audited migrations, session recovery | Any bypass across tenants |
| B02 Upload and verification | B01, provider contract spike | Direct resumable transfer, reservations, checksums, quarantine, idempotent finalize/cancel | Corrupt accepted bytes, quota bypass or source overwrite |
| B03 Browse and playback | B02, codec/access tests | Stable pagination, private ranges, explicit unavailable state, TTL recovery | Data leak or unacceptable measured startup/seek |
| B04 Descriptor evidence/corrections | B03, licensed analysis choice if included | Raw tags preserved, provenance, unknowns, revision conflicts and user overlays | Fabricated evidence or overwritten user corrections |
| B05 Playlist host integration | Explicit resume/integration authorization, B04 | Independent package adapter, minimal model payload, schema/refusal handling and retrieval eval | Model controls tenant access or missing hard constraints hidden |
| B06 Manual approved-plan service | Explicit render authorization, B04, G006 | Bounded jobs, source/hash checks, quality publication, cancel/retry/ledger | Clipping, invalid bounds, duplicate charges, nondeterministic claim unsupported |
| B07 Automatic proposal bridge | Separate automatic-planning authorization, B05/B06 | Declarative proposal, validation, user review, no direct execution | Proposal bypasses engine validator or triggers unapproved work |
| B08 Beta operations | Scoped gates passed, B01–B03 at minimum | Measured quotas/billing, deletion/export, restore, support and incident ownership | Failed safety/legal/economics gate |
| B09 Wider launch | Retained paid demand and measured tail costs | Published capabilities/limits agree with actual tests; launch decision recorded | Unsupported unlimited or quality claims |

Each slice must provide a compact evidence manifest: authorization reference, changed paths, contract versions, fixtures, test commands/results, budgets, safety limits, open defects, rollback and log updates. Test the boundary affected by a change; do not rerun heavy corpus analysis as generic CI.

## Resource planning

No responsible calendar estimate is possible before audience, runtime and licensing decisions. Plan by evidence milestones and bounded tasks. The first implementation candidate should be a small upload→verify→browse→play vertical slice, with optional analysis and mixes behind independent flags.

Costed staffing categories: product interviewing/usability, cloud/API/frontend, audio/runtime engineering, legal/license review, security review and operations/support. One person may cover several categories, but the responsibilities cannot disappear. Agent implementation speed does not eliminate recruitment, listening, license response time or operational ownership.

## Build/no-build readout template

State proposed release scope, user segment, geography, rights basis, provider and total expected cost. For each applicable gate list the threshold fixed before testing, observed numerator/denominator, artifact, remaining failure and reviewer decision. Then choose one of: continue discovery, approve capped spike, approve scoped build, pivot, stop.

A stop/pivot decision must specify what remains reusable locally, what resources/data must be deleted, why the rejected route failed, and what new evidence could reopen it. A go decision must name exactly which held capabilities are now authorized. Never infer automatic mixing authorization from approval of library playback.
