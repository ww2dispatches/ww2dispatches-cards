# The Map Room

The third part of the Campaign Series: a filmed plotting table, one clip per day. The plan, the look, and every decision live in `docs/WW2 Dispatches Map Room.md` (the Project copy is the master). The day record format and the brief for the Campaign Series chat are in `FORMAT.md`. Renders never go in git; finished clips go to Cloudflare R2.

## Making a day's clip
```
python3 map-room/engine/render_day.py campaign-series/bulge-1944/day-03.json <work dir> day-03.mp4 [--photo still.jpg] [--samples 128]
```
It checks the record, renders whatever is missing (cached in the work dir, so each view's plate and most block sprites render once for the whole series), draws the overlays, composites, builds sound C from the day's moves, and joins them. `--stills 4.0,9.5` writes frames instead of a clip. Test runs use `--samples 16`.

Before rendering a series, after the build sitting:
```
python3 map-room/engine/check_record.py campaign-series/bulge-1944          # the pre render check, every day
python3 map-room/engine/contact_sheet.py campaign-series/bulge-1944 sheet.png   # every day's night table, flat and fast, errors in red
```

## Layout
| Path | What |
|---|---|
| `FORMAT.md` | The `mapRoom` block and the brief for the Campaign Series chat. |
| `engine/render_day.py` | One day, start to finish (above). |
| `engine/day.py` | Shared: reads a day and its view, works out positions, rake angles and the clip's timeline. |
| `engine/clip.py` | The compositor: slides the sprites, draws every move, the grease pencil line, pockets, rings, GROUNDED and the hatch on a flat sheet warped onto the table, the push in for closer views, the loop. |
| `engine/scene.py` | Blender (the `bpy` package): plates, block and rake sprites, rendered by spec. |
| `engine/template.json` | Frame, safe area, tab and strip placement, block zone, beat lengths. |
| `engine/check_record.py` | The pre render check: fields, labels (and that they fit the block), kit, safe area, sides of the line, overlaps, sources, order. |
| `engine/contact_sheet.py` | One sheet per series for review. |
| `engine/fit_view.py` | Frames a view: the largest map scale at which a box of places fits the block zone. |
| `engine/placeholder_map.py` | A watermarked stand in map per view until the traced maps exist (step 4). |
| `engine/faces.py`, `engine/ov.html`, `engine/ov_shoot.py`, `engine/maproom_sound.py` | Block faces, the tab and strip, sound C. |
| `engine/view.json` | The fixed camera. |
| `series/<campaign>/table*.json` | Each view's framing. Traced maps go in `series/<campaign>/maps/<view>.png` (`main.png` for the whole battle). |
| `kit/silhouettes/` | The 30 silhouettes and `library.json`. |
| `fonts/` | TTF copies of Oswald 700 and Special Elite. |
| `test/` | Test days (`day-t1` opening, `day-t2` Bastogne, `day-t3` salient: invented positions covering every move), `day01-example.json`, the sketch framing. Never posted. |

## Template rules
* **Safe area** (working zone across TikTok, Reels and Shorts): top 220, bottom 480, right 140 px. The tab sits at 230 px, the strip 480 px up; every block stays in the block zone between them, clear of the right rail.
* Sprites render on a padded frame (the rake with extra room for its long pole), over a padded plate that serves as every sprite's shadow base. A block sprite is rendered once per table cell and reused.
* The rake comes from behind the move, in one of eight directions, and is drawn just before the block it pushes.
* Knock rule: a knock only when the rake meets a block or a block is pushed into another (`contact`).
* Each clip loops: its last third of a second dissolves back to the opening still.
