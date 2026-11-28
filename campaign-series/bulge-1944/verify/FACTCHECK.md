# Bulge fact check (Map Room chat, 27 Nov 2026)

Every day's night table was checked two ways against the next day's LOC situation map: an overlay sheet (every block drawn on the scan) and a blind second read by fresh readers who never saw the records. The reader results are in `day-NN-blind-night.json`; the crops in `evidence/` show each mismatch (blue box: where the record puts the block; red circle: the symbol on the map).

## Result
* **The front line passes on all 30 days.** Every day's line is within 10 km of the blind reader's line, most within 5 to 7 km. The one exception is Day 9 (24 Dec), up to 23 km at the Celles tip, which is the Cole exception already listed in the doc.
* **Days 1 to 15 pass.** The only differences there are the German divisions placed by Cole, and the corps blocks (see "Expected differences" below).
* **Four Allied blocks don't match the maps from Day 16 on, and need fixing in the records.** The Map Room chat doesn't change positions; the fixes belong to the Campaign Series chat.

## Send back (please fix)
1. **84th Infantry (84id), Days 18 to 30.** The block stays near Marche at [5.29, 50.24] from its Day 17 shift to the end. From the 3 Jan map on, the maps show the 84th east of the Ourthe in VII Corps' attack toward Houffalize, and further south each week. Map readings, by night table: Day 18 [5.47, 50.34] (17 km off); Day 22 [5.46, 50.31] (14 km, blind read); Day 23 [5.49, 50.30] (16 km, blind read); Day 28 [5.56, 50.26] (19 km, blind read); Day 30 [5.68, 50.20] (28 km). Fix: an advance on Day 18 (3 Jan, the VII Corps attack) to about [5.46, 50.33], and shifts or advances after that following the maps south. Evidence: `day-18-84id.jpg`, `day-22-84id-2ad.jpg`, `day-28-84id-2ad.jpg`, `day-30-84id-2ad.jpg`.
2. **2nd Armored (2ad), Days 21 to 30.** The block stops at [5.45, 50.285] after its Day 19 advance. The maps show it pushing south beside the 84th: Day 21 [5.64, 50.30] (13 km); Day 23 [5.60, 50.29] (11 km, blind read); Day 26 [5.63, 50.25] (13 km); Day 28 [5.67, 50.24] (16 km, blind read); Day 30 [5.72, 50.24] (20 km). Fix: an advance on Day 20 or 21 to about [5.62, 50.29], then follow the maps south to about [5.72, 50.24] by Day 30. Evidence: the same three crops.
   * Note that Day 22 is the checker's quiet day NOTE. The front line really does match on the 6 and 7 Jan maps, but the 2nd Armored and 84th move inside it, so a move added there may turn Day 22 into an ordinary day.
3. **6th Armored (6ad), Days 16 to 30.** It arrives on Day 16 at [5.835, 49.88], which on the map is the 35th and 26th Infantry's ground south of Wiltz. Every map from 1 Jan shows the 6th Armored just south east of Bastogne, at about [5.67 to 5.72, 49.95 to 49.99]: 16 km off on Days 16, 17, 22 and 23 (blind reads), and 11 km on Day 28. Its own source (Cole, the corridor's east side) agrees with the map. Fix: the Day 16 arrival `to` at about [5.70, 49.97]. Evidence: `day-16-6ad.jpg`.
4. **3rd Armored (3ad), Day 17, and the days around it (please check).** The record keeps it on the front at [5.60, 50.33] from Day 8. On the 2 Jan map (Day 17's night) it is in an assembly area near Hamoir at [5.33, 50.48], 25 km north, before the 3 Jan attack. On the 7 Jan map (Day 22) the reader found no 3rd Armored symbol at all. From Day 19 its record is within 7 to 9 km of the map, which passes. Please check Cole on when the 3rd Armored left the line in late December. If it did, add a fall_back (or leave) and a return on Day 19. If Cole keeps it on the front, keep the record and name Cole as the source, like the other exceptions. Evidence: `day-17-3ad.jpg`.

## Smaller, your call
* **82nd Airborne, Days 26 to 28:** the maps show it pulled back to around Aywaille, about [5.72, 50.47], 10 to 11 km behind its block (relieved in early January). It's right at the one block limit; a fall_back on Day 26 would match.
* **4th Armored, Day 28:** 11 km from the reader ([5.72, 50.00] on the map against [5.69, 49.905]), just over the limit. It's probably fine to leave.
* **6th Airborne, Days 21 to 23:** the block stands at Bure, where the division fought on 3 to 5 Jan (its source, paradata). The maps draw the division symbol north of Rochefort at about [5.17, 50.21], 12 to 13 km away. Keep it at Bure, but add a line naming this as a history-over-map exception, like Celles.

## Expected differences (no change needed)
* **German divisions** (2nd Panzer, 26th and 18th Volksgrenadiers, 15th Panzergrenadiers): 11 to 27 km from the map symbols on several days, because the maps show them where Allied intelligence last saw them. The doc already says they follow Cole.
* **Army and corps blocks** (Sixth Panzer Army, Seventh Army, III Corps, V Corps): the map draws army and corps headquarters, which sit 15 to 45 km behind the front. The blocks stand on the ground each one held, so they differ by design. The readers found no Sixth Panzer Army or Seventh Army symbol on any map.

## After the fixes
Rerun `check_series.py`, then tell the Map Room chat. It will rerun the overlay and the blind read on the days that changed. Days 1 to 15 aren't affected by any of these fixes, so they can render now.
