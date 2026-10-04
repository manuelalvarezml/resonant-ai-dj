# Web refresh — local review, 2026-10-03

> Latest continuation: [Shared listener profile and player polish](SINGLE_USER_PROFILE.md). This now adds durable saves and an API/routes/IAM update to the publication scope. Earlier frontend-only handoff below is historical. Nothing in this revision is deployed.

Status: implemented and verified locally at http://127.0.0.1:4174. **Not deployed.** The owner explicitly asked to review the local web edition before confirmation. That instruction controls over the pasted background-audio prompt's deployment sentence. The published website continues to serve the preceding release.

## Second refinement — full-screen player and concise web presentation

The owner's follow-up is implemented locally on 4174. This supersedes the first refresh's partial-height player and visible Close control. Production remains unchanged pending confirmation.

- Expanded mobile player fills `100dvh` edge to edge, with safe-area spacing. Pull down anywhere on the sheet to minimize; Escape remains available to keyboard users. Horizontal seek gestures remain separate. The app behind the expanded player is inert and keyboard focus stays in the sheet.
- Mini-player title/artist follow the finger and preview the adjacent song, clipped inside a dedicated text viewport. Track changes happen after a short transform transition. Boundary resistance, repeat-all, canceled gestures and reduced-motion preferences are handled. Text is larger and shifted slightly right.
- The 24-bar mini spectrum shares the existing desktop FFT analysis/timer. The web frequency range is 20 Hz–20 kHz, capped by sample rate; symmetric plot margins center the actual visualization independently of Y-axis labels. There is no visible spectrum caption. The owner edition retains its original frequency defaults.
- On iOS, both displays remain native-audio **progress indicators**, not FFT: reintroducing a live analyser on the audible media element would restore the background-playback dependency. Native dots now repaint on media/visibility/resize events, without a continuous animation loop.
- Library cards use a single keyboard-accessible button across title, artist and facts. Separate per-row play buttons and Analyzed labels are absent. Cards show at most three genres, BPM, selected key and the highest-scoring Musical character label, without the cosine number. Favorite/options controls remain independent. The mobile toolbar uses aligned two-row spacing and a compact Filter button.
- Queue shows the current occurrence first, with a slightly larger title, followed only by upcoming songs. Previous entries and large artwork are absent. A downward pull from the top of the queue closes it; ordinary scrolling remains available. Mouse/pen dragging supports desktop device previews too.
- Web PlaylistIQ explanations contain two paragraphs, occasion/activity/recipient/emotional aim and an arithmetic contribution table. Raw source tags and JSON are absent. Assumptions, limitations and a maximum-ten-item plan summary follow the results; the estimator sliders icon is last. The summary preserves exclusions and ordering. Planner evidence-gap explanations remain available in the limitations section. No inference, ranking or score was changed.
- Playback and job statuses use short ironic lines while retaining actionable error/interruption information.

### Final refinement verification

- **143 tests pass; 72 JavaScript modules pass syntax; 38-file web build passes.** The temporary synthetic presentation fixture was removed before the build. Build-manifest hashes and local imports were checked.
- In-app Chromium browser: 393×852 and 320×800 responsive layouts, real local track playback from the genre area of a full card, left/right track changes, full-screen geometry exactly `(0,0,393,852)`, pull-to-minimize from the plot and track text, current-first queue and pull-to-close, visible pause status, mini FFT, desktop 1440×960 layout and zero captured warning/error logs. Browser gestures used native mouse dragging, not physical touch.
- PlaylistIQ result rendering was visually checked at 393px and 320px using a clearly labeled synthetic result through the same presentation module. No paid request was sent. The final score table keeps numbers/headers intact at 320px. Result count, two-paragraph rendering, human context, limitations and exclusions have deterministic tests.
- Evidence: `output/web-refresh/refinement-library.jpg`, `refinement-player.jpg`, `refinement-queue.jpg`, `refinement-iq-fixture.jpg`, and `refinement-verification.json` at project root. The original first-refresh screenshots below are historical.
- Real iPhone touch feel, native progress rendering, lock-screen audio, interruptions and background next-track advancement remain owner device acceptance. A desktop viewport does not verify iOS. No cloud mutation, password activation, audio edit/upload, analysis or paid model call occurred.

