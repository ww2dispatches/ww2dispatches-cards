# The Map Room: format 2 (balcony and focus)

**Status, 20 Nov 2026:** approved by Brian and built. The checker (`engine/check_series.py`), the engine (`engine/render_series.py`) and the overlay tool (`tools/trace/overlay.py`) all work to this document; `test/series-proof/` is a two day test series. The old fixed views format and its tools (`check_record.py`, `render_day.py` used alone) are retired. Days without a move and aircraft missions were added on 21 Nov 2026.

## The idea
A real map room has a huge table. From the balcony you see every block on it, spread out, but you cannot read them. You only read a block when you come down and stand over it. The clip does the same:

1. **Balcony.** The whole battle from nearly straight above. Every unit on the roster is a small block in its nation's color with its silhouette. The grease pencil line shows the front from one edge of the map to the other.
2. **Focus.** The camera comes down to where today's story happens. Smaller towns and roads appear, block names become readable, and the rake makes the day's moves.
3. **Balcony again.** The new line is drawn, the camera goes back up, and the whole battle shows what changed.

Fixed rules behind it (Brian, 20 Nov 2026):
* **A block covers 10 km of ground, always.** It never changes size with the view. It is thin (about 40% of the old height) so it hides little of the map.
* **One balcony view per series.** No more opening, salient or Bastogne views.
* **One focus per day.** The engine fits the camera to the pieces that move. Nobody fits a view by hand.
* **Blocks never overlap and never pass through each other.** The engine spaces them. An attack into enemy ground drives the enemy block aside.
* **Every position and every line comes from the situation maps and is fact checked before anything is rendered** (see The fact check). The maps were drawn at noon, so a day's night table is read from the **next** day's map (see Which map).

## Who writes what
| File | Written | By | Holds |
|---|---|---|---|
| `series/<campaign>/series.json` | Once per series | Map Room chat | The balcony box, block size in km, the list of situation maps by date. |
| `series/<campaign>/geo/` | Once per series | Map Room chat | Rivers, borders, roads and towns for the map. |
| `series/<campaign>/units.json` | Once per series, in the build sitting | Campaign Series chat | The roster: every unit that will ever appear, who it is, and its block. |
| `mapRoom` block in each day record | Each day, in the build sitting | Campaign Series chat | Only what changed that day. |

The big saving is the last row. **A unit stays where it was last placed until a day says otherwise, and the morning line is always the night line of the day before.** Day 1 sets the table. After that a day only names the units that move, arrive, leave or shift, and gives the night line.

## The roster: `units.json`
One entry per unit, written once. Days refer to units by `id` only, so a unit's name, side and block can never drift from day to day.

```json
{"id": "101", "name": "101st Airborne Division", "label": "101st Airborne", "nation": "us", "type": "airborne",
 "parent": "VIII Corps, Third Army", "sources": ["Cole, The Ardennes, order of battle"]}
```
| Field | Rule |
|---|---|
| `id` | Short and unique in the series. |
| `name` | The full official name. |
| `label` | What the block says: the full name, 16 characters at most. Over 16, drop a word ("106th Infantry Division" becomes "106th Infantry"), never abbreviate (no Div, Inf, Pz, Abn, CCB). No SS unit names: show SS formations under their army or corps. No dashes. |
| `nation` | `us`, `britain`, `germany` (`soviet`, `japan` for later series). |
| `type` | `infantry`, `armor`, `artillery`, `airborne`, `fighter`, `medium_bomber`, `heavy_bomber`, `transport` (aircraft: see Aircraft), or a ship. Airborne divisions take `airborne` even when fighting on the ground. German parachute divisions that fought as infantry keep `infantry` unless the day is an actual drop. Any other kind of unit takes the closest block. |
| `heavy`, `variant` | Optional, as before (the Tiger; the B 29). |
| `parent` | The corps and army it belonged to. Used by the fact check and for crowded ground (see Spacing). |
| `sources` | One or more for the unit's identity and command. |

A roster of 15 to 25 units suits a land battle of this size. Divisions are the normal level. Use a corps or army block only for a stretch of front the story never visits.

