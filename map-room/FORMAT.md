# The Map Room: format 2 (balcony and focus)

**Status, 20 Nov 2026:** draft for Brian's approval. It replaces the fixed views format of the same morning. The proof clip (`tools/proof/proof_zoom.py`, `test/proof-zoom-*.json`) shows the look. The engine and the checker are being rebuilt to this document, so `check_record.py` still enforces the old format until that lands. The Campaign Series chat should not write `mapRoom` blocks until this status line says the checker is ready.

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
* **Every position and every line comes from that day's situation map and is fact checked before anything is rendered** (see The fact check).

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
| `type` | `infantry`, `armor`, `artillery`, `airborne`, `fighter`, `medium_bomber`, `heavy_bomber`, `transport`, or a ship. Airborne divisions take `airborne` even when fighting on the ground. German parachute divisions that fought as infantry keep `infantry` unless the day is an actual drop. Any other kind of unit takes the closest block. |
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
| `map` | That day's situation map. It must be one listed in `series.json`. |
| `line` | The front at the end of the day, as `[lon, lat]` points from the **north edge of the map to the south edge**, German ground on the left as you walk it. It must reach both edges: the front does not stop where the story stops. Day 1 also gives `lineStart`, the front before the battle. |
| `lineSources` | Two or more. One must be the day's situation map. |
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
| `air_mission`, `grounded` | As before: the aircraft block goes out to `target` and back, or stays with GROUNDED pencilled beside it. | `target` |

**Driven blocks (Brian, 20 Nov 2026).** When an attack goes into ground an enemy unit holds, list that unit under `drives` with where the sources put it that night. On the table the attacker meets it, with a knock, and carries it along. **If the way straight back is blocked, the driven block slides aside** along the front, on its own side of the new line. An attacker never ends against a friendly block by passing through an enemy one.

**Knock rule.** A knock only when something touches something: the rake meeting a block, or a block meeting a block.

### Spacing
Blocks are 10 km across, and real divisions often stood 5 to 10 km apart. The engine nudges blocks apart by up to 5 km each so none overlap, keeping each on its own side of the line. If a stretch of front is too crowded even for that, the checker says so and names the units. The fix is to show their corps as one block there, not to move anyone to a false position.

## The fact check
Nothing is rendered until every day passes all three parts. The Map Room chat runs them in its position check step, straight after the build sitting, and never changes a position itself: anything wrong goes back to the Campaign Series chat with the evidence.

**1. The checker (automatic, every day record).**
* Who: every unit in a day is on the roster; nation, type and label come only from the roster.
* Where it came from: a unit's start today is its end yesterday. The checker carries every unit forward, so a unit cannot jump, appear twice or vanish without a `leave`.
* How far: an `advance` or `fall_back` longer than 40 km in a day, or a `shift` longer than 15 km, is an error.
* Which side: every block is on its own side of the night line. Driven and attacking blocks end on the correct sides of the new line.
* The line: runs edge to edge, does not cross itself, and each day's morning line is the night line before it.
* Sources: every move, shift, set and line names that day's situation map, and every move a second source.
* Table: no overlaps after spacing, no block passing through another during a move, moves fit one focus.

**2. The overlay sheet (every day, read by the Map Room chat).** `tools/trace/overlay.py` draws the day's blocks and night line on top of that day's situation map scan, lined up by the map's own grid. Each block is compared with the unit symbol printed on the map: the right unit, on the right side, within one block (10 km) of where the map shows it. The line is compared with the map's front along its whole length. The sheet is saved beside the day record so anyone can look.

**3. A blind second read (the units that move, and the line).** A separate check is given only the scan and the roster, not the day record, and reports where it finds each moving unit and the front. Where it and the record differ by more than one block, the day goes back with both readings.

Where the situation map and Cole disagree about a position, follow Cole for where a unit went and say so in the sources. The situation maps were drawn at noon from reports that could be a day old.

Each day's result is written to `verify/day-NN.json`: passed or not, what was compared, and anything sent back.

## What the Campaign Series chat does in the build sitting
1. Write `units.json` for the series.
2. For each day, in the same research pass as the story: the night `line`, the day's `moves`, any `shifts`. Day 1 also sets every unit.
3. Run the checker on the whole series and fix every error.
4. Hand off. The Map Room chat runs the overlay and the blind read, sends back anything wrong, then renders and schedules.