## Delivered in the first refresh

- Library contains 186 distinct encoded recordings from the existing 187 fully analyzed MP3 files. The Library information button, Analysis and Inside Resonant tabs are removed in web mode. Your library becomes Library. Owner edition navigation and analysis stay available.
- PlaylistIQ candidates, rendered matches, playback queues and saved results remove repeated recording identities while preserving first-ranked order. Existing favorites and playlist references are remapped to the retained recording without erasing unknown IDs. The estimator pipeline, ranking weights and audio features are unchanged.
- Mobile navigation has the same brand / tabs / Playlist + and queue rows on every route. Search, Play all and shuffle precede Filter, sort and direction. The duplicate heading and Features button are hidden.
- One persistent bottom mini player displays title, a smaller subdued artist and play/pause. Horizontal swipes request next/previous (previous switches tracks even beyond three seconds); tapping opens the visualizer, transport and seek control. Closing returns to the mini player. Desktop keeps its existing player and FFT spectrum.
- PlaylistIQ uses a large transparent prompt editor with the native text caret and a large accessible Find tracks button. Candidate selector, analyzed count, coverage paragraph and listening lab are absent. Estimators are collapsed into a small lower-right disclosure.
- DJ mixes has one copy, numbered song names, transparent numbered transition links at 3:23 and 6:47, and “Each blend lasts about 30 seconds.” Links seek to the exact fractional start and start playback. No audio was edited or rendered.

## Duplicate evidence

All 187 encoded MP3 audio streams were hashed with ffmpeg stream copy (`-map 0:a:0 -c:a copy -f hash -hash sha256 -`). This does not decode audio or run inference. There were 186 unique packet hashes. Exactly one pair, Violet Eves / Listen Over the Ocean, had identical encoded audio despite different complete-file hashes:

- Retained identity: `b23cf7fc573254db349ab179fdcc406c5da159186b04b1fe914ff913d83e4ae2`.
- Equivalent file: `4d1b398a896faa64804dea2b7ccdc59ac416be35b23bbe84b90e9f1b42d25e24`.
- Shared packet hash: `68b3a6b887791dd18f89e661e6c424843c32d10c4b3d4a63532e41a677702174`.

`src/recording-identity.js` records only this proven cloud alias; titles are never used to merge distinct versions. The immutable catalog and source files retain all 187 records/files; the web candidate/display layer uses 186. Future imports require a fresh stream audit. This check does not claim to identify alternate encodings of the same performance.

Private receipt: `output/web-refresh/full-audio-identity-audit.json` (project root). No source audio, analysis caches or immutable release files were altered.

## Background playback investigation and fix

Inspection confirmed two hazards in the old app: its visualizer attached `createMediaElementSource` to the audible element and depended on AudioContext output; its `pagehide` callback cleared the queue and audio source. These are confirmed code paths, not a confirmed reproduction of this owner's iOS symptom.

The web edition now leaves playback intact on pagehide and hidden visibility. On iPhone/iPad it never attaches the audible element to Web Audio. The same native audio element handles tracks and next-track advancement. Visible pageshow/visibilitychange reconciles paused media without forcing playback. External pauses clear play intent, update the button/Media Session and expose an interruption message; queued stale pause events cannot cancel new playback. Desktop uses the existing FFT graph.

**Visualization tradeoff:** iOS shows playback-progress dots, explicitly labeled as progress. These are driven by the native media position and are not a fabricated live frequency spectrum. Desktop and desktop Chrome at mobile width keep the real live spectrum. Device-size emulation alone does not emulate WebKit or lock-screen policy.

Sources reviewed:

