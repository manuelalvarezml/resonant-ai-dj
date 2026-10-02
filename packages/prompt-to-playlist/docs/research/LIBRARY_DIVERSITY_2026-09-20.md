# PlaylistIQ library diversity audit and album expansion plan

Audited 20 September 2026. Recommendations are a curatorial proposal, not predictions of the scores these recordings will receive.

## Main finding

The library has substantial variety **within electronic club music**, but very little breadth outside it. There are 44 distinct highest-ranked MAEST styles, yet 69 of the 88 genre-backed tracks (78.4%) have Electronic as their top family. Counting weaker secondary labels does not remove the imbalance: Electronic appears in the top six of 84/88 tracks (95.5%).

The best next additions are acoustic songs, jazz, soul, roots reggae, traditional Latin music, classical and ambient recordings, plus guitar-driven high-energy music. Simply adding slower house or more electronic subgenres would not provide enough new choices for everyday creative prompts.

## What was actually audited

- The **unfiltered Analysis table in the current Chrome app**, at `http://127.0.0.1:4173/?front=radio-wide#analysis`: 109 unique tracks, 83 complete, nine partial and 17 unanalyzed. These counts agree with the previous recovery audit, but were read again today.
- Available measurements: genre 88; BPM 85; mood, danceability, vocal profile, arousal, key and loudness 92 each. A partial track contributes only to dimensions for which a value is present. Unknowns are excluded from that dimension's denominator, never converted to zero.
- Values were extracted from the accessibility representation of the displayed table, with the app's one-decimal rounding. This is a UI snapshot, not a new hash-verified export of browser records. The [aggregate data snapshot](LIBRARY_DIVERSITY_2026-09-20.json) preserves counts, bins, medians, style counts and incomplete-track names.
- The disk cache separately contains 113 SHA-256 records: 101 complete and 12 partial. Those records are **not** interchangeable with the active Chrome library, so they were not used as the population for the charts.
- No new audio decoding, inference, importing, purchases or listening tests were performed. Album recommendations below draw on published album information and musical judgment, not measurements of new audio.

## Measured distribution

### Genres

Top family is the parent of the single highest-scoring style; it is a compact descriptive summary, not a replacement for PlaylistIQ's top-six matching policy. Top-six presence counts each track once per family; columns can therefore overlap.

| Family | Top family, of 88 | In top six, of 88 |
|---|---:|---:|
| Electronic | 69 | 84 |
| Latin | 9 | 13 |
| Rock | 5 | 7 |
| Hip Hop | 3 | 11 |
| Funk / Soul | 2 | 6 |
| Pop | 0 | 5 |
| Reggae | 0 | 2 |
| Folk, World, & Country | 0 | 1 |
| Jazz | 0 | 0 |
| Blues | 0 | 0 |
| Classical | 0 | 0 |

Twenty-one tracks have no displayed genre evidence. Zero here means no corresponding parent in the observed top six; it does not prove that the music has no stylistic influence from that family or that every omitted score among the 519 classes is zero. For example, Electronic / Future Jazz remains an Electronic-parent label in this calculation.

The strongest concentrations are House (11 top-ranked tracks), Techno (10), Reggaeton (7), Donk (6) and Synth-pop (4). The nine Latin-primary tracks are seven Reggaeton and two Guaracha. The two Funk / Soul-primary tracks are both Disco. Therefore neither group currently provides broad coverage of salsa, bolero, acoustic Afro-Peruvian music, gospel, soul ballads or R&B.

A sensitivity check requiring at least 20% support **within the observed top six** leaves Electronic on 80 tracks, Latin on 11, Rock on five, Hip Hop/Funk-Soul/Pop on four each, Reggae on one, and Folk-World-Country on none. This is only an audit illustration; 20% is not calibrated and is not a proposed runtime threshold. Three tracks have even their strongest genre below 25%: Rana, Bzzhound – Sexy Biatchh, and Jobsorato – Chamber Of Reflection. Their top labels deserve less interpretive weight.

### Tempo and energy

| Estimated BPM | Tracks, of 85 |
|---|---:|
| Below 80 | 0 |
| 80 to below 100 | 5 |
| 100 to below 120 | 12 |
| 120 to below 140 | 35 |
| 140 to below 160 | 26 |
| 160 to below 180 | 5 |
| 180 and above | 2 |

