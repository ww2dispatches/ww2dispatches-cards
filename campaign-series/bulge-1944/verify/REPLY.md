# Reply to the Bulge fact check (Campaign Series chat, 27 Nov 2026)

All four "Send back" items are fixed in the records, and the three smaller items are decided. `check_series.py` passes. Its one NOTE is Day 22, which is still a quiet day. Distances below are from each block's night position to the readings in FACTCHECK.md and the blind reads.

## Send back
1. **84th Infantry.** It shifts on Day 18 to [5.36, 50.30], in the VII Corps line west of the 2nd Armored, and shifts again on Day 28 to [5.56, 50.287]. Distances: Day 18 9.0 km, Day 22 7.2, Day 23 9.3, Day 28 3.0, **Day 30 12.9**. Day 30 can't get closer: the map's spot for the 84th is boxed in by the 2nd Armored to the east and the 51st Highland at La Roche to the south, so a 10 km block can't stand there. Please judge it as a crowding exception.
2. **2nd Armored.** It shifts on Day 18 to [5.50, 50.40], advances on Day 19 to [5.55, 50.32] and advances again on Day 27 to [5.705, 50.255]. Distances: Day 19 2.2 km, Day 21 6.8, Day 22 2.6, Day 23 4.9, Day 26 9.6, Day 28 3.0, Day 30 2.0.
3. **6th Armored.** It now arrives on Day 16 at [5.725, 49.915], just southeast of Bastogne. Distances: Day 16 8.2 km, Day 17 6.9, Day 22 8.7, Day 23 8.5, Day 28 3.9. To make room, three blocks moved a little (all checked against the readings):
   * The 4th Armored shifts on Day 16 to [5.585, 49.88] (Day 17 9.5 km, Days 22 and 23 7.2).
   * The 28th Infantry's remnant shifts to [5.43, 49.80] until it leaves on Day 18.
   * The 11th Armored's Day 17 shift is now [5.55, 49.975].
   * The 17th Airborne's Day 18 arrival is now [5.41, 49.95] (9.8 km), so its Day 20 attack clears the 4th Armored.
4. **3rd Armored.** Cole ends CCA's fight south of Manhay on 31 December (ch. XXIII), and the 83rd Division's morning reports put it in the line at Soy and Grand-Pré on 30 and 31 December. So the 3rd Armored now **leaves on Day 17** (to its assembly area near Hamoir, sourced to the 2 Jan map) and **arrives again on Day 19** at [5.695, 50.36] for the attack. It shifts on Day 27 to [5.83, 50.36] and advances on Day 30 to [5.85, 50.26].
   * Distances: Day 19 5.1 km, Day 23 8.4, **Day 28 12.8**, Day 30 6.2.
   * The Day 28 gap is the price of the 2nd Armored's drive south: it has to pass the 3rd Armored, and the 3rd's Day 30 advance has to clear it again. Please judge it as a crowding exception.
   * The 3rd Armored is off the table on Day 18 (night of 2 Jan), although the 3 Jan map shows it moving back up. A block couldn't come back from Hamoir on Day 18 without breaking that day's focus around the 17th Airborne.

## Smaller items
* **82nd Airborne:** done. A fall_back on **Day 24** (the 75th Division relieved it on the Salm on 8 January) to [5.78, 50.50], near Aywaille. Its Day 18 shift is now [5.84, 50.42], to give the 3rd Armored room. Distances: Day 22 9.2 km, Day 23 9.1, Day 26 5.4, Day 28 1.8.
* **4th Armored, Day 28:** left as is, now **16.4 km**, because the 6th Armored took the ground southeast of Bastogne. The map draws the 4th just south of the 101st, where a fourth block won't fit. Please judge it as a crowding exception.
* **6th Airborne, Days 21 to 23:** kept at Bure. Day 21's move now names the exception in its sources (the map draws the division north of Rochefort, about 12 km away; the block follows the fighting at Bure). It is also listed with the other history over map exceptions in the Campaign Series doc.

## Days that changed
16, 17, 18, 19, 24, 27, 28, 30. Days 20 (the 17th Airborne's start point) and 21 (the 6th Airborne source line) changed slightly too. Days 1 to 15 are unchanged and can render now.

# Round 2 reply (Campaign Series chat, 27 Nov 2026)
* **82nd Airborne:** the fall_back now happens on **Day 26** (11 Jan map), not Day 24. Distances: Days 24 and 25 9.3 km (still in the line), Day 26 5.4. Day 26 now has three moves (2nd Panzer leaves, 15th Panzergrenadiers fall back, 82nd falls back).
* **84th Infantry:** its Day 28 shift is now a **Day 27 advance** (order 3, after the 2nd Armored's drive south and the 51st Highland's arrival), to [5.56, 50.287]. It had to be a move, not a shift, because shifts are placed at morning, when the 2nd Armored still stands on that ground. Days 27 and 28 are now 3.0 km off.
* **Crowding exceptions:** each block's last move or shift now carries a source starting "Crowding exception:" that names the blocks in the way:
  * the 84th's Day 18 shift (Days 24 to 26: the 2nd Armored)
  * the 84th's Day 27 advance (Day 30: the 2nd Armored and the 51st Highland)
  * the 3rd Armored's Day 27 shift (Day 28: the 2nd Armored passing)
  * the 4th Armored's Day 16 shift (Day 28: the 6th Armored and the 101st Airborne)
* `check_series.py` passes; its one NOTE is Day 22. Days changed in this round: 16, 18, 24, 26 and 27 (on Days 16 and 18 only the source notes changed, so the picture is the same).

# Round 3 reply (Campaign Series chat, 27 Nov 2026)
* **82nd Airborne:** option (a). The Day 26 fall_back is removed, and the 82nd gets a **Day 27 shift** to [5.76, 50.48], sourced to the 12 Jan map. Distances: Day 26 7.2 km (still in the line), Day 27 3.1, Day 28 3.1.
* The relief source (the 75th Division's history on lonesentry.com) dates it 8 January. That's a single secondary line against three maps in a row, so the block follows the maps, and the shift's sources say so.
* Day 26 is back to two moves. `check_series.py` passes; its one NOTE is Day 22. Only Days 26 and 27 changed.
