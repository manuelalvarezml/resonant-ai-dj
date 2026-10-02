# MAEST listener findings — 2026-09-14

Source: the owner's pasted 33-song listening review in this task. Structured
transcription: `maest-listener-review-2026-09-14.json`. Exact filenames and hashes
join to the saved model results. Notes preserve wording; copied HTML spaces,
trailing commas and Markdown filename escapes are cleaned. Duplicate accepted
labels and conflicting field/note judgments remain explicit.

## Recommendation, pending owner's decision

Keep MAEST as a useful parallel multi-label genre estimator and preserve the
previous EffNet/Jamendo model. Do not convert this listening feedback into an
automatic model replacement or search-policy change.

The listener describes useful genre suggestions across all 33 reviewed songs.
Only six accepted-genre fields contain a single distinct genre; the other 27
contain multiple genres. Some notes allow additional labels even where the
accepted field is narrower. This is evidence of owner-perceived usefulness on
this selected sample, not a held-out accuracy measurement or a controlled
head-to-head comparison with the previous estimator.

A fixed top-three cutoff loses requested information: Synthwave at rank 6 for
Work Out Tonight, Experimental at rank 6 for And We Hear I Love You, Hard House
at rank 5 for Play, Breakbeat at rank 4 for Ritmo Actual. Experimental is also
explicitly essential for Bachetrón. One accepted Dance-pop score is only 8.1%;
a universal high probability threshold would discard a useful owner judgment.
Conversely, high scores do not imply the owner wants all the proposed labels.

Proposed presentation: one primary suggestion, an expandable ranked candidate
list (retain all 519 internally), and independently selectable complementary
genres. Accepted genres become human judgments with provenance, never rewritten
model probabilities. Do not automatically promote all ten suggestions to tags.
Some tracks require only House; others require a combination of style labels.

Low top-two margin is not necessarily failure: Excursions has near-tied Boom Bap
and Jazzy Hip-Hop that the owner approves together. A margin chart should be a
review-priority aid, not an automatic rejection rule.

## Ambiguities retained

- Catamaran repeats Psychedelic Rock and omits Garage Rock in the accepted field;
  notes approve the top three and favor Surf in position one or two.
- It's ok to cry lists three accepted genres but notes approve four.
- Italiani omits House in the accepted field, although notes approve top three
  plus Chanson.
- Ma quale idea lists two accepted genres; notes approve top five and top three.
- Victim calls Experimental fourth; it is fifth in the saved model output.
- DON'T DIE YOUNG requests Pop without specifying an exact taxonomy label.

Do not silently resolve these into definitive ground-truth labels. They do not
block the broad usefulness conclusion, but do block exact precision/recall or
rank-accuracy claims from these fields alone. The four RAM-limit failures still
have no semantic judgments and cannot count as model successes.

## Report repair and verification limits

The copied page count is the build-time fallback wording, suggesting that its
interactive initialization did not complete. The prior script declared a global
`top` helper, which can conflict with a browser's `window.top`. The script now
uses a scoped block and `topScore`; browser-specific root cause remains
unconfirmed. All 33 judgments are embedded in both static and interactive views,
with a revision-specific browser-storage key to avoid prior dummy-test values.
Previous browser storage is not deleted. Syntax and isolated DOM checks pass,
including 33 exportable judgments. Actual browser verification remains pending.
