# Local discovery and player refinement — 2026-10-03

Ready on **http://127.0.0.1:4174/**. This revision remains local; no deployment, AWS change, audio change, analysis or paid PlaylistIQ request. The shared-profile implementation and deployment requirements in [SINGLE_USER_PROFILE.md](SINGLE_USER_PROFILE.md) remain applicable. Earlier screenshots describe previous layouts.

## Delivered behavior

- The expanded mobile spectrum grows from 33.333dvh to 41.667dvh (1.25×), still starting at 12.5dvh. Its canvas spans the screen, with symmetric 36px plot margins: the visualization itself is centered, independently of axis labels.
- Love and Add to playlist are 29px icons with accessible labels and 48px targets. Their row sits directly above the enlarged transport. Title/artist occupy the center of the intervening space, with a 16px gap. Play/pause is 76px, previous/next glyphs 30px and timeline timestamps 15px.
- Seek activity has separate state. The deliberate-pause quote requires explicit pause intent; seeking suppresses it. Status text has a fixed position outside the transport layout, so temporary buffering/status changes cannot push the buttons or timeline upward. External interruptions remain actionable and no seek introduces forced autoplay. Native iOS audio routing remains unchanged.
- The queue is a floating lower sheet: top 25dvh, height 75dvh. Existing eased opening/closing and downward drag dismissal remain.
- The Playlist/+ header row is removed. Queue is the rightmost control in the tabs row; duplicate queue controls and the empty desktop bar are removed. Playlists retains its Create playlist action but no longer shows Your prompts / Listening habits. Those remain in PlaylistIQ.
- Track cards place the heart below the ellipsis. Ellipsis opens five character-bank matches immediately, with three-decimal cosine values aligned right. No second Love control or collapsed audio-features section in that dialog. Add to playlist remains available.

## Discovery and habits

`src/discovery.js` defines one initial randomized library permutation per full page load. Search, filters, Love toggles and profile refreshes reuse that permutation; they do not scramble the list under a listener. Sort By includes Random order, and explicit title/BPM/etc. sorts override it. Saved playlist order and ranked PlaylistIQ results retain their original semantics. The last first-track ID prevents the next page load from starting with that same track when alternatives exist. Logging in loads a fresh page and follows the same behavior.

The example bank contains **50 unique prompts: 10 writing styles × 5 examples**: Scene, Activity, Feeling, Texture, Genre, Specific brief, Journey, Minimal, Poetic and Conversational. Two examples from different styles are selected on each new page, excluding both previous examples. The pair remains stable while navigating in that page. They appear in the existing large gray placeholder style; nothing is automatically submitted.

Listening habits adds library exploration/unheard count, return listens, average observed listening time per started play, listened-completion rate, time heard from PlaylistIQ requests, most-heard keys and most-heard saved playlists. All derive from the already persisted aggregates and catalog metadata. No new collection process, cloud service or write type is added. Exploration means some observed progress; return listens count additional qualifying listens (30 seconds or half a short track), not unique new tracks. BPM/key/genre summaries retain the limitations of their estimated features.

## Verification

- **165 web tests pass**, including bank cardinality/uniqueness, distinct styles and refresh pairs, stable filtered random order, old first-track avoidance, seek intent and no-op seeking, immediate cosine details, derived habits, and existing persistence/playback tests.
- **81 JavaScript modules** pass syntax checks. Web build contains **44 static files**, no source audio.
- In-app Chromium: 393×852 and 320×800 mobile layouts and 1280×900 desktop; no document-width overflow. At 393×852, visualization y=106.5/h=355; title block center≈544.7; icons y=630; transport y=680; queue y=213/h=639. Seeking to 5:19 kept audio playing, status empty and transport at y=680. Explicit pause displayed its quote without moving transport.
- Reload changed the first library track and prompt pair; all 186 distinct recordings remained. Five ordered cosine details displayed immediately. Playlist page no longer contains profile links. Updated listening statistics rendered from existing saved history.
- Physical iPhone touch/background playback was not tested. Responsive Chromium does not establish iOS behavior.

Evidence: `output/web-refresh/third-verification.json`, `third-mobile-player.jpg`, `third-mobile-library.jpg`, `third-queue.jpg`. Old packaging-validation candidates do not contain this latest frontend; regenerate through the maintained workflow only after publication approval.
