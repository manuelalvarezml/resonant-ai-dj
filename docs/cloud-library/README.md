# Cloud music library discovery

Start with [AGENTS.md](AGENTS.md), then [STATUS.md](STATUS.md). This package is the maintained discovery and proposed-build specification for the cloud phase in ../../PLAN.md, D042 and D043. It is designed to survive agent handoffs without reconstructing chat.

**Current recommendation: continue discovery; do not start a full cloud build.** Desk research and proposed contracts are complete for this revision. Customer validation, legal clearance, commercial model/dependency review, provider benchmarks and deployment portability remain unproven. No vendor has been selected or purchased.

## Reading paths

| Need | Read |
|---|---|
| Five-minute takeover | [STATUS.md](STATUS.md), then [RESEARCH_REPORT.md](RESEARCH_REPORT.md) |
| Storage decision, first roadmap item | [STORAGE_COMPARISON.md](STORAGE_COMPARISON.md) |
| Demand, differentiation, onboarding and usability | [PRODUCT_VALIDATION.md](PRODUCT_VALIDATION.md) |
| Proposed service and development workflow | [ARCHITECTURE.md](ARCHITECTURE.md) |
| Data, API and job boundaries | [CONTRACTS.md](CONTRACTS.md) |
| Threat model, privacy, copyright and software/model licenses | [SECURITY_RIGHTS.md](SECURITY_RIGHTS.md) |
| Cost assumptions and pricing experiments | [UNIT_ECONOMICS.md](UNIT_ECONOMICS.md), [cost model](economics/UNIT_ECONOMICS.xlsx) |
| Milestones, acceptance criteria, dependencies | [DELIVERY_PLAN.md](DELIVERY_PLAN.md), [registers.json](registers.json) |
| Reliability, incident response and recovery | [OPERATIONS.md](OPERATIONS.md) |
| Record a steer, decision, failed attempt or rejected route | [MAINTENANCE.md](MAINTENANCE.md), [TEMPLATES.md](TEMPLATES.md) |
| Audit evidence and coverage | [SOURCES.md](SOURCES.md), [TRACEABILITY.md](TRACEABILITY.md), [VERIFICATION.md](VERIFICATION.md) |

## Artifact ownership

Narrative reports explain reasoning. registers.json owns current structured statuses, dependencies, gate definitions and open questions. events.jsonl owns append-only changes to those statuses. sources.json owns source metadata. economics/inputs.json owns the published cost scenario inputs; the workbook is an editable analysis view whose accepted changes must be reconciled back into that JSON before a new research revision. Never treat independently edited copies as automatically synchronized.

All proposed architecture and contracts remain discovery material, not current runtime schemas. Live engine contracts remain ../SCHEMAS.md and the engine models; playlist contracts remain in the independent package. Historical engine tests and listening findings are not cloud validation.

Research revision 1.0, dated 2026-09-08. No recurring automation is installed. Future work follows the maintenance protocol when a new task, steer, experiment or source update arrives.
