# Frontend options — 0.2.0

**0.2.1 — D062/E050:** Always-visible Option1/Option2 header buttons;
Radio is predominantly black/dark gray. Live switching preserves generated
playback; desktop/390/320 checks pass. Library information and exact0.1.2 snapshot
retained.13syntax/15HTTP checks pass; no provider scope changes in this revision.


## Compare

- **01 / Studio:** original gray Geist Mono front at `/?front=studio#demo`
  (the default `/` URL also selects Studio).
- **02 / Radio:** NTS-player-inspired alternative at `/?front=radio#demo`.

Use Library information → Front end to switch within the app. The switch moves
existing transport DOM and applies scoped CSS; the audio element and library
state remain in place by design. Opening a different URL/tab loads a new player
session. Browser-local music/playlists use the same origin/database in both.
Do not run two simultaneous sessions unless intentional.

Radio follows the user's [saved brief](NTS_PLAYER_BRIEF.txt) and
[NTS player reference](https://www.nts.live/): strong horizontal player, bold
sans-serif titles, monochrome surfaces, hard artwork edges, sparse hierarchy.
It uses system Arial/Helvetica, not a claim about NTS's proprietary typography.
There are no real radio channels, NTS feeds or copied artwork. Existing local
imports/generated demos, collections, shuffle/queue and evidence remain shared.

## Exact previous version

`checkpoints/option-1-0.1.2/` preserves the pre-change source, public assets,
scripts, tests, docs and package/handoff files. `snapshot.json` records34SHA-256
hashes. It excludes source audio, dependencies, secrets and generated dist.
Build it independently in a temporary directory using its existing npm scripts;
copy that checkpoint to a separate working directory before experimenting.
Archived Markdown links retain the original repository-relative context.
Never edit this checkpoint to match subsequent releases. It is not shipped or
served. Current Studio receives shared bug fixes; the snapshot is exact0.1.2.

## Implementation and verification

`src/radio.css` scopes every style to body.radio-layout. `src/app.js` reads the
front query, switches class/layout and replaces the URL without reloading.
Studio CSS/presentation remains default. Library information stays in place.
0.2.0 passes30tests,13syntax modules,15HTTP checks and two additional route/asset
responses.34archive hashes match. No new dependencies or provider services.
Browser interaction/responsive inspection was not run for this variant under
the current Sites workflow. Verify narrow layout and live switching in a future
explicit browser-QA request; do not inherit0.1.2 acceptance as Radio evidence.
