# Musical character: 120 concepts and reusable matching

Current checkpoint: 2026-10-01. Bank `musical-character-v2-120`; web feature version `selected-estimators-v3-character120`.

## What changed

The owner approved replacing the 32-description inspection bank with 120 carefully written concepts and explicitly requires existing audio embeddings to be reused. The bank contains 30 emotion, 25 groove, 25 texture, 20 intensity and 20 space/arrangement concepts. These are hand-written comparison probes, not newly trained classes. Descriptions focus on one musical dimension rather than inferring a scene, era, artist, genre or personal preference. Audio is downmixed to mono, so stereo-width probes were deliberately excluded. Arrangement/intensity labels characterize the sampled excerpts, not an exhaustive structural analysis of the whole song.

The Analysis column remains **Musical character**. For the new bank it shows the two strongest relative matches in each dimension, rather than letting generic electronic/groove labels occupy all four slots. Details retains all 120 scores, exact descriptions, dimensions, bank version, sampled coverage and segment score range. Old 32-label records remain readable and visibly offer a refresh. No confidence threshold has been invented; these are uncalibrated similarities. Music2Emo coverage now says “90 seconds analyzed” to avoid confusion with the 1990s.

## Audio extraction and description matching are independent

1. Text setup encodes each description once, using the existing pinned MuQ-MuLan encoder. Individual vectors are cached by exact text and encoder identity. A complete bank artifact contains the descriptions and their 512-dimensional normalized embeddings.
2. On Analyze Tracks, compatible audio vectors are recovered by source SHA-256 from the existing feature record, independent audio cache or saved stage checkpoint. Encoder identity, sampling policy, dimensions, finite normalized values, duration and segment intervals must validate.
3. Description matching reads the cached text vectors and computes cosines against the existing audio segments. It does not load MuQ, PyTorch or audio decoders. The record retains the same audio vectors and replaces the old descriptor scores with all 120 new scores.
4. Only a track without compatible audio embeddings runs audio extraction. New audio vectors are atomically saved independently before matching, so later matching failures do not discard them.
5. Bank version/content hash and audio-vector fingerprint identify the score computation separately from audio identity. Bank changes invalidate matching, not audio extraction. A fully current retry does neither. `executed_algorithms` records requested analyzer work; `rematched_algorithms` separately reports the lightweight refresh.

Other missing/stale estimators still run when using the full Analyze Tracks action. Existing compatible stages are reused. The bank's scores still do **not** feed the playlist planner or ranking: prompt-specific text continues to be compared directly with saved audio embeddings, using unchanged scoring policies.

Cached artifacts:

- `output/semantic-text-cache/`: exact-text/encoder caches.
- `output/semantic-description-banks/musical-character-v2-120.json`: complete bank and text embeddings.
- `output/semantic-audio-cache/<source-sha256>.json`: audio vectors independent of bank wording.
- `output/web-features/<source-sha256>.json`: current user-facing feature result; replaced records retained in its history directory.

## Preparation and verification

From the PlaylistIQ package: `.venv/bin/python scripts/prepare_character_bank.py`. This uses the existing guarded worker, offline models, four CPU threads, 6000 MiB RSS cap and 1024 MiB available-memory floor. Preparation is text-only. Ordinary matching deliberately refuses a missing text cache with an actionable setup error instead of silently loading a model.

All **120/120** text vectors were saved and validated. Initial preparation took **34.38 seconds**, peak worker RSS **1574.8 MiB**, minimum host available memory **2664.6 MiB**. Worker status: passed.

`scripts/smoke_character_matching.py` upgraded exactly the two existing acceptance tracks: Listen Over the Ocean and My Paradise – Edit. It forbids model loading, audio decoding and analyzer execution, asserts audio vectors and all other stage records are unchanged, and checks a subsequent no-op retry. Matching took 0.0424 / 0.0417 seconds; complete bridge calls took 0.211 / 0.160 seconds. Both production caches now have the new bank. No other track was rescored and no audio inference ran.

Evidence: `output/semantic-description-banks/matching-acceptance.json`, `musical-character-v2-120-preparation.json` and `http-acceptance.json`. The real local HTTP analysis route returned both current records with 120 descriptions, no analyzer execution and no additional matching on retry.

Validation: 516 Python tests and 85 web tests pass; JS syntax/build acceptance is recorded in the work log. Tests cover changed-bank invalidation, exact vector preservation, independent-cache reuse, rejection of stale/malformed audio vectors, missing-text-cache refusal, bridge refresh/history/no-op retry, and grouped display. Initial test invocations from the DJ root used the wrong environment/path; they were corrected to the package environment. There were no model preparation or matching failures.

