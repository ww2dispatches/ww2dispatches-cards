# WW2 Dispatches cards

Post card images for WW2 Dispatches, a World War II this day in history account. Images are hosted here for scheduled posts on X, Instagram, and Threads.

## Layout
* `cards/` finished images, one pair per dispatch: `dispatch-NNN-x.jpg` (1600 x 1440) and `dispatch-NNN-instagram.jpg` (1080 x 1350). These are the files Buffer links to.
* `dispatches/` one JSON file per dispatch: number, date, place, series, pull line, caption, photo framing, and sources.
* `photos/` the public domain source photos.
* `renderer/` the card renderer, a copy of the Dispatch Press drawing code run in headless Chromium.

## Rendering
```
python3 renderer/fetch_photo.py "<Wikimedia Commons file page URL>" photos/<id>.jpg
node renderer/render.js            # every dispatch
node renderer/render.js <id> ...   # just these
```
Framing fields in a dispatch file work like the Dispatch Press sliders: `focusX` and `focusY` (0 to 100, default 50 and 40) and `zoom` (100 to 200).

Public link pattern: `https://raw.githubusercontent.com/ww2dispatches/ww2dispatches-cards/main/cards/dispatch-NNN-x.jpg`
