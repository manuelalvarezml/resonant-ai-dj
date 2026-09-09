# Product and market validation plan

## Segment hypothesis

Prioritize DJs with personally owned digital audio, a recurring crate-preparation workflow and a reason to listen away from the main workstation. Start with house/electronic preparation because that is the local engine's existing evidence boundary, while avoiding a claim that all electronic music has a reliable beat grid.

Secondary segment: personal collectors who manage local files and want private rediscovery. Do not combine its economics or priorities with DJs until interviews show similar behavior. A collector with 1TB of lossless recordings may value preservation while a DJ wants edits, cue points and fast preparation.

The product hypothesis is: a user can upload a selected crate, inspect trustworthy descriptors, audition it remotely and create a useful editable selection; eventually a validated, downloadable mix saves enough work to justify payment. Every clause can fail independently.

## Competitive landscape

| Alternative | Documented job served | Consequence for discovery |
|---|---|---|
| rekordbox | Cloud sync and DJ ecosystem integration | Test whether another library duplicates work; ask about existing subscription and cue/playlist fidelity |
| Lexicon | DJ library organization, smartlists and cross-application workflows | Trust, conversion and existing habits may outweigh new AI features |
| iBroadcast | Hosted personal music listening | Basic storage/playback has a low-priced substitute |
| Plexamp | Personal-server listening and discovery | Some collectors prefer control and will accept server setup |
| YouTube Music uploads | Private uploaded collection | Basic remote access alone may have low willingness to pay |
| Mixed In Key Mashup / DAW | User-directed tempo/key mixing and audio export | Compare result quality, editing effort and control, not only prompt novelty |
| Existing local workflow | Folders, existing DJ tools and manual mixes | “Do nothing” has no upload burden and is the strongest default alternative |