- [Spotify Now Playing](https://support.spotify.com/vn-en/article/now-playing/) and [Play Queue](https://support.spotify.com/us/article/play-queue/): persistent playback controls and expanded now-playing/queue interaction. Typography and layout here are our implementation, not claimed exact Spotify specifications.
- [WebKit 261554](https://bugs.webkit.org/show_bug.cgi?id=261554) and [237878](https://bugs.webkit.org/show_bug.cgi?id=237878): background AudioContext problems.
- [WebKit 323104](https://bugs.webkit.org/show_bug.cgi?id=323104): reported silent playback while media APIs advance. Avoiding Web Audio removes our known dependency but cannot prove that the operating system will never interrupt sound.
- [Apple HTML5 audio guide](https://developer.apple.com/library/archive/documentation/AudioVideo/Conceptual/Using_HTML5_Audio_Video/): native media playback behavior.

No physical iPhone test was performed. If iOS reports playing while output is silently lost, the page cannot reliably infer actual speaker output from currentTime alone. No automatic replay loop or invented playback-success claim was introduced.

## Password and deployment handoff

The owner-requested replacement password is staged in ignored, mode-600 files:

- `output/web-refresh/password-rotation/listener-password.txt`
- `output/web-refresh/password-rotation/password-hash.json` (bcrypt cost 12; intended parameter `/resonant/first-release/password-hash`)

No live SSM value or active password file was replaced. Local 4174 remains the existing unauthenticated loopback preview; the password applies to cloud login after approved rotation. Do not commit the password or hash to source, copy it into frontend assets, or overwrite the active deployment tuple during review.

After explicit approval: use the existing [serverless runbook](../../../deploy/serverless/RUNBOOK.md) and [live checkpoint](../../../docs/cloud-library/first-release/serverless/LIVE_ROLLOUT.md). `deploy/serverless/export-static.mjs` reads current frontend source while preserving the frozen audio release. Create a new candidate output directory, publish/version the frontend through that workflow, retain protected library/media behaviors and login redirect, rotate the staged server-side password, and repeat auth/range/login smoke checks. No worker rebuild, new analysis or audio upload is needed for these UI changes. Do not blindly reuse an old app upload plan.

## First-refresh verification (historical)

- `npm test`: **135 passed, zero failed**. Covers distinct recording preservation, legacy alias references, ranked deduplication and queue, native pauses/resume, stale pause race, foreground reconciliation, ended advancement, swipe decisions and lifecycle preservation.
- `npm run check`: **70 JavaScript modules** passed syntax validation.
- `npm run build:web`: **37 files**, no source audio. Manifest hashes, relative module imports, web config and absence of private paths/password/key markers checked. Receipt: `output/web-refresh/verification.json`.
- Initial sandbox test run had four `listen EPERM` failures in loopback HTTP tests; the complete suite passed with loopback permission. No unresolved assertion failure.
- Chrome on macOS: 186 rows; desktop at 1680px; mobile CSS viewports 393×852, 390×844 and 320×800; document widths matched viewports. Persistent mini player, expanded real FFT at desktop mobile width, play/pause, queue opening, prompt typing, and transition seeks around 203.8s and 407.5s observed. No browser warning/error logs in the checked session. Browser zoom was accounted for using measured CSS dimensions.
- Screenshots: `output/web-refresh/mobile-library.jpg`, `mobile-player.jpg`, `mobile-playlistiq.jpg`.
- Real touch swipes, iOS native progress dots, background audio, lock-screen controls and background next-track advancement remain physical-device acceptance. No paid PlaylistIQ request was needed or sent for this frontend regression check.

## Short iPhone checklist after approved publication

1. Refresh the deployed page, log in with the new password, play a track and tap its bottom bar. Check title/artist, pause, swipe both directions and progress dots.
2. Play continuously; lock the phone for at least two minutes, then repeat while using another app. Confirm audible playback, not only an advancing timer.
3. Seek near the end, lock the screen and listen through the next track. Check lock-screen pause/resume/next and verify the displayed song changes.
4. Interrupt with another audio app or a call. Return to Resonant and confirm its playback state matches the actual sound and Play resumes correctly. Test Safari and Chrome separately; record device/iOS/browser and whether wired/Bluetooth output was used.

The currently published site does not yet include this fix. The owner can review appearance now on local 4174 using the iPhone 14 Pro DevTools preset; hardware acceptance follows publication approval.
