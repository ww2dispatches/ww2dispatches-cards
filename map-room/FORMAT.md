# The Map Room: the `mapRoom` block

> **Direction change, 20 Nov 2026 (Brian approved the zoom proof). This document still describes the old fixed views and is being rewritten.**
> Decided: one balcony view per series (the whole battle from nearly straight above); a focus point per day that the camera comes down to; every block covers 10 km of ground, about 40% of the old height; labels are read only in the close view; the grease pencil line runs to the edges of the map; an attack drives an enemy block back or aside (`driven`), blocks never overlap or cross, and the engine spaces them; unit positions come from that day's situation map; the bed is the Declass Ops room ambience. Proof: `tools/proof/proof_zoom.py`, `test/proof-zoom-*.json`.


Final format, 20 Nov 2026 (Map Room build chat). For the Campaign Series chat: write one `mapRoom` block into each day record (`campaign-series/<campaign>/day-NN.json`) in the build sitting, then run the checker. The Map Room chat turns each block into the day's clip, and its pre render check reads the same block. Full plan: the project doc "WW2 Dispatches Map Room".

## The short brief
1. **Pick the day around something that moved** where the story allows: a town taken, a road cut, a column pushing on.
2. **Write the block in the same research pass** as the day's story. Each move needs **two sources**: Cole, *The Ardennes: Battle of the Bulge* (CMH) sets where a piece goes; that day's Library of Congress 12th Army Group situation map is the second source. Where they differ, follow Cole.
3. **Six to eight pieces, one to four moves.** Show only the units that matter that day.
4. **Full unit names on the blocks**, 16 characters at most. Shorten only by dropping a word, never by abbreviating.
5. **Morning and night front lines**, from the north end of the front to the south end, following it around the Bulge (German ground on the left as you walk it).
6. **Blocks must not overlap**, and each sits on its own side of the line and inside the clip's safe area (between the tab and the strip, clear of the apps' buttons). Blocks are big on the map, so on crowded days use fewer pieces or the corps or army instead of each division.
7. **Pick the day's view** (`"view"`), each framed to its ground:
   * `"opening"`, 16 to 20 Dec: Monschau and Elsenborn to Echternach, Bastogne to the Our; a block about 24 km.
   * no view (the whole battle): days that span the front, such as the spearhead near the Meuse; a block about 40 km.
   * `"bastogne"`: days centered on Bastogne; a block about 7 km, so the 101st, the ring around it and the relief from the south can all be shown. Use it when the day's moves all happen around Bastogne; days that span the front (the spearhead near the Meuse, the northern shoulder) stay on the whole battle view.
   * `"salient"`: January days (a block about 20 km) once the Bulge is being squeezed: the First Army's attack from the north (3 Jan on), the Third Army's from the south, and the closing on Houffalize. Days whose story is elsewhere (Bodenplatte on 1 Jan, the Soviet offensive on 12 Jan) pick the view that fits their moves, or the whole battle view.
8. **Run the checker** after each day and fix every ERROR: `python3 map-room/engine/check_record.py campaign-series/bulge-1944`
9. **Do not schedule Buffer.** The Map Room chat schedules each day once its clip exists.

## Example
```json
"mapRoom": {
  "asOf": "2400 hrs, 16 Dec 1944",
  "lineAM": [[6.24, 50.57], [6.36, 50.42], [6.46, 50.29], [6.18, 50.13], [6.21, 49.93], [6.52, 49.73]],
  "linePM": [[6.24, 50.57], [6.23, 50.42], [6.44, 50.29], [6.10, 50.13], [6.14, 49.93], [6.50, 49.74]],
  "lineSources": ["Cole, The Ardennes, ch. and page", "LOC 12th Army Group situation map, 16 Dec 1944"],
  "pieces": [
    {"id": "5pz", "nation": "germany", "type": "armor", "label": "5th Panzer Army",
     "move": "advance", "from": [6.45, 50.12], "to": [6.21, 50.10], "order": 1,
     "sources": ["Cole, ...", "LOC situation map, 16 Dec 1944"]},
    {"id": "106", "nation": "us", "type": "infantry", "label": "106th Infantry", "name": "106th Infantry Division",
     "move": "hold", "from": [6.20, 50.27]},
    {"id": "9af", "nation": "us", "type": "fighter", "label": "Ninth Air Force",
     "move": "grounded", "from": [5.72, 50.38], "order": 2, "sources": ["...", "..."]}
  ]
}
```
A full example is `map-room/test/day01-example.json` (sketch positions, not verified).