Median 130.4 BPM; range 85.7–200; 24 unknown. 61/85 (71.8%) fall in 120–<160 BPM. Most useful numerical expansion: slower perceived pulses and 80–120 material. Before pursuing fast-tempo quotas, review half/double-time readings: Buggin’ Out displays 187.5 while Excursions displays 96.8. This is a flag for listening/beat-grid review, not proof that either result is wrong.

Arousal ranges only from 4.0 to 7.2 on the model's nominal 1–9 scale; 74/92 tracks lie in 5–<7, 17 in 3–<5 and one in 7–9. No value is below 4.0. That narrow range may reflect both repertoire and model behavior. Do not force the library to occupy all theoretical DEAM values; first establish how low/high-energy reference recordings score.

### Mood and other descriptors

Each row is a separate score distribution. Mood dimensions do not sum to 100%, and a score is not a calibrated probability of listener approval.

| Descriptor | 0–<25% | 25–<50% | 50–<75% | 75–100% | Median |
|---|---:|---:|---:|---:|---:|
| Happy | 35 | 33 | 16 | 8 | 31.45% |
| Sad | 89 | 3 | 0 | 0 | 4.55% |
| Relaxed | 58 | 21 | 12 | 1 | 20.25% |
| Aggressive | 38 | 28 | 21 | 5 | 32.55% |
| Danceable | 1 | 2 | 2 | 87 | 98.8% |
| Vocal | 13 | 12 | 42 | 25 | 62.7% |

N=92 per row; 17 unknown. 85/92 have danceability at least 90%. Only Cumbia a la Luna reaches relaxed ≥75%. None reach sad ≥50%. These facts expose a weak test pool for sadness and nondance listening; they do **not** establish that the current library contains no sad music.

Vocal and instrumental are complementary outputs of one classifier: 25 tracks have vocal ≥75%, and 13 have instrumental ≥75%. Do not count these as independent mood dimensions.

Integrated loudness ranges from −16.4 to −4.5 LUFS, median −9.25; 62/92 are at least −10 LUFS. More spacious acoustic and classical recordings may expand production/dynamic variety, but loudness is not emotional energy. Keys: 56 minor and 36 major, with 17 unknown. Minor key is not a sadness label, and balancing keys is a much lower priority than balancing musical material.

## Exact albums to add

Choose the **original album program**, avoiding deluxe bonus discs and multiple remasters initially. Use an ordinary authorized digital edition suitable for local files; a linked reference page is not necessarily a download storefront or a recommendation for its expensive vinyl edition. Exact BPM, model mood scores and resulting genre counts must be measured after import. The functions below are my proposed listening-test uses, not objective labels for every song on an album.

### Pass 1 — strongest immediate expansion

