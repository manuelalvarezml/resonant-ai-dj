# Web refinement — 2026-10-04

Status: **published on October 4** with the subsequent muted-green/15% tab refinement and 1.6-second mini-spectrum pause easing. See [production release and acceptance](../../../docs/cloud-library/first-release/serverless/HISTORY_SPECTRUM_RELEASE.md). The sections below preserve the preceding local review evidence.

## Delivered

- Navigation: PlaylistIQ, LIBRARY, PLAYLISTS, DJ MIXES. PlaylistIQ is 8% larger, mixed case, muted champagne. Removed duplicate collection headings, Title header and floating track count. Mobile search/filter controls are 15% shorter; stacked ellipsis/heart leave musical facts aligned right.
- Liked Songs is always present in Playlists, including zero likes, derived directly from the durable existing favorites. No second copy of the like state or extra service.
- Expanded player opens over 780 ms and closes over 660 ms, with reduced-motion accommodation. Dragging smoothly introduces up to 42 px corner rounding; the settled player remains full screen. Queue uses matching slow motion, occupies the lower 75% of the viewport and closes on outside clicks/tab navigation.
- Find tracks uses an arrow and hover/focus movement instead of a bottom border. The two rotating examples retain their style; a separate short invitation reads “Or surprise us. We’ve heard worse.” Textarea grows with its content on browsers supporting field sizing.
- Your prompts / Listening habits sit at the bottom left of PlaylistIQ, with the estimator icon at right. The icon opens a themed options list immediately with a noninteractive Feature estimators heading. Mix Transitions is styled as a heading with no colon.
- Prompt cards open their saved tracks inside the same dialog. Selecting a track starts that result queue at the chosen position, switches off shuffle for faithful order, and keeps the dialog open. Closing clears content and stale focus; closed dialogs are explicitly removed from layout.
- New completed requests save bounded human-readable interpretation/context and up to five score contributions per match. Existing track selections remain playable. Missing older explanations are explicitly identified instead of invented. Pause text is 10% larger and the mini spectrum becomes a line of dots when paused.

## Visualization diagnosis and repair

The iPhone path intentionally used `attachPlaybackDots` after the earlier background-audio fix. That code filled a grid using currentTime/duration, and its mini visualization was also progress. Chrome's iPhone emulation uses the same UA-based branch. This explains the exact reported matrix; restarting could change the device/branch being viewed, but could not turn that fallback into a spectrum.

Removed both progress renderers. Desktop retains the live Web Audio FFT. Native iPhone playback now uses real, locally precomputed frequency magnitudes with the same visual renderer, synchronized to the HTML audio element's currentTime, including seeks. The native branch never calls createMediaElementSource. It is an audio-derived visualization, not a live measurement of the phone's output.

`packages/web-player/scripts/build-spectra.py` reads the frozen sources with FFmpeg and computes 96 logarithmic bands, 20 Hz–20 kHz, at 10 frames/s using an 8192-point Blackman FFT. No ML analyzers run and no audio is modified. Generated 188 files (187 frozen MP3s plus the mix), 65,289,047 bytes, under `output/display-spectra/v1/`. The deduplicated visible library remains 186 recordings. The browser interpolates frames, draws at at most 20 fps, caches at most three tracks and stops drawing when hidden. Missing display data leaves native playback intact; it never substitutes progress for a spectrum.

Relevant platform context: [MDN media-element routing](https://developer.mozilla.org/en-US/docs/Web/API/AudioContext/createMediaElementSource), [WebKit background suspension](https://bugs.webkit.org/show_bug.cgi?id=261554), and [native versus Web Audio background behavior](https://bugs.webkit.org/show_bug.cgi?id=263627). These reports support preserving native playback; they are not physical-device verification of this implementation.

## Evidence

- 168 web tests passed, 22 API/edge tests passed; syntax check covers 85 modules; web build contains 47 static files. Logs: `output/web-refresh/fourth-tests.txt` and `fourth-api-tests.txt`.
- New tests cover frame/seek mapping, corrupt spectrum rejection, saved prompt evidence round-trip/escaping/membership and legacy prompt preservation.
- Independent generated two-tone check: 220 Hz and 4000 Hz tones yielded peak bands at 220.36 and 4039.18 Hz, respectively, across 20 frames. No library source modified.
- Chrome at 393×852: native branch forced with `?spectrum=recorded`; visibly changing real spectrum, paused dots, fullscreen geometry, curved drag dismissal, saved history playback, no prior tracks in selected-result queue, outside queue dismissal, Liked Songs add/remove, footer/menu and dialog cleanup verified. A 320 px layout has no document/nav/footer horizontal overflow. Desktop live FFT also rendered; viewport override reset afterward.
- Mid-animation geometry observed for both sheets, confirming entry frames rather than instant appearance. Player drag observed 36.88 px top corner radius at 200 px displacement, then returned to miniplayer.
- Production read-only audit found **three completed prompt records, each with ten track IDs**, so no reset or deletion was performed. Those records do not contain saved explanation snapshots. Local history has an additional older three-track request used for playback verification. Local test likes were restored; local listening counters naturally include these test plays.
- Screenshots: `output/web-refresh/fourth-native-spectrum.png`, `fourth-playlistiq-mobile.png`.
- No paid AI calls, cloud writes, source-audio edits, commits or push this turn. The spectrum file generation is display preprocessing only.

## Deployment continuation after approval

This update requires frontend **and API profile-model** publication, plus private spectrum assets. Do not publish frontend alone and assume new explanation snapshots will be stored by the old API.

An offline candidate is prepared at `output/web-refresh/history-spectrum/candidate/`: 437 upload-plan entries, app ID `d3845468713b5b37ba4903a17dcea4f890671f14f1cbcddd0619a4c6da6d2b6b`. Export verified the frozen release and spectrum source hashes, including the mix. No uploads have occurred. Existing audio is referenced, not recopied.

The refresh helper now accepts `--work-dir output/web-refresh/history-spectrum`; use it consistently for this rollout so October 3 rollback evidence and its old candidate are not reused. Staging permits **new** `library/spectra/v1/*.json` objects while preserving refusal to overwrite mismatched library/audio objects, including existing spectra. CloudFront already authenticates the library path. The standard prepare/stage/runtime/publish/acceptance workflow still applies; API packaging and cloud stages remain pending.

After authorized publication, test on the actual iPhone: play/seek/skip with the spectrum open; pause/minimize and inspect dots; lock screen and switch apps; verify next-track continuation, then reopen. Test sheet swipes and prompt-result queues. Browser checks cannot establish physical iPhone background reliability.