Sources: [rekordbox](https://rekordbox.com/en/feature/cloud/) S028; [Lexicon](https://www.lexicondj.com/manual/all) S030; [iBroadcast](https://www.ibroadcast.com/premium/) S031; [Plexamp](https://www.plex.tv/plexamp/) S032; [YouTube](https://support.google.com/youtubemusic/answer/9716522?hl=en) S033; [Mashup](https://mashup.mixedinkey.com/how-to-make-mashups/create-epic-mashups) S034. “Consequence” is analysis. No competitor absence claim means a feature was proven absent.

No credible narrow TAM was established. Use a bottom-up reachable-customer model after recruitment: reachable qualified prospects × activation × paid conversion × retained months × net revenue. Keep channel reach estimates separate from actual customers. Interview convenience samples cannot estimate the global population.

## Research sequence and sampling

EX001 proposes 15 DJ interviews and 5 collector interviews across at least two recruitment channels. These are discovery sample targets, not statistically representative samples. Record refusals and screen-outs so the results do not describe only enthusiastic early adopters. Capture country, DJ role, owned-file count/bytes, lossless share, monthly additions, upload speed, existing apps and paid subscriptions.

Do not recruit or contact anyone until outreach is explicitly authorized. The current task prepares interview materials and a record structure. Consent, contact details and recordings belong in restricted storage; public agent notes use participant IDs and anonymized evidence.

Use 30–45 minute sessions. Begin with recent behavior before demonstrating a concept. Ask:

1. Describe the last time you prepared a crate or mix. Which steps consumed time, and what did you actually deliver?
2. Show the organization method with private content hidden. Which information do you trust and correct?
3. How many files and bytes are in the collection? Where are the copies and backups?
4. What fails when you listen away from the main computer?
5. What did you last pay for to address this workflow? Why that product?
6. When did you last upload a large dataset? How long did it take, and what made you stop?
7. Which files must never leave your device? What would you need to trust deletion?
8. If one capability vanished—playback, descriptors, playlists or mixes—which loss would matter most?
9. What specific next-week task could you attempt with the proposed service?
10. What would make you decide against it?

Record spontaneous behavior separately from answers elicited after suggesting AI. Ask participants to rank value before presenting prices. Randomize proposed price anchors across interviews or cohorts, and record which anchor they saw. A hypothetical “yes” is weak evidence; a concrete follow-up task, authorized upload attempt and later paid retention are stronger.

## Proposed experiment gates

These thresholds are initial decision rules subject to an explicit pre-experiment steer, never retroactively adjusted to make a result pass.

| Gate | Proposed evidence | Failure interpretation |
|---|---|---|
| Repeated problem | At least 8/15 DJs describe a recurring relevant workflow and a concrete recent cost | Audience or job may be wrong |
| Concrete intent | At least 5/15 DJs agree to a dated follow-up using a selected crate | Demo interest is weak |
| Activation | At least 8/10 authorized pilot participants reach first playback and a saved crate | Onboarding or value proposition needs revision |
| Upload tolerance | At least 8/10 complete a selected-crate batch; report full-library intent separately | Consider selective-cloud or local-first product |
| Retention | At least 6/10 activated participants return for a real task in week two | First-use novelty may dominate |
| Paid signal | At least 5 eligible participants accept a real paid pilot at a price that covers scenario costs | Reprice, reduce costs or stop; do not infer willingness from free users |
| Differentiation | Users can identify a meaningful time/quality benefit against their actual alternative | A general library product may be undifferentiated |

All denominators, missing data and reasons for withdrawal must appear in the readout. These numbers cannot support a population conversion rate. A small paid pilot is a direction signal. The full build needs renewed review once larger cohorts expose storage and support tails.

## Proposed smallest supported workflow

Use desktop browser upload and responsive web playback. Choose one desktop Chromium version family first and explicitly test current Safari before promising it; decide mobile playback support from observed interviews and codec tests. A standalone mobile/desktop app, offline guarantee, background folder watching, public sharing, subscription-streaming imports and direct performance-deck integration remain deferred.

Flow specification:

1. Account creation explains private use, supported files, export/deletion and the current storage/job limits.
2. Select a crate. A local preview shows filenames, byte total and estimated upload time; it does not transmit files before the upload action.
3. Confirm import. Reserve quota, issue short-lived capabilities and begin bounded transfers.
4. Completed verified files appear progressively. Upload and analysis progress have separate states.
5. Browse title/artist plus evidenced descriptors. Unknown values remain unknown; filters can expose coverage.
6. Play a track privately; seek, retry an expired capability, then continue queue playback.
7. Propose a playlist only after that integration is authorized. Show interpreted required/preferred/excluded criteria, missing evidence and actual matches.
8. Save an editable selection tied to a catalog revision.
9. Later, separately authorized mix flow: inspect proposal, validate, show job cost/limits, confirm render, preview measured output, download the approved artifact.
10. Export or delete the library through visible account controls.

The mix button must be absent or explicitly unavailable while the feature is unapproved; do not simulate a successful render in the product.

## Textual user-flow prototype

| Screen/state | Required content | Available action | Failure/recovery |
|---|---|---|---|
| Empty library | Private storage explanation, supported formats, quota | Choose files | Reopen selection; no lost quota reservation |
| Import preview | Count, bytes, upload estimate, duplicate/unsupported summary | Start / remove files | Edit batch |
| Active upload | Per-file status, aggregate bytes, usable tracks | Pause / cancel / play completed file | Resume only missing parts or reselect unchanged source |
| Processing | Verified original plus pending metadata/analysis | Browse/play if eligible | Retry one recoverable file, retain rest |
| Library | Descriptor coverage, stable sorting, search, source/version | Filter / inspect / correct | Clear unsupported filters; show insufficient evidence |
| Playlist review | Original request, interpreted criteria, coverage gaps | Edit criteria / save selection | Clarify, never silently drop hard constraints |
| Mix review, future | Track sequence, warnings, duration, price/quota estimate | Confirm bounded job | Reject or revise plan |
| Job progress | Queued/running stage, cancellation | Cancel / leave page | Poll resumable job record |
| Result | Preview, loudness/peak status, plan and provenance | Download/export | Failed-quality result is not published as ready |
| Deletion/export | Scope and retention consequences | Request / inspect status | Retry idempotently; report completion evidence |

This is a low-fidelity specification, not an interactive usability test. Build an interactive prototype only under an explicit scope decision; fake data must be labeled.

## Evidence record and decision readout

Each interview/experiment record must include participant ID, consent scope, segment, geography, date, questions/version, observed behavior, direct anonymized evidence, interpretation, counterevidence and next action. Keep quotations short and permissioned. Mark missing measurements null.

At the readout, group by actual workflow and upload profile. Do not average a gigging DJ's urgent use with a collector's occasional listening. Decide whether to continue, pivot to selective-cloud preparation, remain local-first, or stop the cloud service. Record rejected alternatives with their reopening condition in registers.json.