This is implementation verification, not evidence of improved listening accuracy. Evaluate the new bank across varied tracks and listener judgments before claiming superiority or integrating it into ranking. Whole-library analysis remains the owner's next manual action. There is no batch analysis running from this task.

## Complete concept bank

Each row is the exact English text used for the saved embedding.

### Emotion — 30

| Concept | Description |
|---|---|
| wistful | Music with a wistful sense of longing for something absent. |
| melancholic | Music with a gently melancholy emotional character. |
| bittersweet | Music that blends sweetness with an undercurrent of sadness. |
| nostalgic | Music that evokes affectionate memories and a feeling of looking back. |
| tender | Music with a tender, caring emotional expression. |
| romantic | Music with an affectionate romantic mood. |
| sensual | Music with a sensual, alluring emotional character. |
| intimate | Music with a close, personal and emotionally intimate atmosphere. |
| serene | Music with a serene feeling of inner peace. |
| contented | Music with a settled, quietly contented mood. |
| hopeful | Music with a hopeful sense of possibility. |
| uplifting | Music with an encouraging, emotionally uplifting character. |
| joyful | Music expressing uncomplicated joy and delight. |
| euphoric | Music with an ecstatic, euphoric emotional quality. |
| celebratory | Music with a festive mood of shared celebration. |
| playful | Music with a playful, mischievous emotional character. |
| confident | Music with a confident, self-assured attitude. |
| triumphant | Music with a feeling of victory and triumph. |
| solemn | Music with a solemn, serious emotional tone. |
| mournful | Music with a grieving, mournful emotional expression. |
| lonely | Music conveying loneliness and emotional isolation. |
| vulnerable | Music with an exposed, emotionally vulnerable character. |
| yearning | Music expressing an insistent desire or emotional yearning. |
| reflective | Music with a thoughtful, inward-looking emotional character. |
| detached | Music with an emotionally distant, detached attitude. |
| brooding | Music with a dark, brooding emotional atmosphere. |
| uneasy | Music with an unsettled, uneasy emotional feeling. |
| suspenseful | Music that creates suspense and anticipation. |
| angry | Music expressing anger and confrontation. |
| defiant | Music with a rebellious, defiant emotional attitude. |

### Groove — 25

| Concept | Description |
|---|---|
| straight pulse | Music with an even, straight rhythmic pulse. |
| four on the floor | Music with a kick drum marking every beat in a steady dance groove. |
| offbeat pulse | Music with prominent accents between the main beats. |
| syncopated | Music with rhythmic accents that play against the expected beat. |
| swinging | Music with a swinging rhythm and unevenly spaced subdivisions. |
| shuffling | Music with a continuous shuffle feel in its rhythmic subdivisions. |
| bouncy | Music with a buoyant, springy rhythmic groove. |
| rolling | Music with a smoothly rolling rhythmic groove. |
| loping | Music with a loping rhythm that rocks forward in long, uneven strides. |
| strutting | Music with a swaggering, strutting rhythmic feel. |
| laid back | Music with a laid-back groove that feels behind the beat. |
| propulsive | Music with a rhythm that insistently pushes forward. |
| stomping | Music with a heavy, stamping rhythmic pulse. |
| skipping | Music with a light, skipping rhythmic pattern. |
| jerky | Music with an angular, stop-start rhythmic feel. |
| broken beat | Music with a broken drum pattern rather than an even kick on every beat. |
| half time | Music with a spacious half-time drum feel and widely separated backbeats. |
| backbeat | Music with a clearly accented snare backbeat. |
| polyrhythmic | Music with interlocking rhythmic patterns that suggest different pulses. |
| hand percussion groove | Music whose groove is carried by interlocking hand percussion. |
| repetitive groove | Music with a persistent rhythmic pattern repeated with small variations. |
| fluid rhythm | Music with a fluid rhythm that changes naturally rather than repeating rigidly. |
| free rhythm | Music with freely unfolding timing and no regular rhythmic pulse. |
| waltzing | Music with a swaying rhythm grouped into three beats. |
| dancefloor | Music with a pronounced groove that invites sustained dancing. |

### Texture — 25

