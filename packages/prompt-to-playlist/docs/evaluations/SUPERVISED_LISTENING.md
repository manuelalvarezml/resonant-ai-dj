# Supervised estimator listening workflow

This is a **development exercise**, not the held-out quality test needed to promote a model. Only Ocean and Paradise have new estimates. No new listening judgments have been entered.

1. The organizer keeps `output/supervised-estimators/comparison-v1/organizer-key.json` private until judgments are complete. It identifies which estimator produced each randomized playlist code. Do not show scores or model names to reviewers.
2. Give Manuel and Grecia their separate `blind-development-<name>.md` or JSON sheet. Each has the seven scenes and independently shuffled profile order. Use the same playback volume/setup; pause between scenes. A track repeated in different codes contains identical audio.
3. Listen to the listed order, then record scene fit (1–5), preference over other codes, ties and short reasons. Independently rate each track's perceived valence and arousal (1–9), urge to move (1–5), and personal induced feeling. “Unsure” is a valid note; do not force a numerical judgment.
4. Keep the original question/scene explicit. Calm beach and energetic beach are separate conditions. Heartbreak ratings cannot certify lyric meaning. Intimate/romantic fit is not determined by arousal alone.
5. Save completed sheets under new filenames before rerunning the generator; the generator rebuilds blank development templates. Compare Manuel and Grecia separately before any aggregate; preserve disagreement.
6. After unblinding, the organizer pairs code judgments with frozen results, reports ties and failures, and chooses whether a larger **explicitly authorized**, artist/release-disjoint held-out test is warranted. These two known examples cannot establish general accuracy or optimal thresholds.

Track lookup (same original audio for all profiles):

| ID in evidence | Track | Local player lookup |
|---|---|---|
| smoke-ocean | Listen Over the Ocean — Violet Eves | Search title in Your Library |
| smoke-paradise | My Paradise - Edit — The Trip | Search title in Your Library |

To inspect engineering behavior separately, use PlaylistIQ's Compared tracks only scope and each estimator profile. This ordinary UI reveals model identities and is **not blind review**. The notebook preserves exact results and profile/scope; its human verdict starts empty.

The [full protocol](../research/SUPERVISED_ESTIMATORS_2026-09-25.md) specifies held-out sampling, metrics and promotion requirements. No broader inference or human review is automatically authorized by this file.
