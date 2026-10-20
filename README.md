# WW2 Dispatches cards

Post card images for WW2 Dispatches, a World War II this day in history account. Images are hosted here for scheduled posts on X, Instagram, Threads, and Facebook (all through Buffer). Videos live in the separate repo ww2dispatches/ww2dispatches-videos.

Two scheduled runs fill each Sunday to Saturday week: Thursday 7:47 p.m. Mountain writes and schedules the 14 cards, and Friday 7:47 p.m. builds and schedules the 7 noon videos, records live links, and drafts the newsletter. Saturday 6:13 a.m. prepares the Name This cards. The full rules live in the claude.ai Project docs: Project Brief (the hub), Roadmap, Cards, Videos, Newsletter, Name This, and Queue Status.

## Layout
* `cards/` finished images, one pair per dispatch: `dispatch-NNN-x.jpg` (1600 x 1440) and `dispatch-NNN-instagram.jpg` (1080 x 1350). These are the files Buffer links to.
* `dispatches/` one JSON file per dispatch: number, date, place, series, pull line, caption, photo framing, and sources.
* `photos/` the public domain source photos.
* `renderer/` the card renderer, a copy of the Dispatch Press drawing code run in headless Chromium, plus the video, story, slide, Name This, series log, and Living Press scripts.
* `stories/` Story Card scripts, `kits/` Video Press Kits, `log/` the series log (rebuilt by `renderer/series_log.py`, never edited by hand), `newsletter/` weekly issue drafts.
* `archive/` retired files (the Grok scout and the old Facebook queue). Not used; do not edit.

## Rendering
```
python3 renderer/fetch_photo.py "<Wikimedia Commons file page URL>" photos/<id>.jpg
node renderer/render.js            # every dispatch
node renderer/render.js <id> ...   # just these
```
Framing fields in a dispatch file work like the Dispatch Press sliders: `focusX` and `focusY` (0 to 100, default 50 and 40) and `zoom` (100 to 200).

Public link pattern: `https://raw.githubusercontent.com/ww2dispatches/ww2dispatches-cards/main/cards/dispatch-NNN-x.jpg`

## Living Cards (video)
Same card bands with archival footage playing in the photo window, for big dispatches that have film.
* Since 18 Oct 2026 trimmed clips and finished videos are committed to ww2dispatches/ww2dispatches-videos (`footage/` and `videos/`), and Buffer links to `https://raw.githubusercontent.com/ww2dispatches/ww2dispatches-videos/main/videos/<file>`. This repo's `footage/` and `videos/` are working folders that ignore .mp4 files (a few older .mp4 files stay until the 20 to 23 Oct 2026 posts that use them have gone out).
* Finished clips: `dispatch-NNN-x.mp4` (1600 x 1440), `dispatch-NNN-instagram.mp4` (1080 x 1350), `dispatch-NNN-vertical.mp4` (1080 x 1920, for Reels, TikTok, and Shorts), each with a `-poster.jpg` of the first frame.
* Add a `video` block to the dispatch JSON (`footage`, optional `focusX` and `focusY`, plus `sourceUrl` and `note`), then run `node renderer/living.js <id>`.

## Living Press page
`renderer/living_press.py` builds the Living Press review page (a pinned claude.ai artifact) from every dispatch that has a Living Card (with its kit) or a Story Card (with its `story.kit` block).
```
python3 renderer/living_press.py <out_dir>   # writes living-press.html plus videos/ to publish
```
Rebuild and republish to the same artifact (https://claude.ai/artifact/7bCSGHeexkFYyn6s1vxRSe) whenever a video is added or a kit changes. Set `"scheduled"` in a dispatch's `kit` block to `true` or a short status line (for example "Buffer and YouTube Shorts scheduled · TikTok not yet").

## Name This cards
Puzzle cards posted Wednesday and Saturday at 10 a.m. Mountain: X Communities through Typefully, Threads, Facebook, and Instagram through Buffer. No dispatch number, so they never affect the dispatch serial.
* `namethis/` one JSON file per card: id, answer, date, place, clue (`pull`), photo, framing, target X community, sources, and once scheduled the Typefully draft id, Buffer ids (threads, facebook, instagram), post_date, and links. Full rules: the Project doc "WW2 Dispatches Name This".
* Stamp, ? seal, and clue are Mimeograph Violet `#5B4B8A`. Pick photos with no visible names, hull numbers, or markings that give the answer away.
* `node renderer/namethis.js [id ...]` writes `cards/namethis-<id>-x.jpg`.