## The day: the `mapRoom` block
```json
"mapRoom": {
  "asOf": "2400 hrs, 26 Dec 1944",
  "map": "LOC 12th Army Group situation map, 26 Dec 1944",
  "line": [[5.98, 51.75], "...", [8.15, 48.98]],
  "lineSources": ["LOC situation map, 26 Dec 1944", "Cole, The Ardennes, p. 555"],
  "moves": [
    {"unit": "4ad", "move": "advance", "to": [5.66, 49.91], "order": 1,
     "drives": [{"unit": "5fj", "to": [5.87, 49.90]}],
     "sources": ["Cole, The Ardennes, p. 555", "LOC situation map, 26 Dec 1944"]}
  ],
  "shifts": [{"unit": "80id", "to": [6.15, 49.86], "sources": ["LOC situation map, 26 Dec 1944"]}],
  "tonight": "The siege is broken. The corridor is one road wide."
}
```
| Field | Rule |
|---|---|
| `asOf` | The moment the night table shows. |
| `map` | The situation map the night table is read from: normally the **next** day's map, which shows tonight's positions at noon tomorrow. It must be one listed in `series.json` (Day 30 of the Bulge uses 15 Jan). |
| `line` | The front at the end of the day, as `[lon, lat]` points from the **north edge of the map to the south edge**, German ground on the left as you walk it. It must reach both edges: the front does not stop where the story stops. Day 1 also gives `lineStart`, the front before the battle (and `pocketsStart` if a unit is already surrounded), with `lineStartSources`: two or more, one of them Day 1's own situation map. |
| `lineSources` | Two or more. One must be the map named in `map`. |
| `pockets` | Optional. Ground held inside the other side's area at night: `{"side": "allied", "ring": [...]}`. No ring is drawn around a surrounded block; the line going around it on the day it happens tells that story. |
| `moves` | What the rake does, in `order`. One to three a day. All of a day's moves must fit in one focus (about 60 km across); a day with action in two far places picks one. |
| `shifts` | Units that are somewhere else tonight without it being shown: small adjustments of 15 km or less. The block is simply in the new place when the clip opens. Anything farther must be a move on some day. |
| `set` | Day 1 only (or the day a unit first appears without an `arrive`): `{"unit", "at", "sources"}` for every unit on the table. |
| `focus` | Optional `[lon, lat]`. Leave it out and the engine centers on the day's moves. |
| `tonight` | Optional closing strip. |

### The move set
| `move` | On the table | Fields |
|---|---|---|
| `advance`, `fall_back` | The rake pushes the block to `to`. | `to`, optional `drives` |
| `arrive` | The block slides in from a map edge to `to`. | `to`, `enters` |
| `leave` | The rake takes the block off the table (surrendered, destroyed, withdrawn). | `why` |
| `air_mission` | Aircraft only. The block shows `label`, what the aircraft are doing (Supply Drop, Glider Drop, Air Strike), not the unit's name. The rake pushes the aircraft block a short way in from the frame edge toward its bases; a dashed black grease pencil track is drawn one dash at a time straight over the target, a half circle turn beyond it, and back to the block beside the way in; a rake reaching from beyond the edge pulls the block back out; the track fades. | `target`, `enters`, `label` |

**Driven blocks (Brian, 20 Nov 2026).** When an attack goes into ground an enemy unit holds, list that unit under `drives` with where the sources put it that night. On the table the attacker meets it, with a knock, and carries it along. **If the way straight back is blocked, the driven block slides aside** along the front, on its own side of the new line. An attacker never ends against a friendly block by passing through an enemy one.

**Aircraft (Brian, 21 Nov 2026).** Aircraft are on the roster but never set on the table: an aircraft block appears only for its `air_mission`. `target` is the drop zone or the place struck, and must sit inside the day's focus. `enters` is the frame edge toward its bases (west for the Bastogne drops). `label` is what the block says (Brian, 21 Nov 2026: a supply drop labelled Troop Carrier is confusing), 16 characters at most; the unit's full name stays in the roster and the sources. A drop zone is flown over, not around (Brian, 21 Nov 2026): the track passes under the target's block and comes out the far side. The engine parks the block just inside that edge, clear of every ground block, and picks the turn distance and side so the least of the track is hidden under other blocks. Nothing but pencil crosses the battle area, so no route has to be found between blocks. Air tracks are black so they never read as the red front line. There is no grounded move: weather days simply have no aircraft. For an air attack whose targets are off the map (Bodenplatte, 1 Jan), put the target at the nearest point inside the focus on the way to them.

**The key card (Brian, 21 Nov 2026).** On a series' opening days (`keyDays` in `series.json`, 3 by default) a cream index card lies on the table in the balcony shot: the nations on the roster, the red front line, black dashes if the series has any air missions, the size of a block, and a north mark. It builds itself from the roster and the days, so nothing is written for it. The engine places it in the largest clear space of the balcony view, inside the safe area and clear of the tab, the strip, every block and both lines, covering as few town names as it can, shrinking to 90% or 80% when space is tight, and leaving it off if nothing clears. It fades as the camera comes down and back as it goes up. After the opening days the key lives in the kickoff post and the book.

