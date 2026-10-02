# Resonant design — 0.1.1

**0.2.1 — D062/E050:** Always-visible Option1/Option2 header buttons;
Radio is predominantly black/dark gray. Live switching preserves generated
playback; desktop/390/320 checks pass. Library information and exact0.1.2 snapshot
retained.13syntax/15HTTP checks pass; no provider scope changes in this revision.


**Option2 — Radio (D060):** Separate scoped radio.css provides bold system sans,
black horizontal player and off-white library. Studio remains default. Read
[frontend options](FRONTEND_OPTIONS.md); exact prior0.1.2 is preserved.


**R3 supersedes small-type guidance below:** All visible text is now at least16px;
track titles18px. Filler descriptions/eyebrows/breadcrumbs are removed or hidden.
Fixed app frame, independently scrollable Tracks region, sticky headings,
medium-size Shuffle action. Mobile prioritizes readable text with horizontal
nav and truncated long labels; no type shrinking to fit.


Reference: [Sustain IT](https://sustainit.space/), inspected 2026-09-12 in the
browser and through its actual stylesheet/computed styles. Most observed text
uses Geist Mono; its font stylesheet also requests Martian Mono 200. Observed
utility text is often 8–12px with light larger headings. This is a reference
for hierarchy and spacing, not a copy of its brand, illustrations or content.

Translation: concrete gray #202020 / #262626 / #303030, warm off-white #eeedea,
muted #b0afad, thin #484848 structural rules, square controls. One compact
masthead and playlist strip replace the former green sidebar. The collection
is open and roomy; the queue is a separate listening rail. Artwork is abstract
CSS geometry and track initials, not inferred album art or an audio waveform.

Geist Mono 200 is the display face; 400 is the utility/body face. Desktop heading
at1280px is56.32px, primary track text14px, controls roughly12.8px, compact
secondary text10.4–12px. Mobile heading40px (35.2px at320), track text12px;
secondary labels9.6–12px. This retains the reference's large-to-small contrast.
Native controls have explicit labels and focus rings. The duplicate demo hero/action strip was removed so the track list starts
inside the first desktop viewport; the description and playback status still
identify generated demo audio.

Fonts are **self-hosted**, unmodified Google Fonts Geist Mono TTFs at weights
200/400. License is bundled at [OFL.txt](../public/fonts/OFL.txt). Original font
metadata/license source: [Google Fonts Geist Mono](https://github.com/google/fonts/tree/main/ofl/geistmono).
Assets were obtained via the Google Fonts CSS API for Geist Mono (weights200–600),
then only the two needed files were retained. No runtime Google request exists.
Fallback: ui-monospace/monospace. Font-display swap keeps text available while
local fonts load; preload reduces the initial font swap.

Keep styles in src/styles.css. Do not add framework dependencies or copied
reference-site assets to restyle this package. Preserve all playback/adapter
state contracts. Test desktop and narrow widths after typography/layout edits.
See [REDESIGN_PLAN.md](REDESIGN_PLAN.md) and [VERIFICATION.md](VERIFICATION.md)
for exact stage, observations and limitations.

## Future playlist action hierarchy — D058

Play, pause, edit/order and add-track actions remain primary. Whole-playlist
audio download is useful but occasional, so expose **Download playlist files**
inside the playlist ellipsis / More options menu—not as a large toolbar button.
Its dialog shows eligible and unavailable tracks, order, total bytes, archive
contents and expiry before confirmation. Keep JSON export and continuous-mix
rendering as separately named actions. This specifies future service UX only;
the verified0.1.1 build still exports playlist JSON, not audio.
