# PlaylistIQ estimator upgrade — reader digest

2026-09-22. [Full research](ESTIMATOR_UPGRADE_2026-09-22.md) · [Implementation, setup and evidence](../ESTIMATOR_UPGRADE.md)

## What we chose and built

A hybrid local system: **MuQ-MuLan** compares music with nuanced descriptions such as airy, intimate, wistful or propulsive; **Essentia's shared EffNet heads** add 56 mood/theme and 40 instrument scores. Existing genre, tempo, key, loudness, danceability and vocal estimators stay in place. Valence is now visible beside arousal.

One LLM call turns a creative request into explicit constraints, available soft preferences and an English musical description. Local text/audio comparison adds a provisional semantic contribution to the structured score. Explanations preserve the exact description, evidence, sampled coverage and arithmetic. No audio is uploaded, and no extra LLM call explains each song.

## Why this choice

A beach day can mean energetic social music or calm open-air music; calm alone cannot distinguish the beach from an intimate evening. More expressive retrieval is useful, but personal interpretation still needs assumptions, clarification and feedback. MuQ offers a practical released music/text implementation; the additional small EffNet heads reuse an embedding we already compute. FIGMA's new retrieval results and Music2Emo's supervised emotion work are promising comparison candidates, not proven better for our situations.

## What passed

- **442 Python tests, 77 web tests**, syntax and production build verification.
- Exactly **two existing songs** received real new inference; original hashes stayed unchanged. Both upgraded records are available in Chrome.
- MuQ took **13–17 seconds per tested song**, with a largest measured worker RSS of **2.8 GiB**. This samples three ten-second windows, not the whole track.
- Cached retries ran **zero stages**. Stored query/result replay was exact.
- Seven live requests across three creative cases exposed an untranslated description and an unavailable soft field. Planner v1.6 fixed the affected case by constraining its response schema, with the failures retained.

## What the tests did not prove

The semantic branch still preferred the house track for the intimate-evening prompt. The combined score kept Listen Over the Ocean first, but that is not a listening verdict. We have built a better way to represent, compare and audit musical intent; we have **not yet proved better playlist quality**. Cosine similarity is not a mood probability, and the strongest candidate in a weak library may still be wrong.

The rest of the library keeps its existing analysis. **Analyze Tracks** upgrades it explicitly, or use a track's **Upgrade / retry analysis** action. Semantic ranking activates only when all eligible candidates have compatible embeddings; incomplete new label coverage is omitted fairly. The immediate next evaluation is blind listening across several scenes, followed by a same-data comparison with FIGMA/Music2Emo if errors persist. JSON remains current; considering YAML is still on the to-do list.