**Quiet days.** A day with no moves is still a clip: the balcony only, about 7 seconds. The morning line is wiped to a ghost and the night line drawn, then the closing strip. Shifts are already in place when it opens. If nothing at all changed, the checker prints a NOTE (not an error) asking the Campaign Series chat to confirm the front really held still.

**Knock rule.** A knock only when something touches something: the rake meeting a block, or a block meeting a block.

### Spacing
Blocks are 10 km across, and real divisions often stood 5 to 10 km apart. The engine nudges blocks apart by up to 5 km each so none overlap, keeping each on its own side of the line. If a stretch of front is too crowded even for that, the checker says so and names the units. The fix is to show their corps as one block there, not to move anyone to a false position.

**Crowding exception (decided 27 Nov 2026, Bulge fact check).** A block may stand a little further from its map symbol than the fact check's one block limit only when the map's own spot is taken by neighbouring blocks. All of these must hold: it is no more than 2 blocks (20 km) off; it stays on its own side of the line, in the same sector and next to the same neighbours; it lasts only until the ground clears; and the record's sources for that block's last move or shift say "crowding exception" and name the blocks in the way. Past 20 km, or if the block ends up in another unit's sector, the corps block rule above applies. The fact check lists every exception by name, so nothing is waved through without being seen.

## The fact check
Nothing is rendered until every day passes all three parts. The Map Room chat runs them in its position check step, straight after the build sitting, and never changes a position itself: anything wrong goes back to the Campaign Series chat with the evidence.

**1. The checker (automatic, every day record).**
* Who: every unit in a day is on the roster; nation, type and label come only from the roster.
* Where it came from: a unit's start today is its end yesterday. The checker carries every unit forward, so a unit cannot jump, appear twice or vanish without a `leave`.
* How far: an `advance` or `fall_back` longer than 40 km in a day, or a `shift` longer than 15 km, is an error.
* Which side: every block is on its own side of the night line. Driven and attacking blocks end on the correct sides of the new line.
* The line: runs edge to edge, does not cross itself, and each day's morning line is the night line before it.
* Sources: every move, shift, set and line names the map in `map` (the next day's map, or the day's own map where it already shows the night position), and every move a second source.
* Table: no overlaps after spacing, no block passing through another during a move, moves fit one focus.

**2. The overlay sheet (every day, read by the Map Room chat).** `tools/trace/overlay.py` draws the day's night blocks and line on top of the next day's situation map scan (see Which map), lined up by the map's own grid. Each block is compared with the unit symbol printed on the map: the right unit, on the right side, within one block (10 km) of where the map shows it. The line is compared with the map's front along its whole length. The sheet is saved beside the day record so anyone can look.

**3. A blind second read (the units that move, and the line).** `tools/trace/blind_read.py packet` makes a folder with the scan cut into tiles under a labelled coordinate grid and the roster entries of the moving units, never their positions. A fresh reader who has not seen the day record (a separate agent started with only that folder) writes where the map shows each unit and the front. `blind_read.py compare` then measures the difference. Where the reader and the record differ by more than one block, or the reader cannot find a unit, the day goes back with both readings.

**Which map (21 Nov 2026).** The situation maps were drawn at noon, from reports up to a day old. So a day's night table is written from, and compared with, the **next** day's map; its morning table matches its own day's map. Day 1 sets the table from the 16 Dec map (`set`, and `lineStart` with its `lineStartSources`, the position at the start), and its night line from the 17 Dec map. Both the overlay and the blind read do this (`night` and `start`).

Where the situation map and Cole disagree about a position, follow Cole for where a unit went and say so in the sources. The situation maps were drawn at noon from reports that could be a day old.

Each day's result is written to `verify/day-NN.json`: passed or not, what was compared, and anything sent back.

## Commands
```
python3 map-room/engine/check_series.py <series folder>                       # part 1 of the fact check, the whole series
python3 map-room/tools/trace/overlay.py <series folder> <day number> <out> [night|start]       # part 2, the overlay sheet
python3 map-room/tools/trace/blind_read.py packet <series folder> <day number> <dir> [night|start]   # part 3, for the reader
python3 map-room/tools/trace/blind_read.py compare <series folder> <day number> <answers.json> [night|start]
python3 map-room/engine/render_series.py <series folder> <work dir> <out dir> [--days 11,12]
```
A series folder holds the `day-NN.json` records. The roster is `map-room/series/<campaign>/units.json`.

## What the Campaign Series chat does in the build sitting
1. Write `units.json` for the series.
2. For each day, in the same research pass as the story: the night `line`, the day's `moves`, any `shifts`. Day 1 also sets every unit.
3. Run the checker on the whole series and fix every error.
4. Hand off. The Map Room chat runs the overlay and the blind read, sends back anything wrong, then renders and schedules.
