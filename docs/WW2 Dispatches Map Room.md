# WW2 Dispatches: The Map Room

A period plotting table, in motion. Wooden pieces are pushed across a glossy campaign map, one clip for every day of a Campaign Series, so followers watch the front line move and come back to see where it stands tomorrow. It is the third part of the Campaign Series (named The Map Room on 20 Nov 2026), beside Day by Day and The Chronicle.

**Status: Proposed 19 Nov 2026.** Talked through with Brian by voice that evening and laid out here. Nothing is built and no other doc, skill, or scheduled task has been changed. Everything below marked Proposed waits for Brian's yes. The mockup exists so the look can be judged before anything is committed.

## Why this exists
* **The problem (Brian, 19 Nov 2026):** posts get views, but the views do not turn into follows, likes, or Declass visits. The videos are short archival clips that simply end and loop. Nothing gives a viewer a reason to come back.
* **The cause:** every dispatch stands alone. A viewer gets a complete story and has no tomorrow to wait for.
* **The answer:** a serial with a tomorrow. The Campaign Series is the first thing we make that moves day by day, and a moving table makes that visible in two seconds, with no reading needed.
* **The path it creates:** the evening clip catches someone in the feed. "Where does the line stand tomorrow" earns the follow. The clip points to the book on ww2dispatches.com for the full story. The book is where the table can be stepped through day by day, and where the Declass button lives. For the Bulge, that path ends in January at Campaigns, where the player fights the same battle at Bastogne.

This is a theory until the numbers say so. See Measuring.

## What it is: three forms, one set of data
| Form | Where | What it does | When |
|---|---|---|---|
| **The daily clip** | **The Day by Day post itself**, 6:30 a.m. Mountain, all six channels (decided 20 Nov 2026) | A 12 to 20 second vertical video. It opens on the day's archival photo in the Day by Day Teletype frame for about a second, then cuts to the table: the day's blocks are pushed into place, the line shifts, and it ends on where the line stands at nightfall. Carries the day's full story caption. | From Bulge Day 1, Wed 16 Dec 2026 |
| **The table in the book** | ww2dispatches.com, the series' book on the Campaign Shelf | Each day page shows that day's table. In a Chronicle chapter the table sits in the page and the pieces shift as the reader moves through the days. This is the explorable map. | Day pages at launch if ready, Chronicle chapters from Part 1 (about 24 Dec) |
| **The game** | Declass Campaigns | Already planned. Campaigns is played on plotting tables in the same style (Card Design doc, "The Campaigns battlefield"), and Bastogne chapter 1 opens 1 Jan 2027. The series table and the game table should look like the same room. | 1 Jan 2027 |

All three are drawn from one record per day (below), so the post, the clip, the book, and the game can never disagree.

## How it ties into the Campaign Series
* **It is part of the series, not its own entity** (Brian, 19 Nov 2026). No new brand, no new research run. The series already has the dates, the daily story, and the serial hook.
* **Name (decided 20 Nov 2026, Brian): The Map Room.** Display format "Campaign Series: The Bulge · The Map Room · Day 3 of 30", matching Day by Day and The Chronicle. A real wartime term (Churchill's and Roosevelt's Map Rooms) and a room, like Code Room. "The Table" was the working name until 20 Nov 2026, rejected as too generic, and was replaced everywhere that day (docs, OneDrive folder, files, mockup).
* **One post a day, not two** (decided 20 Nov 2026, Brian, option B): the 6:30 Day by Day post becomes the Map Room clip with the day's story caption. The archival photo is not lost: it is the clip's opening frame, and it still shows on the site's day pages and in The Chronicle. Brian: it keeps the photo people would see anyway, ties it to what happened on the map, gives every platform the same Campaign Series content, and puts the series on the strongest video channels. Both daily Living Cards (noon and 7 p.m.) are untouched, and no post is added.
* **It changes every day** (Brian, 19 Nov 2026), since in a real campaign something moves every day. On a quiet day the move is small: one division shifts, or the aircraft sit grounded by weather.
* **The story drives the pieces** (Brian, 19 Nov 2026). Each day's moves come from that day's verified story, so the pick for each day should center on something that moved: a town taken, a road cut, a column pushing north.
* **The long version is the home** (Brian, 19 Nov 2026). The Chronicle on the website is where the series really lives, and it is where the table does its deepest work. Brian is happy to change the Chronicle to fit.

