# Cloud library unit economics

## Purpose and uncertainty

The [workbook](economics/UNIT_ECONOMICS.xlsx) is an editable scenario model, not a quote or revenue forecast. [inputs.json](economics/inputs.json) records the published assumptions for agents. [calculated.json](economics/calculated.json) preserves the reference outputs and upload scenarios. Accepted workbook edits must be reconciled to the JSON and versioned.

Storage prices are documented inputs. Compute, support, retries, acquisition and behavior are unmeasured assumptions. Licensing, taxes and merchant availability depend on unresolved entity/jurisdiction decisions. Do not call a margin “validated” while these are unknown.

## Model scope

Provider comparison uses average retained original bytes plus an editable derivative ratio and retained mix bytes. Monthly transfer includes playback, mix downloads, original exports and worker reads. Free tiers are conservatively excluded for R2/B2 to compare scalable marginal economics; Spaces and Supabase include their account bundles once. R2 request estimates include stated-rate marginal cost, not exact invoice unit rounding. Wasabi shows only a retained-storage base; early-delete charges and egress suitability are flagged separately. S3 price result is unavailable until the regional quote is supplied.

Whole-service contribution uses the B2 candidate as a transparent base scenario, without selecting it as the provider. It includes:
- Primary object storage and applicable origin transfer.
- A configurable retained backup copy.
- Monthly new-track analysis, per-job runtime and retry factor.
- Mix render runtime, repeated jobs and retry factor.
- Worker outbound transfer at a separately editable rate.
- Request translation tokens and bounded calls.
- Fixed DB/auth/API/queue/logging/monitoring allowance.
- Per-customer support and payment fees.
- A risk contingency applied to variable operating cost.

One-time acquisition and initial analysis are modeled separately from steady state and can be amortized over retained months. Trial users have storage/compute cost but no revenue. Initial full-library analysis must not be hidden in a monthly-new-tracks assumption.

## Units and equations

The published scenario retains one month of a 48kHz/24-bit WAV master plus
one compressed export for each one-hour mix. It models one compressed
download per mix. Extra master downloads, multiple retained months and
repeated downloads require increasing the corresponding inputs/transfer
assumptions before interpreting the result.

Use decimal GB=1e9 bytes for workload estimates. GiB=2^30 bytes and TiB=2^40 bytes. Store both the unit and provider conversion. A 320kbps stream uses 0.144 decimal GB/hour before protocol overhead. A one-hour stereo 48kHz/24-bit PCM WAV is 1.0368GB; a stereo 48kHz/16-bit WAV is 0.6912GB. These are calculations, not measured file sizes. Encoded outputs add headers and may use a different profile.

Upload hours = original_GB × 8000 / (uplink_Mbps × useful_fraction × 3600). A useful_fraction of 0.70 is a planning assumption. Track counts are independent inputs; do not infer lossless collection size from a fixed MP3 size.

Monthly analysis cost = new_tracks × minutes_per_track / 60 × worker_hourly_rate × retry_factor.
Initial analysis cost uses initial_track_count instead.
Monthly render cost = mixes × minutes_per_mix / 60 × worker_hourly_rate × retry_factor.
LLM cost = calls × (input_tokens×input_rate + output_tokens×output_rate) / 1e6.
Payment expense = gross revenue×percent_fee + successful_transactions×fixed_fee.
Contribution = gross revenue − modeled recurring operating expense − payment expense.
Contribution margin = contribution/gross revenue, unavailable at zero revenue.

Source for the token-price scenario: [GPT-5.4 mini](https://developers.openai.com/api/docs/models/gpt-5.4-mini) S045. The current package's model is preserved; this research does not run calls or choose a replacement. Token counts and call volume are assumptions; measure refusals, retries and prompt-size tails before pricing.

## Pricing experiments

Test constrained plans rather than publishing prices:
1. A small crate/library tier with explicit GB and processing allowances.
2. A larger DJ tier with additional retained storage and limited render credits.
3. Optional metered processing beyond an included cap, shown before execution.

Example willingness-to-pay anchors can be $9, $19 and $29/month, explicitly research hypotheses. They are not recommended commercial prices. A 1TB user at a low-price tier can consume much of revenue in storage/backup alone, even before support and processing. Reject an “unlimited library plus unlimited mixes” promise until measured tail economics and enforceable terms support it.

Do not charge by an opaque model cost. Present understandable storage and job allowances, failed-job policy, cancellation consequences, retention and what a rerender costs. Reserve usage before work; successful ledger reconciliation settles it once.

## Sensitivity and gates

Evaluate at least 10, 100 and 1,000 paying users; 25, 100, 500 and 1,000GB libraries; 10/50/200 listening hours; low/base/high analysis minutes; 0/4/20/100 mixes; 1.0/1.25/2.0 retry multipliers; 5/15/60 support minutes; and short retained lifetimes. These are input sweeps, not inferred percentiles. After a pilot, replace them with actual p50/p90/p95 usage and cohort retention.

Proposed economics gate: at target price, positive median contribution and ≥60% contribution margin under the agreed base case, with a nonnegative p95-user result under quota enforcement and acquisition payback within an agreed retained lifetime. Thresholds require owner agreement and measured costs; all are currently unpassed.

Common omitted costs to obtain before a final decision: commercial analyzer/model licenses, payment/tax/accounting, legal/security review, cross-region backup, restore/export events, support escalations, model/codec upgrades, maintenance engineering and outage compensation. A positive partial contribution scenario is not company profitability.

## Reference update protocol

Refresh provider prices before procurement or after 30 days, and after policy/region changes. Record exact units and effective date. Recompute all published scenarios, compare deltas, register any newly uneconomic path and explain whether price, workload or architecture changed. Keep older revision inputs/output checksums rather than overwriting history without an event.