| Concept | Description |
|---|---|
| dreamy | Music with soft, dreamlike sonic textures. |
| shimmering | Music with shimmering, glistening high-frequency textures. |
| hazy | Music with blurred, hazy sonic edges. |
| airy | Music with light, airy instrumental textures. |
| warm | Music with warm, rounded timbres. |
| bright | Music with bright, clear-edged timbres. |
| dark toned | Music with dark, low-toned instrumental colors. |
| metallic | Music with ringing, metallic timbres. |
| glassy | Music with clear, glass-like synthetic tones. |
| velvety | Music with smooth, velvety instrumental tones. |
| gritty | Music with a grainy, gritty sonic texture. |
| distorted | Music with audibly distorted instrumental sounds. |
| fuzzy | Music with a fuzzy, softly saturated sound. |
| crisp | Music with crisp, sharply defined sound attacks. |
| soft edged | Music with softened attacks and gently rounded sound edges. |
| woody | Music with resonant, woody instrumental timbres. |
| breathy | Music with audible breath and breathy instrumental or vocal tones. |
| acoustic | Music dominated by the resonances of acoustic instruments. |
| electronic | Music with synthesized electronic textures and programmed sounds. |
| analog synth | Music with rounded, gently drifting analog synthesizer tones. |
| plucked | Music with prominent plucked-string textures and short resonant decays. |
| bowed | Music with sustained bowed-string textures. |
| percussive | Music whose sonic texture emphasizes struck and percussive sounds. |
| bass rich | Music with a prominent, full low-frequency texture. |
| choral | Music with blended, sustained layers of human voices. |

### Intensity — 20

| Concept | Description |
|---|---|
| restrained | Music with a restrained level of force and emphasis. |
| gentle | Music played with gentle force and delicate emphasis. |
| calm | Music with a calm, unhurried level of activity. |
| sedate | Music with very little kinetic energy or urgency. |
| moderate energy | Music with a moderate, steady level of energy. |
| animated | Music with an animated, lively level of activity. |
| energetic | Music with vigorous, sustained energy. |
| explosive | Music with sudden explosive bursts of force. |
| fierce | Music delivered with fierce, forceful intensity. |
| relentless | Music that maintains unrelenting intensity with little respite. |
| urgent | Music with a strong sense of urgency. |
| leisurely | Music that unfolds at a leisurely pace without pressure. |
| simmering | Music with contained intensity that feels ready to rise. |
| surging | Music whose intensity repeatedly swells and recedes. |
| building | Music that gradually increases in intensity. |
| subsiding | Music that gradually settles and loses intensity. |
| even intensity | Music that maintains a consistent level of intensity. |
| contrasting dynamics | Music with strong contrasts between restrained and forceful passages. |
| light touch | Music performed with a light touch and little physical weight. |
| heavy impact | Music with weighty attacks and a strong sense of physical impact. |

### Space and arrangement — 20

| Concept | Description |
|---|---|
| sparse | Music with few simultaneous parts and substantial gaps between sounds. |
| dense | Music with many simultaneous parts filling the arrangement. |
| minimal | Music built from a small number of recurring musical elements. |
| layered | Music with several clearly overlapping instrumental layers. |
| lush | Music with rich, enveloping layers of harmony. |
| spacious | Music with a pronounced sense of space around individual sounds. |
| close dry | Music with close, dry sounds and little audible reverberation. |
| reverberant | Music with long reverberant tails around voices or instruments. |
| echoing | Music with clearly audible repeating echoes. |
| distant | Music with sounds that seem distant and set back in the arrangement. |
| foreground vocal | Music with the lead voice prominently forward in the arrangement. |
| blended vocal | Music with vocals blended into the instrumental background. |
| call and response | Music arranged as alternating calls and answering musical phrases. |
| drone based | Music organized around a continuous sustained drone. |
| arpeggiated | Music with repeating arpeggios outlining its harmonies. |
| chordal | Music organized around sustained or repeated blocks of chords. |
| interlocking lines | Music with separate melodic lines that interlock and answer one another. |
| long sustained tones | Music with an arrangement dominated by long, sustained tones. |
| short detached notes | Music with an arrangement dominated by short, separated notes. |
| evolving arrangement | Music whose arrangement gradually changes as parts enter and leave. |


## Final app acceptance

Chrome loaded the current Analysis page and visibly showed the five character dimensions, 120-description notice and spelled-out sampling coverage for the cached Ocean record. Its new labels differ from the original bank; for example, the groove suggestions included laid back and waltzing. These are model outputs requiring listening review, not newly verified facts about that track. Search was cleared and the enabled Analyze Tracks button left ready. The browser showed 237 unique tracks at that point; no batch was started by the agent. All preparation/analysis workers had exited. Syntax validation passed for 45 JavaScript modules; production build passed with 28 static files.