### The day record gains one block (final 20 Nov 2026)
`campaign-series/<series>/day-NN.json` gets a `mapRoom` block, written in the same sitting as the post. **The full format and the brief for the Campaign Series chat are in the cards repo at `map-room/FORMAT.md`**, and `map-room/engine/check_record.py` checks each day. In short:
* `asOf` ("2400 hrs, 16 Dec 1944"); the clip's strip reuses the day's existing `subtitle`.
* `lineAM` and `linePM`: the morning and night front, from the north end of the front to the south end, following it around the Bulge, with German ground on the left as you walk it (corrected 20 Nov 2026: the first rule, strictly north to south, could not draw a bulge); `lineSources`, two or more; optional `pocketsAM` and `pocketsPM` for surrounded ground such as Bastogne.
* `pieces`, six to eight: `id`, `nation`, `type` (from the silhouette kit, including the shared artillery and airborne blocks; see The look), `label` (full name, 16 characters at most, shortened only by dropping a word), `name` when shortened, `move` (the move set), `from`, `to`, `enters` for arrive, `target` for air missions, `contact` when a block is pushed into another, `order` and two `sources` for every piece that does something.
* **Table framing per series** (`map-room/series/<campaign>/table.json`): the Bulge is framed so the whole battle, Celles to the German border and Echternach to Elsenborn, fits the camera. A block then covers about 27 km, so crowded days use fewer pieces or a higher level (corps or army). The 19 Nov sketch framing was too tight: Bastogne fell off screen.
* **The Bastogne close view** (decided 20 Nov 2026, Brian): days whose story centers on Bastogne carry `"view": "bastogne"` and use a second framing (`table-bastogne.json`), about 22 km across with a block about 5 km, so the 101st, the ring around it and the 4th Armored's approach from the south can all be shown. Why: the battle itself is at its widest in late December (the spearhead near the Meuse), but the story narrows to a pocket about 8 to 10 km across, smaller than one block on the whole battle view. Days that span the front stay on the whole battle view. Positions are real coordinates either way, so the book's stepping table can show either view.

### Rules in the Campaign Series doc this would change (Proposed, not yet edited)
* "Platforms: X, Threads, Instagram, Facebook. No YouTube or TikTok version." The Map Room would go to all six. Day by Day stays as it is.
* "No add on lines ever." The Map Room would carry one line pointing to the book. Day by Day stays as it is.
* "Day by Day is a photo post" and its image sizes: Day by Day becomes a vertical video, opening on the still. The still keeps being rendered, since it is the opening frame and the site's day image.
* The Bulge sitting writes the day records (story and moves) but does not schedule Buffer; the Map Room chat schedules each day once its clip exists.
* Nothing changes for the Videos doc or the weekly runs.

