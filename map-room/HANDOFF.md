# Map Room Handoff

Between the Campaign Series: The Map Room chat (cloud) and Map Room Desktop (Claude Code on Brian's desktop). Each side pulls main before starting and after the other pushes. Only one side edits a file at a time.

## Requests
Written by the Map Room chat: what to build or fix and why, one item each, dated.

* **21 Nov 2026, handover (no build needed).** The balcony key card landed in 07e9e2f (`engine/keycard.py`, its hook in `engine/zoomclip.py`, `keyDays` in `series/bulge-1944/series.json`; rules in `FORMAT.md`, The key card). From here all engine code is yours. Two things to know: (1) it was only seen at 32 samples here, so please look at it in the first full render of Days 1 to 3; (2) on the test series it shrank to 80% and sat just above the strip, because nothing at full size cleared every block in the top band under the tab. If it looks too small on a phone at full quality, tell this chat and we'll decide between a smaller card and a looser clearance.

* **21 Nov 2026, checker: accept the next day's map as the source for a night table.** The situation maps were drawn at noon, so a day's night positions first appear on the next day's map (found in the blind read test: the 26 Dec map still shows 4th Armored south of the line it crossed that afternoon). `FORMAT.md` now says a day's `map`, and the sources for its `line`, `moves` and `shifts`, normally name the **next** day's map. `check_series.py` still requires the day's own map in three places (the `map` field must equal the day's own label, and `sourced()` checks for it in line, move, shift and set sources). Please change it to accept the map for the day itself or the day after (both must be listed in `series.json`; `set` and `lineStart` on Day 1 stay on the day's own map), and keep the test series passing. Needed before the Bulge sitting starts Thu 26 Nov, since the Campaign Series chat runs the checker there.

## Done
Written by the desktop: what changed, the commit, where the test clip is.

* **21 Nov 2026, Ops room ambience in the repo, no more silent fallback.** The `*.wav` rule in `map-room/.gitignore` had kept `kit/sound/declass_ambience_ops_room_v02.wav` out of git, so every clip fell back to the teletype bed (the clicking in the intro). The file is now tracked (`!kit/sound/*.wav`; render WAVs stay ignored), and a missing file stops the render with a clear error. Level unchanged: the old bed's RMS, about 18 dB under the theme. Commits e5d1677, cac4ef8, 69226de. Test clip: OneDrive, The Map Room\Desktop Render Test 2026-11-21\ops-room-bed\day-11-strict\day-11.mp4.
* **21 Nov 2026, each day's sound seeded by its day.** `maproom_sound.build(seed=day)`, passed by zoomclip.py and render_day.py. A day now sounds the same rendered alone or in a series (proved byte identical). Every clip's sound changed once; pictures did not. Commit 5cc242d.
* **21 Nov 2026, bpy pinned and setup documented.** `map-room/requirements.txt` pins bpy 5.3.0 (Python 3.13); the README Setup section lists ffmpeg, Chrome and rsvg-convert, with Windows steps. The cloud should install from requirements.txt. Commit 43d6bf2. Also e3babaf: the render_series.py note now says quiet days get a balcony only clip.
