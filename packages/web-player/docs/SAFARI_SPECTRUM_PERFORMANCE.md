# Safari spectrum cadence fix — 2026-10-06

Status: implemented and verified locally; not published to resonant.lat. Physical iPhone 12 performance remains to be checked.

## Report and diagnosis

Owner reports low apparent frame rate in both the main and mini spectrum on Safari/iPhone 12, unlike Chrome mobile view. The original code capped both displays at 20 fps and reset its frame timestamp to each delivered callback. At 30 Hz callbacks, a 50 ms threshold accepts only every second callback: 15 fps. Callback jitter can also undershoot the intended cap. This is a reproducible scheduling issue, not proof of the owner's current device settings.

WebKit documents intentional 30 Hz animation callbacks in Low Power Mode and lower frame rates under load/heat. [WebKit explanation](https://bugs.webkit.org/show_bug.cgi?id=215745). Desktop Chrome device mode does not reproduce the actual phone's CPU or Safari runtime. [Chrome limitations](https://developer.chrome.com/docs/devtools/device-mode#limitations). Low Power Mode and which device ran Chrome were asked about; no answer was available during implementation. Do not label either as the confirmed root cause on this phone.

The native spectrum reads cached 10 Hz audio-derived magnitudes and interpolates them, rather than routing iOS playback through Web Audio. Interpolation improves animation continuity; it does not add new measured frequency frames. Reduce Motion deliberately selects 5 fps, unchanged by this fix.

## Changes

- Phase-preserving animation scheduling carries unused time forward, skips missed frames without catch-up bursts, and avoids the 30 Hz → 15 fps gate.
- Native recorded-spectrum presentation targets 30 fps for both canvases. Live Web Audio presentation retains its 20 fps target.
- History insertion remains nominally 20 slices/second, independently of painting, preserving the roughly 4.15-second falling history. The newest slice uses the current interpolated values.
- Fixed grain offsets are cached once when the textured main view first becomes visible. At full falling history this removes up to 47,808 sine/cosine evaluations per repaint, retaining point positions, density, dimensions and the existing capped retina resolution. Cache storage is approximately 374 KiB.
- Native audio routing, spectrum assets, source audio, pause easing, reduced-motion behavior, visibility suspension, ranking and cloud configuration are unchanged.

## Verification and limits

172 player tests pass. New tests cover 30/60/120 Hz callback sequences, 20 Hz history timing, 5 Hz reduced-motion timing and late callbacks. A mocked DOM/canvas integration test drives the real native rendering loop for two seconds at 30 Hz: both canvases paint 60 times, fixed grain trigonometry does not repeat, the collapsed main canvas does not repaint while the mini continues, hidden documents stop, and paused animation settles to idle. This proves scheduling/logic, not actual GPU paint speed or physical-device FPS.

The initial sandbox suite passed 167/171 tests; four existing HTTP tests could not bind loopback (EPERM). Their permitted rerun passed, and the final complete suite after the integration test passed 172/172. Syntax passes for 88 modules; local and web builds pass (50 and 48 static files); local manifest/private-material verification passes.

## Publication and device check

Only the frontend needs publication for this change; no API, worker image, audio or spectrum generation is required. Do not use a historical combined refresh to change unrelated runtime aliases merely for this patch. Keep immutable frontend assets, previous entry-pointer versions and rollback receipts. No publication occurred in this task.

After publication, compare the same track on the actual iPhone 12 with Low Power Mode on/off, noting Reduce Motion. Test expanded and mini displays, seek/skip, pause easing, background/lock-screen playback and return to foreground. Confirm the new asset identity before attributing a result to the patch. If it still stutters, capture actual callback intervals, media-time progression and canvas paint durations with Safari remote inspection; do not infer physical-device performance from desktop emulation.

## 2026-10-06 — Superseding account release

The owner subsequently authorized implementation and publication. [Account release](ACCOUNTS_RELEASE.md) adds a device-local full-animation override (the new default) and an option to follow OS Reduce Motion. The earlier 5 fps policy now applies only when Follow device Reduce Motion is selected. The timing/geometry optimization and native audio path are retained. See the account checkpoint for publication receipts; physical iPhone 12 FPS remains unmeasured.