## The look
**Decided with Brian, night of 19 Nov 2026, after the first mockup and three rounds of counter studies:**
* **A plotting table, filmed.** A glossy map under a warm lamp, a wooden rim, the room dark around it. It should look like someone filmed a real table.
* **The pieces are wooden blocks, not figures.** Thick blocks in a **dark stained wood** with a printed face. Brian rejected carved figures (tank, soldier, aircraft) as childish, both in the first clip and in the film quality render, and rejected thin card counters as the second choice. Blocks keep the wood, read best on a phone, and look like a grown up tabletop game.
* **Each face carries three things:** the nation's color, a cream silhouette for the type, and the unit name in Oswald. No flags, no insignia, no regime symbols, no strength numbers, and no SS unit names.
* **One color per nation:** olive for the United States (#5E6233), khaki for Britain (#9A8358), charcoal for Germany (#34373B), red for the Soviet Union (#96392F), ochre for Japan (#B58A2E). Blue and red by side was rejected. Olive beside slate grey was rejected as too close; charcoal separates clearly.
* **One silhouette per nation per type.** The silhouette stands for the nation, never for the unit's actual equipment, so no day needs equipment research.
  * **Infantry is a helmet,** one per nation, from Brian's set (made in Grok): United States, Britain, Germany, Soviet Union, Japan. For Japan, the first helmet he sent (flared on both sides) stays; a replacement was tried and dropped as too close to the German one. Soldier figures of every kind were rejected as childish.
  * **Armor is a tank,** one per nation, from Brian's set: Sherman, Churchill, T 34, and for Germany the Panzer IV. **The Tiger is kept for special occasions** (Brian, 20 Nov 2026: too iconic to leave out, but not the everyday tank). The rule: a German armor block shows the Panzer IV unless the day's own verified story names a Tiger or a heavy tank unit, so no day needs extra equipment research. No Japanese tank yet.
  * **Aircraft come in three roles,** fighter, medium bomber, heavy bomber, all seen from above, nose up, with straight wings and propellers so none reads as a jet. From Brian's set: United States P 51, B 25, B 17; Britain Spitfire, Lancaster; Germany Bf 109, Ju 88; Soviet Union Il 2; Japan Zero, G4M. Added 20 Nov 2026: Brian's B 29, and a C 47 transport drawn by Claude (the Bulge needs it for the Bastogne supply drops on 23 Dec), with a tapered nose and rounded tip as Brian approved.
  * **Ships are one shared set for every nation** (Brian, 20 Nov 2026: detail is too hard to see at this size for national versions). Five types in side profile: carrier, battleship, destroyer, submarine (a WW2 boat with a deck gun, replacing a first try that looked modern), and a landing craft drawn by Claude after Grok struggled with it. The nation's color says whose ship it is. Ships keep the nation colors and never go navy blue (Brian, 20 Nov 2026), so color always means nation.
  * **Artillery and airborne** (decided 20 Nov 2026, Brian): one shared silhouette each, in nation colors. Artillery is Brian's Grok gun with the barrel raised (`artillery-shared.png`); airborne is a simple canopy based on the Campaigns parachute mark (`airborne-shared.svg`). **Airborne divisions get the airborne block even when fighting on the ground**, like the 101st at Bastogne. **German parachute divisions that fought as infantry keep the German helmet** unless the day is an actual drop. Shared silhouettes flip for German and Japanese blocks so the facing rule holds.
  * **Any other unit type** (engineers, tank destroyers, cavalry and so on) uses the closest existing block plus its name tag, unless a day's main action depends on that type; then the Campaign Series chat flags it to the Map Room chat.
* **Facing:** Allied silhouettes face right and German ones face left, toward each other. A series can flip this to suit its map.
* **You see them move.** A rake pushes each block, slowly enough to follow. Brian likes the rake from the film quality render (pale pole, brass collar, dark head).
* **Few pieces.** Six to eight on screen. Each day shows only the units that matter that day.
* **The front line is red grease pencil on a clear acetate sheet over the map** (decided 20 Nov 2026, Brian, replacing the red cord on brass pins, which slid on its own and ran under the blocks). The line lies flat under the blocks. The clip opens on the morning line; the blocks are pushed across it; after the last push the morning line is wiped to a faint ghost, the night's line is drawn in one stroke north to south, and the ground taken that day shades in with a light charcoal hatch. One redraw at nightfall, not one per push.
* **The series labels carry over:** the cream tab and strip in the same Oswald and Special Elite type as Day by Day.
* **Sound:** no music, ever (superseded by sound C, which adds a quiet in house theme). The clip carries the table's own sounds: wood sliding on glass, and a knock only where something touches something (see the knock rule under Sound C).
* **The map is a real traced map**, the same rule the Campaigns tables follow.
* **Rendered at film quality.** Brian: this is much cleaner and better "if we can render it like this." The film quality renderer is too slow to film every frame, so the plan is to render the table and each block once and slide the blocks in the edit. **Proven in motion, 20 Nov 2026** (first sitting, below): the plate and each block rendered once, then slid in the edit. Awaiting Brian's look.

### The mockup (19 Nov 2026)
"The Map Room Mockup: The Bulge, Day 1": a 15 second vertical clip in two looks, the wood table and a flat map for comparison, with a page that plays either one. Files in OneDrive under `WW2 Dispatches\The Map Room\Mockup 2026-11-19`.
* **What it proves:** the format reads on a phone, the pieces are recognizable by shape, the rake and the cord work, and the series labels fit.
* **What it is not:** the map is a sketch drawn from memory of the geography, and the positions are simplified. **Nothing in it has been verified and none of it may be posted.**
* **How real it looks:** it reads as a well made wooden game table, not as a photograph. If Brian wants it closer to photographic, the same day records can drive a film quality renderer instead. That is a build choice for the Map Room chat and does not change anything else here.
* **How it is made:** the table is a small 3D scene that runs in a browser. The workspace films it frame by frame and encodes the video. Because it runs in a browser, the very same scene can be the interactive table on the website. One build, both uses.
* **Superseded the same night:** the first clip's carved figures and blue and red colors were replaced by the blocks and nation colors above. Later studies in the same folder: `map-room-counter-study.jpg`, `map-room-silhouette-study.jpg`, `map-room-blocks-stained.jpg`, and the final faces sheet `map-room-block-faces.png` (the intermediate face rounds were dropped).

## Sources and accuracy
* **The daily situation maps are real and free to use.** The Library of Congress holds the HQ Twelfth Army Group situation maps: 416 printed maps showing troop positions from 6 June 1944 to 26 July 1945, one for each day, published by the United States government. The collection includes a Battle of the Bulge set. (loc.gov, World War II Military Situation Maps, call number G5701.S7 svar .A4.) Checked 19 Nov 2026.
* **What they show is what headquarters believed.** Each map records the positions as the Army Group's operations staff understood them that day, which is not always where the units truly were, least of all for German units.
* **So the rule (Proposed):** every move needs two sources, as every fact does. The official history (Cole, *The Ardennes: Battle of the Bulge*, Center of Military History, public domain) sets where a piece goes. The situation map is the second source and a storytelling tool: where the two differ, the table follows the history, and the caption may say what headquarters thought that night.
* **Scale:** pieces are armies, corps, and divisions, or a named column when one unit is the day's story. A piece's position is approximate by nature, and the caption never claims more precision than the sources give.
* **Covers the Western Front after D Day only.** For Anzio, Okinawa, Midway and the rest, each series names its own map sources in its sitting (the Army's American Forces in Action series, the Navy and Marine Corps histories, the West Point atlas).

## What we already have that feeds this
| Already built | How it helps |
|---|---|
| Campaign Series day records, renderer, and skill | The moves ride in the same record. No second research pass. |
| The 6:30 Day by Day slot and its renderer | A home for the clip with no new slot, and the opening frame comes from the existing Day by Day still. |
| The Campaign Shelf, day pages, and Chronicle chapter pages | The place the table lives on the site. Each day already has its own address. |
| Campaigns plotting tables (`bastogne_perimeter`, `alsace_moder`) and the traced map method | The Bastogne table is already traced and approved. The method and rules for tracing the Ardennes map exist. |
| Campaigns enemy cards and the machines only rule | The same thinking about showing units without people or symbols. |
| Declass sound work | The table sounds, made the same way. |
| Cloudflare R2 media hosting | Where the clips live for Buffer and the site. |
| Platform Console | Already counts clicks out of posts, views of each book page, and taps on the collect button. Every link in the path is measurable from day one. |
| The date bank and entity index (started 19 Nov 2026) | Later, every unit and place on the table links to its entity. Not needed for the Bulge. |
| Lunch Drop and the reply rotation | Carries the series story on X during the run, and can carry the clip. |

## The Bulge: what has to change
* **Less than feared.** Brian thought the Day by Day posts were mostly written. By the Campaign Series doc and the copy of the repo on the desktop (which holds only the Pearl Harbor folder), the Bulge is not built yet: the doc lists anchor days, and the build sitting is set for Thanksgiving weekend, 26 to 29 Nov. So there is nothing to go back and rework. **To confirm with the Campaign Series chat**, in case the desktop copy is behind. If posts have been written since, they stay, and each day only gains its moves.
* **The build sitting gains one step.** For each of the 30 days: the moves, checked against that day's situation map and Cole, written into the day's `mapRoom` block.
* **Day picks lean toward movement.** Most anchor days already move (the 101st races to Bastogne, St. Vith falls, the ring closes, Abrams breaks in, the two armies close on Houffalize). Home Front and Blueprint days still run: the story is told in the morning and the table simply shows that day's line in the evening.
* **Somber days stay plain.** On 17 Dec (the Baugnez crossroads) the table shows the column's advance and nothing else.
* **Flash day, 16 Dec.** The table is a map, so it does not touch the Flash card's moment. As Day 1's 6:30 post it opens the day, ahead of the Flash card at 8 a.m.
* **The Chronicle's four parts** are written in short sittings ahead of each date, as planned. Each part's sections already match one day each, which is exactly what the stepping table needs.
* **Campaigns days.** On 1 and 11 Jan the series post carries a Campaigns line. The table on 1 Jan can close in on the Bastogne perimeter, the same ground as the game's chapter 1 table.

## Who does what (Proposed)
* **A new pinned chat, "Campaign Series: The Map Room", with its own skill.** It owns the table scene, the piece set, the map tracing, rendering, sound, and scheduling the clips. Recommended over folding it into the Campaign Series chat, which is already long and would have to carry a 3D renderer on top of research and writing. It follows the pattern already used for Campaigns (planning, build, and card design in separate chats).
* **The Campaign Series chat and skill** gain one step: write the `mapRoom` block for each day in the build sitting. The docs carry the handoff, so nothing is copied between chats.
* **Website: Build and Fixes chat** owns how the site shows the table (day pages first, then the stepping table in Chronicle chapters).
* **Campaigns Card Design chat:** no new work. Its Bastogne table is reused.
* **Brian:** three approvals (the gates below) and his usual review of the Bulge sitting. No daily work. Clips are built and scheduled for the whole series in one go.

## Roadmap
Today is Thu 19 Nov 2026. Bulge Day 1 is Wed 16 Dec. That is 27 days.

| When | What | Who |
|---|---|---|
| Thu 19 Nov | Mockup and this doc. | Done |
| **By Sun 22 Nov** | **Gate 1: the look.** Brian picks wood or flat, and answers the open decisions below. | Brian |
| Mon 23 to Wed 25 Nov | Map Room chat and skill set up. The real template built: Ardennes map traced, piece set, rake, grease pencil line, sounds. Day 1 rendered at full size as the proof. (Code Room launches Tue 24 Nov; this needs nothing from Brian.) | Map Room chat |
| Thu 26 to Sun 29 Nov | The Bulge build sitting as planned, with each day's moves added to its record. | Campaign Series chat |
| Mon 30 Nov to Fri 4 Dec | All 30 clips rendered. One proof sheet. **Gate 2: Brian watches Days 1 to 5.** If the look or the pace is wrong, it is fixed once in the template and all 30 are rendered again. | Map Room chat, Brian |
| Mon 7 Dec | Pearl Harbor Flash day. Nothing for the table. | |
| By Wed 9 Dec | All 30 clips uploaded and scheduled in Buffer at 6:30, 16 Dec to 14 Jan, on all six channels. Day pages show each day's clip. | Map Room chat, Website chat |
| Fri 11 Dec | Campaigns go or no go for January (already set). | |
| **Wed 16 Dec** | **Day 1 at 6:30 a.m.** | |
| **Wed 23 Dec** | **Gate 3: the first week's numbers** (below). Keep, adjust, or stop. | Platform Console, Brian |
| About 24 Dec | Chronicle Part 1 goes live, with the table stepping through its days if the Website chat has it ready. If not, it follows with Part 2. | Website chat |
| Fri 1 Jan | Campaigns chapter 1 opens at Bastogne. The table and the game share the ground. | |
| By Sun 10 Jan | Decide whether Anzio (landing 22 Jan) gets a table, in time for its sitting. | Brian |
| Thu 14 Jan | Last day. Full review of the run. | |

**If it slips or fails a gate:** the Bulge Day by Day runs as photo posts on X, Threads, Instagram, and Facebook, exactly as Pearl Harbor did, and the day records already written still work. Nothing else depends on it. **Deadline for that call: Fri 4 Dec**, so the photo posts can still be scheduled in time.

## Measuring
Read at Gate 3 and again at the end, against the same slots in the weeks before:
* **Follows on series days** against ordinary days, by platform. This is the number the table exists to move.
* **Hold on the clip** (how long people watch) against the noon and 7 p.m. Living Cards, from the Scoreboard.
* **Day by Day as a video against Day by Day as a photo** (Pearl Harbor), on the four platforms both ran on.
* **YouTube and TikTok:** the series' first time there, so watch follows on those two.
* **Clicks out of Map Room posts** to the book, **views of the day pages and chapters**, and **taps on the Declass button**, from the Platform Console.
* Do not judge on one week alone if the counts are small. Gate 3 can also say "too early, keep going".

## Open decisions for Brian
1. ~~The look~~ **Decided 19 Nov 2026:** wood table, dark stained blocks.
2. ~~The name~~ **Decided 20 Nov 2026:** The Map Room.
3. ~~The slot~~ **Decided 20 Nov 2026:** option B, the Day by Day post becomes the clip.
4. ~~Colors~~ **Decided 19 Nov 2026:** one color per nation (see The look).
5. ~~A pointer to the book~~ **Decided 20 Nov 2026:** yes (see below).
6. ~~The chat~~ **Decided 20 Nov 2026:** a new pinned "Campaign Series: The Map Room" chat; skill written last.


## Decisions and open questions, 20 Nov 2026 (morning, with Brian)
* **Pointer: yes.** Every Map Room post ends with one line pointing to the series book on ww2dispatches.com (Instagram and TikTok: "link in bio"). An exception to the series' "no add on lines" rule, for Map Room posts only.
* **No narration.** Brian leans against it (he never liked the Onyx voice: too slow, not upbeat). On screen text and the caption carry the story; the clip must work muted.
* **Sound: decided 20 Nov 2026, version C** (Brian): table sounds, the war room bed (teletype, clock, faint static), and the quiet in house theme (slow piano and low strings, original, generated in code). Plus a wipe and a grease pencil drag for the nightfall redraw. No narration. **No knock when a pushed block stops** (Brian, 20 Nov 2026: nothing hits anything, it just slows on the glass). The push sound follows the block's speed and fades out duller as it stops; the rake's contact tap is lighter. **The knock rule** (Brian, 20 Nov 2026): a knock only when something touches something, the rake meeting a block or a block pushed into another block. Nothing else knocks: not a block stopping, not hold, not arrive. Test: `Day 1 Test 2026-11-20\map-room-bulge-day01-test-quiet-stop.mp4`.
* **Slot: decided, option B.** The options were (A) 7 p.m. on series days, replacing the second video; (B) merge into the 6:30 Day by Day post, which becomes the Map Room clip with the day's story caption on all six channels, opening on the day's archival photo for about a second before the table; (C) 6:30 on YouTube and TikTok only, Day by Day unchanged elsewhere; (D) a new evening slot; (E) one weekly recap instead of daily. Brian chose B (reasons under "How it ties into the Campaign Series").

## Start here: the Map Room chat
A pinned chat, "Campaign Series: The Map Room", owns the Map Room from here. This section is its brief. Read the whole doc first.

**Where the build chat picks up (20 Nov 2026).** This planning and test chat is closed. The look, the render once and slide method, the grease pencil line, sound C, the move set, and the label rule are all decided (above and in "First sitting result"). The finalized chat starts from the method files and does the rest.

**Setup when creating the chat:** nothing to select for the repo. As the Project Brief says, the chat attaches `ww2dispatches/ww2dispatches-cards` itself with add_repo (push access) and clones it. If that call is refused, as it was in the planning chat, the chat stops and asks Brian to approve it. Connect the `WW2 Dispatches` OneDrive folder (laptop `C:\Users\brian\OneDrive\Personal\Claude\WW2 Dispatches`, desktop `D:\OneDrive\Personal\Claude\WW2 Dispatches`). Blender runs in the workspace as the Python package (`pip install --break-system-packages bpy`, about 430 MB).

**Method files:** `The Map Room\Kit\map-room-method-files-2026-11-20.zip`: `scene.py` (Blender scene: plate, blocks, masks, rake, camera), `comp.py` (the compositor: slides the sprites, draws the grease pencil line and hatch, overlays, encodes), `faces.py` (block faces from the silhouette kit), `ov.html` (the Day by Day tab and strip, drawn in headless Chrome with the repo's fonts), `maproom_sound.py` (sound C, generated in code), `day01.json` (the test record, unverified positions), and the sound stems. The approved test clip is `Day 1 Test 2026-11-20\map-room-bulge-day01-test-grease-c.mp4`.

**Order of work**
1. Commit the method files into the cards repo (pick the folder, record it here) and apply the template fixes: render blocks with room past the frame, draw the rake before its block, refuse blocks that start off screen.
   * **Done 20 Nov 2026, pushed to main** (commits 79364ad and 6045826, with a repo copy of this doc in `docs/`). Folder: `map-room/` at the top of the cards repo (`engine/` scripts, `kit/silhouettes/` with `library.json`, `fonts/`, `test/` Day 1 record and sketch map, a README with the run order). Renders never go in git; day records stay in `campaign-series/<series>/day-NN.json`. Fixes made and proven on a re-rendered Day 1 test clip (`Day 1 Test 2026-11-20\map-room-bulge-day01-test-fixes.mp4`, sound C): every sprite renders on a padded frame (270 px each side, 240 px top and bottom) over a padded plate, so a block at the edge stays whole; the rake is drawn just before the block it pushes, with a 0.12 gap (was 0.07); the pre render check refuses any block partly off screen where it starts or ends, judged at the end of the push in, with arrive moves exempt at their start. The check caught the test record's 7th Army start, the original edge problem, so that start moved from 6.55 to 6.50 E (test record only). Also added `engine/ov_shoot.py`, the missing overlay driver.
   * **Repo access:** approved by Brian 20 Nov 2026. The patch and folder zip in OneDrive `The Map Room\Kit` are now only backups.
2. **By Wed 25 Nov:** final `mapRoom` block format and a short brief for the Campaign Series chat (move types, full names under 16 characters, morning and night line points, blocks clear on their own side and inside the frame, two sources per move). Update the handoff line in the Campaign Series doc's Open section.
   * **Done 20 Nov 2026, pushed to main.** `map-room/FORMAT.md` (format and brief), `map-room/engine/check_record.py` (the checker, tested against every rule), `map-room/engine/view.json` (the fixed camera, so the checker runs without Blender), `map-room/series/bulge-1944/table.json` (the Bulge framing, provisional until step 4), and `map-room/test/day01-example.json`. The Campaign Series doc's handoff clause (1) now points to the format and the checker. `scene.py` and `comp.py` move onto the table framing and the new block in step 3.
3. Build the move animations not yet made (arrive, hold, cut off, surrender, air mission, grounded) and the clip template (beats, safe areas, loop), plus the pre render check and contact sheet.
4. **By Wed 25 Nov, before the Bulge sitting:** trace the real Ardennes map from the Library of Congress situation maps and Cole, covering the whole table area in `map-room/series/bulge-1944/table.json`, and the Bastogne close view in `table-bastogne.json` (from the same sources as the Campaigns `bastogne_perimeter` table), and confirm both framings; show Brian one still of each before rendering with them. In the clip template (step 3), a close view day opens on the whole battle for a beat and pushes in to Bastogne, so viewers always know where they are; Brian judges that at Gate 2.
5. After the Bulge sitting (26 to 29 Nov): **check the positions against the record** (added 20 Nov 2026, Brian): using the situation maps already opened for the tracing in step 4, compare each day's block positions and lines with that day's Library of Congress situation map. This is a second look, not new research: anything that looks wrong goes back to the Campaign Series chat to fix in the day record, never changed here. Then render all 30, Gate 2 (Days 1 to 5 by Fri 4 Dec), upload to R2, schedule all 30 in Buffer at 6:30 on all six channels by Wed 9 Dec.
6. Write the Map Room skill last, from what worked.

**What it owns:** the table scene, the block set, map tracing, the clip template, sound, rendering, the pre-render check, and scheduling each Map Room post in Buffer. It does not research or write the stories (the Campaign Series chat does) and does not build site pages (the Website chat does).

**What it starts with**
* The silhouette kit: `WW2 Dispatches\The Map Room\Kit` in OneDrive. `Silhouettes` holds 30 silhouettes named by type and nation (cream PNGs, and black SVGs that the face maker converts) plus `library.json` (colors, file map, rules); `map-room-working-files-2026-11-20.zip` holds the working files from the mockups (the browser scene, the film quality scene, face sheets).
* The approved look: `map-room-block-faces.png` (faces) and `map-room-blocks-stained.jpg` (dark stained blocks under the lamp) in `WW2 Dispatches\The Map Room\Mockup 2026-11-19`.
* The repos, attached the same way the other build chats attach them (the cards repo for the code and files; clips go to Cloudflare R2 like the videos).

**First sitting: prove the method**
1. Render the table and each block once at film quality, then make the Day 1 clip by sliding them in the edit. If that does not look right in motion, stop and report before building anything else, since the answer changes the format rules.
2. Make it in three sound versions for Brian: table sounds only; table sounds with a war room bed (teletype, clock, faint static); both with a quiet in house theme. No narration in any.
3. Open on the Day 1 still in the Day by Day frame for about a second, then the table.

**Then, by Wed 25 Nov**
* The fixed set of moves, each with one standard animation: advance, fall back, arrive, hold, cut off, surrender, air mission.
* The `mapRoom` block in the day record, final, and handed to the Campaign Series chat before its Bulge sitting (26 to 29 Nov).
* The clip template: length, opening and closing beats, safe areas for each platform, loop.
* Label rules: a character limit and standard abbreviations so every unit name fits a block.
* The pre-render check: every block on the map, on the right side of the line, not overlapping, name fits; then one contact sheet per series for Brian.
* Where files live in the repo.

**After the Bulge sitting:** check each day's positions against its situation map (step 5), make the sound kit, render all 30, show Brian Days 1 to 5 (by Fri 4 Dec), schedule all 30 by Wed 9 Dec. Write the skill last, from what worked.

**Rules that hold:** one silhouette per nation per type; Tiger only when the day's story names one; ships, artillery and airborne shared, in nation colors; airborne divisions on the airborne block, German parachute infantry on the helmet; no flags, insignia, regime symbols, or SS names; every move needs two sources; no dashes in anything written.

**First sitting result (20 Nov 2026, Map Room chat)**
* **Method works.** One film quality plate of the empty table (Blender Cycles, about 3 minutes), each block rendered once with its own shadow and reflection (about 1 minute each), the rake and a brass pin the same way. The edit slides them in 2D and draws the red cord between the pins. A full 16 second clip composites in under 2 minutes, so all 30 days are cheap once the plate exists. Small limit: a sliding block keeps the perspective of its starting spot, which is invisible over moves of this size; a very long move would need the block rendered at both ends.
* **Clip as built:** 16 s, 1080 x 1920, 30 fps. 1.1 s on the Day by Day still, a 0.4 s dissolve to the table, three pushes (rake slides in, meets the block, pushes, withdraws), the cord shifts after each push, a slow 3.5% push in on the table, and at 13.3 s the strip changes to the closing line. Tab top left at 110 px, strip bottom edge 330 px up, both clear of phone app buttons.
* **Three sound versions** (all generated in code, original, no narration): A table sounds only (slide on glass, rake tap, block knock, faint room hum); B adds the war room bed (distant teletype, clock, faint static); C adds a quiet in house theme (slow piano and bowed low strings in D minor, ending open on A for tomorrow).
* **Test only, nothing posts:** the map and positions are still the 19 Nov sketch, and the opening still is a placeholder (the Flash card's photo in grayscale). The real Day 1 still and moves come from the Bulge sitting. Every frame carries a TEST stamp.
* **Files:** clips and a still in OneDrive `The Map Room\Day 1 Test 2026-11-20`; the scripts (scene, compositor, faces, sound, overlay page) and sound stems in `The Map Room\Kit\map-room-method-files-2026-11-20.zip`.
* **Brian's review (20 Nov 2026):** sound C chosen. The cord was rejected (it moved on its own and slid under the blocks) and replaced by the grease pencil line with one redraw at nightfall; rebuilt the same morning as `map-room-bulge-day01-test-grease-c.mp4` (17.5 s). Next: the move set, `mapRoom` block, template, label rules, and pre render check by Wed 25 Nov. The cards repo could not be attached with push access from that chat; fixed in the build chat on 20 Nov 2026.

* **Decided with Brian, 20 Nov 2026 (later):**
  * **The move set:** advance and fall back (the rake push); arrive (slides in from the map edge); hold (stays, with no sound and no tap; changed 20 Nov 2026 under the knock rule); cut off (a grease pencil ring drawn around the block); surrender (the rake drags the block off the map); air mission (the aircraft block slides out and back); grounded (stays, with GROUNDED pencilled beside it).
  * **Labels:** full unit names, never short forms, so the clip teaches people who do not know them. Only a name over 16 characters is shortened.
  * **Length:** no hard limit. Keep it fluid and judge by the numbers. The Day 1 test runs 17.5 s.
  * **Template fixes from the test:** every block is rendered with room past the frame edges (as the rake already is), so a block that starts near the edge stays whole; the rake is drawn before the block it pushes, with a little more gap; the pre render check refuses any block that starts partly off screen.
  * **The Bulge is not written yet** (Brian checked with the Campaign Series chat). The Campaign Series sitting (26 to 29 Nov) still writes the stories and each day's moves in one research pass, as its Open section already says; the Map Room chat hands it the final `mapRoom` format and a short brief by Wed 25 Nov.
**Starter line for Brian to paste:** "You are Campaign Series: The Map Room. Read the WW2 Dispatches Map Room doc, all of it, then pick up at Where the build chat picks up in its Start here section, step 1."

## Handoffs
Lines for other chats. Nothing here is live until Brian approves this doc.
* **Campaign Series chat:** a handoff line is in its doc's Open section (20 Nov 2026). Before the Bulge sitting: Day by Day becomes the Map Room clip on all six channels; each day record gains a `mapRoom` block (format final 20 Nov 2026: `map-room/FORMAT.md`); the sitting does not schedule Buffer.
* **Website: Build and Fixes chat:** after approval, show each day's table on its day page, then the stepping table in Chronicle chapters.

## Changelog
* 20 Nov 2026 (Map Room build chat): Bastogne close view added (Brian): optional `view` in the record, `series/bulge-1944/table-bastogne.json`, checker and `FORMAT.md` updated. Front line rule corrected so a line can follow the Bulge around (north end to south end, German ground on the left). Step 4 now traces both maps.
* 20 Nov 2026 (Map Room build chat): artillery and airborne blocks added (Brian): one shared silhouette each in nation colors; airborne divisions use it even on the ground, German parachute divisions fighting as infantry keep the helmet; any other type uses the closest block and its name. Kit, face maker (SVG support, shared silhouettes flipped for Axis), checker, and `FORMAT.md` updated.
* 20 Nov 2026 (Map Room build chat, step 2): `mapRoom` format final in `map-room/FORMAT.md`, with the checker and a per series table framing (the Bulge framed to show the whole battle; a block covers about 27 km). Campaign Series doc handoff updated. Steps 4 and 5 wording tidied: the map is traced before the sitting, the positions are checked after it.
* 20 Nov 2026 (Map Room planning chat): added the position check against the daily situation maps to the build chat's order of work (step 5). Repo copy in `docs/` synced to this version the same day by the build chat.
* 20 Nov 2026 (Map Room build chat): knock rule set by Brian: a knock only for rake to block or block to block contact. Hold loses its tap; arrive has no knock of its own.
* 20 Nov 2026 (Map Room build chat): stop knock removed from pushes at Brian's call; push sound now follows block speed. Pushed to main.
* 20 Nov 2026 (Map Room build chat, step 1): method files set up as `map-room/` in the cards repo with the three template fixes, proven on a re-rendered Day 1 test clip. Pushed to main after Brian approved the repo attach.
* 20 Nov 2026 (Map Room chat, close): planning and test chat closed; Start here rewritten as the brief for the finalized build chat (setup, method files, order of work, new starter line).
* 20 Nov 2026 (Map Room chat, later): Move set, full name labels, no length limit, and the edge and rake fixes decided with Brian; the Bulge confirmed unwritten.
* 20 Nov 2026 (Map Room chat, Brian's review): Sound C chosen. Front line changed from a red cord on pins to grease pencil on acetate, redrawn once at nightfall with the day's gain hatched.
* 20 Nov 2026 (Map Room chat, first sitting): Film quality render once and slide method proven on the Day 1 test clip; three sound versions made for Brian to judge. Files in OneDrive.
* 20 Nov 2026 (morning, later): Renamed everywhere from The Table to The Map Room (Brian): this doc moved to "WW2 Dispatches Map Room", the day record block renamed `mapRoom`, the OneDrive folder and every file renamed, the mockup clips and sheets re-rendered with the new label, intermediate face rounds dropped, the mockup page retitled.
* 20 Nov 2026 (morning): Named The Map Room. Pointer line approved. No narration. Sound to be judged on three Day 1 test versions. Slot decided: option B, the Day by Day post becomes the clip on all six channels. Handoff brief written for the new Map Room chat; handoff line added to the Campaign Series doc.
* 20 Nov 2026 (after midnight): Ten aircraft and four ships from Brian added, plus Claude's landing craft. Decided: ships are one shared set in nation colors; Panzer IV is the German tank and the Tiger is for special occasions; B 29 and Claude's C 47 added. Final sheet: `map-room-block-faces.png`.
* 19 Nov 2026 (late night): Counter studies with Brian. Decided: dark stained wooden blocks, one color per nation, helmets for infantry and one tank per nation from Brian's Grok silhouettes, three aircraft roles, film quality rendering. Figures, card counters, blue and red, and all soldier figures rejected.
* 19 Nov 2026: Doc created after Brian's voice session and his request for a layout and roadmap. Situation maps confirmed at the Library of Congress. Mockup made for Bulge Day 1 in two looks. Everything Proposed.