## Day level
| Field | Rule |
|---|---|
| (day) `campaign` | Already in every day record. It picks the series' table framing (`map-room/series/<campaign>/table.json`). |
| (day) `subtitle` | The clip's strip uses the day's existing subtitle, 38 characters at most. Nothing new to write. |
| `view` | Optional. Omit for the whole battle. `"opening"` for 16 to 20 Dec, `"bastogne"` for the Bastogne close view, `"salient"` for the January squeeze. Framings in `map-room/series/bulge-1944/table*.json`. Positions are always real `[lon, lat]`; the view only changes how close the table is. |
| `asOf` | The moment the night table shows: `"2400 hrs, 16 Dec 1944"`. |
| `lineAM`, `linePM` | The front at the start and end of the day: 3 to 24 `[lon, lat]` points from the **north end of the front to the south end**, following it around any bulge, so **German ground is on the left** as you walk it (inside the Bulge). The line may run a little past the table's edges (the drawing clips it), but at least two points must be on the table. On the Bastogne view this is often just the stretch of front that crosses the view. |
| `lineSources` | Two or more sources for the lines. |
| `pocketsAM`, `pocketsPM` | Optional. Ground held inside the other side's area, such as Bastogne once surrounded: `{"side": "allied", "ring": [[lon, lat], ...]}`. |
| `tonight` | Optional. The closing strip. Default: "The line tonight. It moves again tomorrow." |

## Pieces
| Field | Rule |
|---|---|
| `id` | Short and unique within the day. Keep the same id for the same unit across days. |
| `nation` | `us`, `britain`, `germany` (`soviet`, `japan` for later series). The side and the block color follow from it. |
| `type` | `infantry`, `armor`, `artillery`, `airborne`, `fighter`, `medium_bomber`, `heavy_bomber`, `transport`, or a ship (`carrier`, `battleship`, `destroyer`, `submarine`, `landing_craft`). Artillery, airborne and ships are one shared silhouette each, in the nation's color. **Airborne divisions take `airborne` even when fighting on the ground** (the 101st at Bastogne). German parachute divisions that fought as infantry keep `infantry` unless the day is an actual drop. Any other kind of unit (engineers, tank destroyers, cavalry) takes the closest existing block and its name says the rest, unless the day's main action depends on it: then tell the Map Room chat. |
| `heavy` | Optional, German armor only: shows the Tiger. Only when the day's story names a Tiger or heavy tank unit; give that unit in `heavyNamed`. |
| `variant` | Optional: `"b29"` for the B 29 on a US heavy bomber. |
| `label` | What the block says. The full unit name, 16 characters at most. Over 16, drop a word ("106th Infantry Division" becomes "106th Infantry"), never abbreviate (no Div, Inf, Pz, Abn, CCB). No SS unit names: show SS formations under their army or corps. No dashes. |
| `name` | The full official name, only when the label had to be shortened. |
| `move` | One of the move set below. |
| `from` | Where the block stands in the morning, `[lon, lat]`, two decimals. Not used for `arrive`. |
| `to` | Where it ends. Only for `advance`, `fall_back`, `arrive`. |
| `enters` | `arrive` only: the table edge it slides in from (`north`, `south`, `east`, `west`). |
| `target` | `air_mission` only: the place hit, `[lon, lat]`. |
| `contact` | Optional, with `advance` or `fall_back`: the id of the block this one is pushed into. The two blocks end touching, with a knock. |
| `order` | Every piece that does something (all moves except `hold`): 1, 2, 3 in clip order, no gaps. |
| `sources` | Two or more for every piece that does something. |

## The move set
| `move` | On the table | Sound |
|---|---|---|
| `advance` | The rake pushes the block forward to `to`. | Rake tap, slide |
| `fall_back` | The rake pushes the block back to `to`. | Rake tap, slide |
| `arrive` | The block slides in from the `enters` edge to `to`. | Rake tap, slide |
| `hold` | The block stays where it is. | None |
| `cut_off` | Stays; a grease pencil ring is drawn around it. | Pencil |
| `surrender` | The rake drags the block off the table. | Rake tap, slide |
| `air_mission` | The aircraft block slides out to `target` and back. | Slide |
| `grounded` | The aircraft block stays, with GROUNDED pencilled beside it. | Pencil |

Knock rule (Brian, 20 Nov 2026): a knock only when something touches something, the rake meeting a block or a block pushed into another (`contact`).

## What the checker enforces
Errors: missing or wrong fields; an airborne division not on the airborne block; label over 16 characters, short forms, SS names, dashes; no silhouette in the kit for that nation and type; a block off the table or partly off screen; a block on the wrong side of the morning or night line (aircraft, `cut_off` and `surrender` are exempt); blocks overlapping at the start or end of the day; fewer than two sources on a move or on the lines; `order` with gaps; more than eight pieces; a placeholder left in a source. Warnings: a German parachute block on a day that is not a drop; fewer than four pieces, more than four moves, nothing moving, coordinates with more than two decimals.

The Map Room chat also compares each day's positions with that day's situation map while tracing the Ardennes map. Anything that looks wrong comes back to the Campaign Series chat to fix in the record. The Map Room chat never changes positions itself.
