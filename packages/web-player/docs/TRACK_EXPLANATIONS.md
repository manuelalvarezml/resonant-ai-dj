# PlaylistIQ track explanations

## Hybrid explanation update — 2026-09-22

`hybrid-semantic-v1` explanations now show the planner's saved musical description, the local segment cosine/range, relative rank and semantic points separately from classifier support. Cosine is never presented as a mood probability. The numeric explanation reconciles the actual 70% structured / 30% semantic shares when both exist, or semantic alone; the old 65/35 genre/preference blend remains inside the structured portion. “Largest unused share” describes point arithmetic, not a measured gap from perfect musical taste. Coverage/fallback warnings and sampled-duration limits stay visible.

77 web tests cover legacy and hybrid behavior, numeric reconciliation, escaping and uncertainty. Chrome acceptance inspected the two upgraded Analysis/details records; fresh hybrid result rendering is covered by tests rather than a new whole-library browser submission. See [pipeline evidence](../../prompt-to-playlist/docs/ESTIMATOR_UPGRADE.md).

## User-facing behavior

Each **Why this track** disclosure now leads with a short explanation of the audio qualities contributing most to the planned playlist, followed by the biggest gap from its available score. It also shows:

- **Musical fit out of 100**, explicitly distinguished from a probability that the listener will like the track.
- **Position and ordering:** relevance normally; requested tempo order takes precedence and uses fit to break tempo ties.
- **Qualification rules:** required genres, genre alternatives, BPM bounds and exclusions. Passing a BPM or exclusion filter adds no points; required genres also contribute according to their recorded support.
- **Each scored objective:** readable musical descriptor, explicit versus inferred origin, primary/secondary/optional priority when available, source quote when retained, evidence value, preference fit, weight and earned points.
- **Total arithmetic**, source descriptions, missing/unscored preferences, and original engine notes under a secondary disclosure.

## Numerical example

If House has evidence **0.60** and weight **0.65**, it earns `0.60 × 0.65 × 100 = 39.00` points. If relaxed mood has evidence **0.80** and weight **0.35**, it earns **28.00** points. Total: **67.00 / 100**.

For a request for less aggression, evidence **0.20** becomes preference fit **1 − 0.20 = 0.80**. Missing evidence earns zero even when less of a quality is preferred. A low known value and a missing value therefore have different effects.

The presentation reads the engine's actual contribution weights. With both groups available, the current engine assigns explicit genre objectives 65% and other preferences 35%; a sole scoring group gets 100%. Within a group, priority weights are 3/2/1. Genre alternatives and broad families use the best-supported eligible style, not summed genre probabilities. Unavailable catalog objectives are omitted; missing per-track evidence does not redistribute its weight.

Values are displayed with two decimal places on a 0–100 scale. Rounded components can differ from the rounded total by a hundredth; the displayed total uses an approximation sign when needed. The saved full-precision contributions and original engine score remain unchanged.

## Implementation

`src/match-explanation.js` formats the existing `maest-intent-v1` score contributions and query. `src/playlistiq.js` embeds it inside each track disclosure. Text, labels, source quotes and raw notes are HTML-escaped. Existing or incomplete records without valid contributions display a truthful fallback instead of reconstructed weights.

This is deterministic presentation. It adds no per-track LLM calls, scoring changes, inferred audio features or listening judgments. Engine weights, model configuration, candidate selection and saved result contracts remain unchanged. Energy mapping is identified as provisional, and independent MAEST style scores are not presented as percentages that must sum to 100.

## Verification — 2026-09-19

64 web tests pass, including a recorded engine fixture, contribution totals, decreasing objectives, zero versus unknown evidence, genre OR/family support, BPM ordering, escaping, historical fallback and rounded-sum notation. Browser acceptance uses the owner's existing Chrome app and the current “dia de playa en yuyos” prompt. Existing playback buttons remain present. Two playlist submissions were used during UI verification; explanation rendering itself sends no model requests. Musical-quality acceptance remains separate.

## 2026-09-19 — Connection to the requested scene

**How it connects to your prompt** now precedes the numeric explanation. It displays the exact saved request, planner interpretation and available occasion/activity/recipient/emotional aim. Positive recorded contributions are connected to conditional listening roles: relaxed music could leave room for an unhurried moment; happy character could contribute a cheerful tone; danceability could invite movement. Each role says whether the planner inferred the preference or recorded it as explicit.

The roles describe possible functions of measured qualities. They do not assert that a track sounds romantic, contains beach imagery or captures a particular social setting. Missing/zero evidence cannot supply a positive scene claim; genre-only and missing-plan results have truthful fallbacks. No beach keyword rule or automatic energy correction was introduced. Existing score/weight arithmetic remains below **What drove its score**.

Saved attempts have **View these results** in the listening notebook. This reopens the exact original prompt, clarification, plan, result and scores without another LLM call. It also keeps the associated listener notes available. Playback still uses current library availability.

Validation: 69 web tests pass, including calm and energetic readings of a beach prompt, a different date scene, absent evidence, decreasing preferences, escaping and preservation of numeric explanations. Existing Chrome profile acceptance reopened the exact “un dia en la playa” result: Listen Over the Ocean by Violet Eves, 65.62/100. The scene explanation, original score and component total appeared together. Reported listener feedback was saved to that original notebook entry; whole-playlist verdict was left unchanged. No new LLM calls, audio inference or ranking changes were needed for this update.

See [the recorded scene mismatch](SCENE_FIT_FEEDBACK.md).
