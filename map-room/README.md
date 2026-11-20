# The Map Room

The third part of the Campaign Series: a filmed plotting table, one clip per day. The plan, the look, and every decision live in `docs/WW2 Dispatches Map Room.md` (the Project copy is the master). This folder holds the code and the kit. Renders never go in git; finished clips go to Cloudflare R2.

## Layout
| Path | What |
|---|---|
| `engine/scene.py` | Blender scene (plate, blocks, masks, rake, camera). Run with the `bpy` package. |
| `engine/comp.py` | Compositor: slides the sprites, draws the grease pencil line and hatch, overlays, encodes. Runs the pre render check first. |
| `engine/faces.py` | Block faces from the silhouette kit. |
| `engine/ov.html` | The Day by Day tab and strip, drawn in headless Chrome with `renderer/fonts`. |
| `engine/maproom_sound.py` | Sound C (table, war room bed, in house theme), generated in code. Seeded, so the stems regenerate exactly. |
| `engine/check_record.py` | Checks the `mapRoom` block in day records (format in `FORMAT.md`). The Campaign Series chat runs it in its build sitting; the pre render check builds on it. |
| `engine/view.json` | The fixed camera, so the checker can test the frame without Blender. |
| `series/<campaign>/table.json` | Where each series' map sits on the table (center and scale). The Bulge framing fits the whole battle; a block covers about 27 km. |
| `FORMAT.md` | The `mapRoom` block format and the brief for the Campaign Series chat. |
| `kit/silhouettes/` | The 28 cream silhouettes and `library.json` (nation colors, file map, rules). |
| `fonts/oswald700.ttf` | TTF copy of Oswald 700 for the faces (PIL needs a TTF). |
| `test/` | The Day 1 test record (old format, used by `comp.py` until step 3), `day01-example.json` (the new format), the sketch framing `table.json`, and the 19 Nov sketch map. All positions unverified, never posted. |

Day records stay with their series: `campaign-series/<series>/day-NN.json`, in the `mapRoom` block (see `FORMAT.md`). `scene.py` and `comp.py` still use the sketch framing and the old test record; step 3 moves them onto `table.json` and the `mapRoom` block.

## Running a day
Work folder (`MAPROOM_WORK`, outside the repo) holds `map.png`, `face-*.png`, `cam.json`, `campad.json`, `plate.png`, `platepad.png`, the sprite folder, and `ov/`. `MAPROOM_DAY` points at the day record.

```
python3 engine/faces.py
python3 engine/scene.py cam     x 1080 1920 1 $W/cam.json
python3 engine/scene.py campad  x 1080 1920 1 $W/campad.json
python3 engine/scene.py plate   x 1080 1920 128 $W/plate.png
python3 engine/scene.py platepad x 1080 1920 128 $W/platepad.png
python3 engine/scene.py block <id> 1080 1920 128 $W/s/blk-<id>.png   # and mask <id> -> msk-<id>.png
python3 engine/scene.py rake  x 1080 1920 128 $W/s/blk-rake.png      # and rakemask -> msk-rake.png
python3 engine/comp.py s <out.mp4> check                             # pre render check only
python3 engine/comp.py s <out.mp4>
```

## Template rules (20 Nov 2026)
* Every sprite renders on the padded frame: 270 px of room past the left and right edges, 240 px past top and bottom, same pixel scale. A block near the edge stays whole, and `platepad.png` is the shadow base for all of them.
* The rake is drawn just before the block it pushes, so the block sits over the rake head, with a 0.12 gap (was 0.07).
* The pre render check refuses any block that is partly off screen where it starts or ends, judged at the end of clip push in. A block whose `move` is `arrive` is exempt at its start, since it slides in from the edge.