| Priority | Exact album | What it adds and why I chose it | First listening checks |
|---|---|---|---|
| 1 | **Nick Drake — Pink Moon (1972)** | Sparse acoustic folk, voice/guitar intimacy, reflective and melancholic material. A sharp contrast to dense club production; useful for quiet solitude and heartbreak tests. [Album guide](https://nickdrake.com/albums.html). | Pink Moon; Place to Be; Things Behind the Sun. |
| 2 | **Erykah Badu — Baduizm (1997)** | Neo-soul/R&B, relaxed grooves and expressive vocals. Fills the space between overt dance music and beatless calm; useful for dinner, intimacy and unhurried social listening. [Album and editorial description](https://music.apple.com/us/album/baduizm/1440837269). | On & On; Next Lifetime; Otherside of the Game. |
| 3 | **Bob Marley & The Wailers — Kaya (1978)** | Roots-reggae repertoire with buoyancy and romantic warmth. A strong candidate set for a calm-but-social beach interpretation, with a perceptible groove. [Artist history](https://www.bobmarley.com/history/). | Easy Skanking; Is This Love; Satisfy My Soul. |
| 4 | **Stan Getz & João Gilberto — Getz/Gilberto (1964)** | Bossa nova and jazz, acoustic guitar/saxophone and light rhythmic motion. Helps distinguish relaxed outdoor or picnic music from dark or intimate late-night calm. [Verve album page](https://store.ververecords.com/products/stan-getz-joao-gilberto-getz-gilberto-verve-acoustic-sounds-series-lp). | The Girl from Ipanema; Corcovado; Doralice. |
| 5 | **Bill Evans Trio — Waltz for Debby (1962; Village Vanguard recording from 1961)** | Acoustic piano trio, instrumental jazz, ballad-to-swing variation and live ensemble interaction. Valuable for quieter prompts and tempo-estimator stress tests. This is the Evans/LaFaro/Motian album, not the later Monica Zetterlund collaboration. [Craft's six-track digital edition](https://craftrecordings.com/products/waltz-for-debby). | My Foolish Heart; Waltz for Debby; Milestones. |
| 6 | **Susana Baca — Susana Baca (1997, Luaka Bop)** | Afro-Peruvian vocal music and acoustic/percussive textures. Adds locally relevant musical breadth that a mostly electronic Latin subset does not supply. Recipient prompts should still ask about taste, rather than assuming every mother likes it. [Label album](https://www.luakabop.com/products/copy-of-x-susana-baca), [label artist description](https://www.luakabop.com/artists/susana-baca). | Negra Presentuosa; Luna Llena; Caras Lindas. |
| 7 | **Willie Colón & Rubén Blades — Siembra (1978)** | Salsa with live percussion, brass and narrative vocals. Adds energetic social/dance choices beyond electronic club music—especially useful for a birthday or family gathering. [Fania album description](https://fania.com/es/eras/willie-colon-and-ruben-blades-siembra/). | Plástico; Buscando Guayaba; Pedro Navaja. |
| 8 | **Metallica — Master of Puppets (1986)** | Guitar-driven intensity and aggression, structural and tempo contrasts, plus an instrumental track. Tests whether the planner can distinguish high energy from a party-ready groove. [Artist discography](https://www.metallica.com/releases/albums/?srule=old-to-new). | Battery; Welcome Home (Sanitarium); Orion. |

### Pass 2 — broaden the remaining scenes and challenge the descriptors

| Priority | Exact album | Additional coverage |
|---|---|---|
| 9 | **Hiroshi Yoshimura — GREEN (1986; original mix, Light in the Attic reissue)** | Environmental ambient, unhurried electronic textures and low rhythmic density. Electronic-family counts could rise while perceptual diversity improves substantially: this is why parent-family uniformity alone is insufficient. Try CREEK, SLEEP and GREEN. [Label description and digital edition](https://lightintheattic.net/products/green). |
| 10 | **Arvo Pärt — Alina (1999, ECM New Series)** | Sparse contemporary classical piano/strings, sustained quiet and flexible phrasing. Useful for contemplation and quiet focus. A single dance-tempo value may be musically meaningless; keep absence of a stable beat distinct from analysis failure. Specify the ECM recording featuring Spivakov, Bezrodny, Schwalke and Malter. [ECM recording](https://ecmrecords.com/product/arvo-part-alina-vladimir-spivakov-sergej-bezrodny-dietmar-schwalke-alexander-malter/). |
| 11 | **Joni Mitchell — Blue (1971)** | A second acoustic singer-songwriter voice with emotional and rhythmic variety. Tests sadness, vulnerability and brighter motion within one album, rather than labeling every track “sad.” Try River, A Case of You and Carey. [Artist album page](https://jonimitchell.com/music/album.cfm?id=5). |
| 12 | **Ali Farka Touré & Toumani Diabaté — In the Heart of the Moon (2005)** | Malian guitar/kora interplay and acoustic musical traditions beyond Europe and the Americas. Useful for warm instrumental social listening and intricate pulse without club percussion. Try Debe, Kaira and Mamadou Boutiquier. [Album reference](https://en.wikipedia.org/wiki/In_the_Heart_of_the_Moon), [label context for the duo](https://www.nonesuch.com/media/toumani-diabate/all-media). |
| 13 | **Nina Simone — Pastel Blues (1965)** | Piano-led vocal jazz/blues, mournful ballads and the much more forceful Sinnerman. A valuable within-album emotional contrast; do not reduce the historical content of Strange Fruit to generic breakup music. [Album description and track list](https://www.qobuz.com/us-en/album/pastel-blues-nina-simone/fp5icxzy75cua). |
| 14 | **Little Simz — Sometimes I Might Be Introvert (2021)** | Modern UK hip-hop, personal reflection and larger-scale arrangements. Expands beyond the current handful of hip-hop-primary tracks. Try Introvert, Woman and I Love You, I Hate You; flag spoken interludes separately when judging full-song playlist usefulness. [Artist interview](https://pitchfork.com/features/moodboard/little-simz-sometimes-i-might-be-introvert-interview/), [artist album stream](https://soundcloud.com/littlesimz/sets/sometimes-i-might-be-introvert). |

If adding only four albums now, choose **Pink Moon, Baduizm, Kaya and Waltz for Debby**. For your beach example specifically, compare **Kaya, Getz/Gilberto and Siembra**: relaxed buoyancy, light acoustic ease, and active dancing are different desired scenes. None should be assumed to satisfy Grecia or Manuel without a listening judgment.

## What “more uniform” should mean here

### A useful library, not uniform classifier numbers

I recommend broadening audible genre, pulse, instrumentation, emotional character and use case together. Do not normalize independent MAEST scores into exclusive shares, require equal counts in all 519 labels, or chase 25 tracks in every mood-score quartile. A model can be systematically compressed or miscalibrated; curating to its output alone would bake that bias into the library.

**First practical milestone:** reduce Electronic-primary dominance toward 40% of genre-measured tracks while filling the empty families. With today's 69/88, at least **85 additional non-Electronic-primary tracks** would be needed to reach ≤40%, if existing classifications stay fixed and every addition is measurable and non-Electronic-primary. For ≤35%, the same hypothetical calculation requires 110. These are planning arithmetic, not promised album outcomes: GREEN may be Electronic, jazz/bossa can cross families, and the 21 current unknowns will change the denominator when resolved.

For the next selection of about 100 new full songs, use these **proposed listening categories** as a starting allocation: 15 folk/singer-songwriter, 15 jazz/bossa, 15 soul/R&B/blues, 10 roots reggae, 15 Latin acoustic/social dance, 10 rock/metal, 10 ambient/classical and 10 hip-hop. They are human curation buckets, deliberately separate from MAEST parents, and they need not dictate which complete albums you keep. With whole albums, measure the resulting mix and adjust the following batch rather than trimming good songs just to hit quotas.

For tempo, aim initially for at least 15–20 **listening-verified** examples below 90 BPM and another 20 around 90–120, while retaining existing faster material. Treat these as reference coverage goals, not album BPM claims. Add free-tempo/beatless references as a separate category rather than inventing BPM values for them. Do not automatically fold every value above 160 in half; many fast tracks are genuinely fast.

### Evaluate the combinations that creative prompts need

Keep a small human-reviewed reference set with multiple artists per category. Include contrasts such as:

- Calm + warm + sociable outdoors versus calm + intimate + late-night.
- Sad + low energy versus sad + propulsive/cathartic.
- Happy + gentle versus happy + celebratory.
- Energetic + danceable versus energetic + aggressive/listening-focused.
- Instrumental + acoustic versus instrumental + electronic.
- Slow pulse + tense versus slow pulse + reassuring.

The four current mood heads cannot represent all these differences. More music gives the engine alternatives, but does not by itself solve the scene-understanding issue exposed by Listen Over the Ocean. Preserve Manuel's and Grecia's separate judgments rather than averaging them into a universal “beach” label.

## Next workflow

1. Resolve which of the 17 unanalyzed tracks and nine partial analyses should be completed, reusing compatible saved results first. Current failures include four missing MAEST outputs and seven missing rhythm outputs, with two tracks missing both. That may reveal additional existing coverage before acquiring anything.
2. Add Pass 1 albums as authorized local audio, deduplicate exact audio hashes and retain artist/album/edition information. No acquisition or new inference is authorized or executed by this audit alone.
3. After the owner selects the new analysis batch, process it through the established bounded workflow, then rerun this audit with known denominators and missing values.
4. Listen to contrasting examples and record scene fit, perceived pulse and model disagreement. If an obviously mournful reference still receives low sad support, investigate the descriptor rather than discarding the song to improve the chart.
5. Add Pass 2 and reassess. Also count artists/albums and listening minutes once an identity-backed export is available, because one short interlude and a ten-minute composition currently count equally.

## Technical interpretation references

- [Feature-to-catalog mapping](../../src/prompt_to_playlist/feature_catalog.py): independent soft descriptors and provisional arousal mapping.
- [Analysis table formatting](../../../web-player/src/features.js): displayed precision and available feature rows.
- [Library deduplication](../../../web-player/src/model.js): unique audio identity handling.
- [Audio feature policy](../AUDIO_FEATURES.md): model identities and evidence status.
- [Chrome recovery evidence](../../../web-player/docs/LIBRARY_RECOVERY.md): why disk inventory and browser library are separate populations.

This report does not change model policy, runtime ranking, saved user feedback, the browser library or release status.
