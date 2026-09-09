# Agent maintenance protocol

## Sources of truth

Use STATUS.md for compact current state; registers.json for structured records; events.jsonl for append-only change history; reports for analysis; sources.json for evidence metadata; parent decision/experiment logs for project-wide authority. Neither a report nor a register can create authorization beyond an explicit user instruction.

An accepted user steer updates the current plan. Preserve the previous reasoning and supersede it; do not rewrite history as though the current direction was always intended.

## When work arrives

1. Read the local takeover and current gate/task state.
2. Classify the work: research, decision, experiment, implementation, incident or maintenance.
3. Identify existing authorization and affected boundaries. Continue reversible research without repeat confirmation.
4. Reserve new IDs by inspecting the full registry; never reuse a deleted or superseded ID.
5. Complete the bounded work; collect exact results, contrary evidence and limitations.
6. Append an event with source, old/new status, reason, affected IDs and evidence paths.
7. Update current registers and relevant reports together.
8. Update STATUS.md and parent handoffs if recommendation, authorization, integration or active track changes.
9. Validate references/JSON/formulas as applicable and record actual checks.
10. End with the next actionable task and unresolved dependency, without claiming a scheduled follow-up exists.

## State conventions

Tasks: open, draft_ready, done_research, requires_authorization, blocked_by_evidence, implementation_unauthorized, separate_active_track, in_progress, done, superseded.
Experiments: not_run, authorized, running, completed, failed, cancelled.
Gates: not_passed, passed, failed, waived_for_scoped_release. A waiver needs named authority, rationale and explicit scope; it never deletes the full-product requirement.
Decisions: proposed, accepted_scope, accepted_inherited, accepted_documentation, accepted_implementation, rejected, superseded.
Paths: retained_alternative, unproven, deferred, not_recommended, rejected_for_scope, failed_in_experiment.
Failures: open, resolved, resolved_for_screening, accepted_risk, superseded.

No experiment can become completed without a result artifact, sample/fixture, version, actual observations and authorization reference. No gate can become passed from a plan alone. Distinguish “unproven” from “failed”: a platform incompatibility hypothesis is not a benchmark failure.

## Source refresh

Before a vendor decision, paid test or legal gate, fetch current primary sources. Refresh prices after 30 days; refresh legal/provider/model terms at every relevant gate. Check effective dates, geography, account tier, units and whether old statements were superseded. Leave unknown fields null. Do not invent publication dates from crawl dates.

For a changed source, append a source-review event, retain the earlier observation in a dated revision record and update sources.json's current claim. Link decisions/cost inputs affected. Do not automatically implement an architecture change because a price moved.

When a page fails, record the attempted URL, observed failure, date, impact and alternative source. Avoid repeated identical fetches. A failed retrieval does not prove a product or feature is unavailable. Do not save large copyrighted pages when short paraphrases and exact links suffice.

## Decisions and rejected routes

Every decision needs the problem, alternatives, criteria, evidence, rationale, consequences, scope, authority and reopen conditions. An alternative may be cheaper but rejected for latency, retention, rights, operator burden or evidence gaps. Record the actual reason; do not invent precision with arbitrary weighted scores.

Add failed experiments to failures with expected versus observed behavior and the distinction between root cause and hypothesis. Link mitigation tasks and tests. Preserve bad results, including promising routes that proved unviable. Never delete a failure because a later attempt succeeded.

## Cost model maintenance

inputs.json is the published source for rates and reference scenarios. Spreadsheet inputs are editable for exploration. Before adopting edits, export/inspect changed values, reconcile them into JSON, rebuild/recalculate, verify case selection and representative boundaries, compare with independent arithmetic, and update calculated.json plus the revision event.

Preserve the previous accepted inputs/output under a dated revision before replacing it. Do not hand-edit calculated outputs to make a scenario attractive. Mark excluded licenses/taxes/support or unmeasured costs prominently. Rounding is presentation, not a change to underlying rates.

## Coordination and handoff

Keep work bounded by artifact/contract ownership. The playlist package is paused; cloud discovery may read its contracts but cannot silently resume implementation. The engine's local headroom task stays separate. Do not spawn or schedule other tasks/agents without applicable authorization.

For a handoff, record completed outputs, unchanged boundaries, current recommendation, highest-risk unknowns, next task, exact approval needed for dependent actions, and where results must be logged. Keep instructions short enough to load before detailed reports.

No recurring automation has been created. This protocol supports future updates when a task or steer arrives. A later requested monitor should define scope, cadence, cost, stop conditions and meaningful notification triggers explicitly.
