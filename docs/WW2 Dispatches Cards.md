# WW2 Dispatches: Cards

The rules for the two daily cards: the **8 a.m. story dispatch** and the **5 p.m. evening card**. The Friday cards run follows this doc. The events, numbers, facts, photos, and evening formats are chosen and verified by the Wednesday research run (Research doc); this doc covers turning them into cards. Shared setup (series, brand, writing rules, photo rules and workarounds, Buffer channel IDs, Schedule Board tasks, record keeping) is in the Project Brief. The slot layout is in the Roadmap's "Posting schedule at a glance". The noon video is in the Videos doc. What the analytics have taught so far is in `analytics/playbook.md` (Analytics doc).

## The batch
Two cards a day, every day, on X, Instagram, Threads, and Facebook through Buffer:
* **8:00 a.m. Mountain: the story dispatch**, with the long story caption.
* **5:00 p.m. Mountain: the evening card**, in one of three formats (Photo of the Day, Quote of the Day, Spec Sheet) with a shorter caption.

The Friday run does 14 cards for the coming Sunday through Saturday, from the dispatch JSON the Wednesday research run wrote. It never schedules a card at noon (the daily video) or at 10 a.m. on Wednesday or Saturday (Name This). It checks Buffer first so a slot that is already scheduled is never duplicated.

## Events, numbers, and facts come from research
The Research doc owns picking the events (film first for the 8 a.m. slot), the series mix, the never repeat rule, the big dates, the fact sheet (`facts`), the sources, and the dispatch numbers. The cards run reads the week's slate and dispatch JSON and builds on them. It never changes an event, a number, or a verified fact. If the slate and dispatch files for the week are missing, follow "If a run fails" in the Research doc.

## Photos for cards
* Research downloads the lead photo for every card into `photos/` (Research doc). The cards run sets the framing (focusX, focusY, zoom) and looks at the result.
* **If a card's photo is still missing on Friday night** (a Brian task still open), use a dispatch from the bank in that slot and say so in the summary. Never leave a slot empty.

## The post card (locked)
The big WWII accounts (@VoicesofWW2, @I_W_M, @The_PacificWar, @RealTimeWWII) post a plain archival photo with a caption, no designed card. A branded card stands out in that feed.

Style: **photo with Field Telegram band**. The archival photo is the hero; cream bands frame it.
* **Top band:** "WW2 DISPATCHES" wordmark on the left with "Dispatch No. 001" under it in Special Elite and ink navy, no logo mark (the WW2 badge already shows as the profile picture beside every post, and a badge in the band read as duplicate words). Evening cards add their format after the number ("Dispatch No. 004 · Photo of the Day"). Series stamp on the right, tilted slightly, in the series accent color.
* **Bottom band:** big date in Oswald (for example "20 OCT 1944"), place line under it in Special Elite and ink navy, optional short pull line at right in the series color, and the handle "@ww2dispatches" small in Special Elite and ink navy in the bottom right corner so screenshots and reposts point back to the account.
* **X image bottom room:** X draws an ALT badge in the bottom left corner of every image that has alt text (about 160 x 95 px on the 1600 x 1440 card), which covered the place line. So the X image has extra paper at the bottom of the bottom band (5% of the card width), and the date, place, pull line, and handle all sit above it. The top band stays the same so the photo stays as large as possible (Brian chose this over matching the top margin). The 4:5 image keeps the normal layout. `renderer/card.html` handles this on its own.
* **Paper texture: grain.** Fine paper fiber texture on the cream bands, slightly darker aged edges, and a roughened rubber stamp look on the series stamp. No perforated edge.
* **Per post, only these change:** photo, dispatch number, date, place, series, the format label and photo window on evening cards, and the optional pull line.
* **Sizes:** X image 1600 x 1440; Instagram image 1080 x 1350 (4:5 portrait), also used for Threads and Facebook.
* First mockup: Leyte landing, October 20, 1944 (MacArthur at Red Beach, NARA 531424).

## The Flash card (decided 25 Oct 2026)
The rare fifth card type, for the war's biggest days (Roadmap, "Flash cards plan"; the research rules are in the Research doc, "Flash days"). A Flash dispatch has `"series": "flash"` and `"flash": true`, and its `photo` points at prepared, approved full art in `flash/`. The Friday run treats it like any 8 a.m. dispatch except for the points below.
* **Full art, not the Field Telegram bands.** `renderer/card.html` draws it edge to edge (`drawFlash`): the art fills the whole card, with a dark fade at the top carrying the wordmark and "Dispatch No. NNN · Flash" on the left and a cream FLASH tape stamp on the right, and a dark fade at the bottom carrying the big date, the place line, the pull line in gold at right, and the handle. No paper, no grain, no series stamp. The X image keeps X's ALT badge corner clear by lifting the bottom block. The same renderer command makes both sizes: `node renderer/render.js <id>`.
* **Never change the art or the framing.** The art is already colorized and approved by Brian; the prepared record sets focusX, focusY, and zoom. Look at both rendered images as usual.
* **Caption:** the normal long story caption from the `facts` block, hook first. Pearl Harbor is somber, so no engagement question, soft ask, or newsletter mention. Instagram may add the event hashtag after `#OnThisDay #WW2` (for example `#PearlHarbor`); X and Facebook swap #OnThisDay for it (`#OTD #WW2 #PearlHarbor`), per the anniversary rule below.
* **Alt text** begins "WW2 Dispatches card, Dispatch No. NNN, Flash." The photo credit line in the caption or alt text says the photo is colorized, as the record's `photoCredit` does.
* **Carousel:** a Flash day is a natural carousel day on Instagram, with the real black and white archival photos of the event as the extra slides (never a second colorized image).
* **The Declass game** gives the Flash card out as always Top Secret, with no serial, in that day's commemorative file (Envelope doc). Nothing extra for this run to do; the catalog rebuild carries the `flash` field.

## Dispatch numbers (one serial)
* The dispatch number counts up by one with every card, 8 a.m. and 5 p.m. alike, in the order they post (date, then time). It counts cards, not events.
* **Numbers are assigned and locked by the Wednesday research run** (Research doc). The cards run never renumbers; by Friday the numbers are already rendered into the week's videos.
* A noon video shares the number of the 8 a.m. dispatch it covers. Name This and the welcome post never take a number.
* **Once a card has posted, its number never changes.**
* At 14 cards a week the serial passes 999 around late 2027; the renderer already handles four digits.

## Evening cards (5 p.m.)
Same card frame, bands, stamp, date, place, and handle as the 8 a.m. card; only the photo window and the format label change, so every post reads as the same brand. Each still ties to that calendar date and carries one of the four series stamps. **Research picks the format and verifies the quote or the spec rows; Friday renders them.**
* **Photo of the Day** (`"format": "photo"`): a striking archival photo with a short caption. Nearly identical to the morning card; the label next to the number is the difference.
* **Quote of the Day** (`"format": "quote"`): the photo dimmed, the quote set large in Special Elite in cream, a short series color rule, and the speaker and occasion under it in Oswald. Fields: `quote`, `quoteBy`. The quote must be **verified word for word** against a reliable source, spoken or written on that date, and short enough to read at feed size (aim under 30 words).
* **Spec Sheet** (`"format": "spec"`): the photo in the top half of the window, a datasheet panel below with a title (`specTitle`) and up to six rows (`specs`: [[label, value], ...]) in two columns on the X card. Use it **whenever a machine, weapon, ship, aircraft, or system genuinely shaped that day's events**, not only on first flights or launches. Brian wants these often. **Every number must agree across sources; if sources disagree, leave that row out.** Usually Blueprint, but any series fits (a Home Front ration chart, a Battle Lines order of battle).
* **Mix** the three across the week, with **at least two Spec Sheets a week** when the dates allow. No fixed weekday per format.
* A Spec Sheet or Quote can cover a slot where a story photo is missing.

## Caption style
Every card gets a full story caption, **written only from the dispatch's `facts` block** (Research doc). Never add a fact; if one is missing, write around it. **Hook first, always.** The opening line or two must grab a scroller on its own: a surprising fact, a vivid image, a twist, or the stakes. The X feed shows only about the first 280 characters before "Show more", and Instagram shows even less before "more", so the hook has to work alone. **Never open with the bare date.**
* **8 a.m. dispatches:** X, Instagram, and Facebook share the same long caption, **about 750 to 1,200 characters**. Structure: the hook, then a paragraph that starts with the date written out (for example "17 October 1941.") and tells what happened, then two or three short paragraphs with why it mattered, one vivid human or technical detail, and what came next. Then the hashtags.
* **5 p.m. evening cards:** shorter, **about 450 to 750 characters**, same rules (hook first, the dated paragraph, one strong detail). A Spec Sheet caption explains why the machine mattered that day; a Quote caption gives the context and repeats the quote.
* **Threads:** a trimmed version **under 500 characters** (the hook, the date and core story, one strong detail), no hashtag.
* Short paragraphs, plain words, no dashes. The sources are already listed in the dispatch JSON by research.
* **What goes where in the JSON (since 24 Oct 2026):** `body` holds **the story only**, nothing after it. Any add on line (an engagement question, the Ko-fi soft ask, the newsletter mention, later the Declass line) goes in `addons`, a list of strings in the order they are posted. The hashtag line goes in `hashtags` as the Instagram ending (for example "#OnThisDay #WW2"). The Threads version stays complete in `threads` (it never carries hashtags). The Declass game reads `body` as the story, which is why the extras live apart from it.
* **The Buffer caption is joined only when scheduling:** `body`, then each `addons` line, then the hashtag line, each separated by a blank line. X and Facebook swap the hashtag line per the Hashtags section. Nothing that has posted changes.
* **Fixes go to the record first.** When a Saturday review change (or any later fix) edits a caption, edit the JSON first (`body`, `addons`, `threads` as the case may be), then swap the Buffer post from the rejoined text. The record and the post must never differ.

## Hashtags and the Threads topic
* **Instagram:** ends `#OnThisDay #WW2`.
* **X and Facebook:** the same caption, but end `#OTD #OnThisDay #WW2` (#OTD is the tag historians and archives use most). The JSON `hashtags` field keeps the Instagram ending; swap it when scheduling X and Facebook.
* **Threads:** no hashtag. Every Threads post is filed in the **History Threads** community through Buffer's topic field (see the Brief's Buffer setup). Older JSON `threads` fields may still end with #OnThisDay; ignore that ending when scheduling.
* **Anniversary days:** Instagram may add one event hashtag after `#OnThisDay #WW2` (for example #PearlHarbor or #VeteransDay). X and Facebook stay at three tags by swapping #OnThisDay for the event tag (for example `#OTD #WW2 #PearlHarbor`).

## Growth rules
These add no time for Brian; the Friday run applies them. **None of them ever goes on a dispatch research marked `somber`.** Every add on line is stored in the JSON `addons` list (never inside `body`) and the matching flag (`question`, `soft_ask`, `newsletter_mention`) is set true, so the analytics and the next run can see what ran.
* **Engagement questions:** close some captions with a short open question, as the last line before the hashtags. Two or three a week, never on back to back days, so it never reads like a formula. Good questions invite family stories, opinions, or a guess ("Did anyone in your family work in a wartime factory?", "Would you have trusted this machine?", "Which do you think mattered more, the code breakers or the convoys?"). One plain line. Never on somber dispatches. Never in the same caption as the Ko-fi soft ask or the newsletter mention. The Threads version carries the same question and must still fit 500 characters; trim the story, not the question. Record `question: true`. Comments get answered under the reply plan.
* **Instagram carousels:** where good extra public domain photos of the same event exist, the Instagram post becomes a carousel. Aim for two to four a week; never pad with weak or unrelated photos. Story Card days already have four to six photos downloaded by research (`videoPhotos`), so they are the natural carousel days. Slide 1 is always the normal card (cards/dispatch-NNN-instagram.jpg). Slides 2 to 4 are extra archival photos of the same event, same licensing rules. Add a `slides` array to the JSON: [{photo: "photos/<id>-2.jpg", caption: "short line, two lines max", credit: "source, record number"}]. Render with `node renderer/slides.js <dispatch-id>`, which writes cards/dispatch-NNN-slide-2.jpg and up (1080 x 1350, cream paper, the whole photo with no crop, caption and credit under it, "Dispatch No. NNN · 2 / 3" at top). Check each slide visually. In Buffer, the Instagram post gets the card first, then the slides in order, each with its own alt text; the card's alt text still starts "WW2 Dispatches card, Dispatch No. NNN, <Series>." X, Threads, and Facebook keep the single card.
* **Ko-fi soft ask:** about once every three weeks, add one soft ask to a single dispatch caption on X, Instagram, Threads, and Facebook, as the last line before the hashtags: "Enjoy these? You can buy us a coffee at the link in our bio." Pick an upbeat or fascinating dispatch (Blueprint and Home Front work well). Never on a somber dispatch. The Threads version must still fit 500 characters with the ask; trim the story, not the ask. No Ko-fi URL in captions. Record `soft_ask: true`; the newest dispatch carrying it shows when the last one ran, so the next lands about three weeks later.
* **Newsletter mention:** about once every two or three weeks, end one dispatch caption on X, Instagram, Threads, and Facebook with "Want one great story from the war in your inbox every Sunday? The free Weekly Dispatch is at the link in our bio." (reworded 30 Oct 2026 for the article format) as the last line before the hashtags. Same rules as the soft ask: never on a somber dispatch, never in the same caption as the soft ask or an engagement question, and **never in the same batch week as the soft ask**. The Threads version must still fit 500 characters; trim the story, not the line. No Substack URL in captions. Record `newsletter_mention: true`; the newest dispatch carrying it shows when the last one ran.
* **Sunday share post (separate, since 31 Oct 2026):** each newsletter issue also gets its own Sunday 1 p.m. post with its own card (rules in the Newsletter doc, "Sunday share post"). It is not a dispatch: no number, no `dispatches/` record, never in Declass. It does carry the Substack link on X, Threads, and Facebook; the no URL rule above is for dispatch captions only.
* **Newsletter launch announcement:** written by the Friday cards run per the Newsletter doc.
* The start dates for each of these are in the Roadmap's First month section.

## Building and scheduling the cards
1. Open the dispatch JSON research wrote in `dispatches/` (it already has the number, date, `time`, series, title, `short`, place, pull line, `format` and its fields, `facts`, sources, photo with `photoCredit`, and `themes`). Add `body` (the story only), `addons`, `hashtags`, `threads`, and the framing (focusX, focusY, zoom). The photo is already in `photos/`.
2. **Leave the `themes` block as research tagged it**, and leave out `video`; the Thursday run adds that.
3. Render with `node renderer/render.js <id>`; the `format` field picks the layout. File names: cards/dispatch-NNN-x.jpg (1600 x 1440) and cards/dispatch-NNN-instagram.jpg (1080 x 1350).
4. **Look at every card image**, adjust framing if needed, commit and push, and confirm the raw links return the new images. Apply the `?v=` rule if a file name was reused.
5. Schedule each card in Buffer on X, Instagram, Threads, and Facebook at its time. X gets the X image; Instagram, Threads, and Facebook get the Instagram image. X, Instagram, and Facebook carry the long caption joined from `body`, `addons`, and `hashtags` (Caption style); Threads carries `threads`. **Alt text must begin "WW2 Dispatches card, Dispatch No. NNN, <Series>."** Use each channel's metadata from the Brief.
6. Record the Buffer post ids under `buffer` {x, instagram, threads, facebook}, beside any film keys the Thursday run already wrote there. The analytics match posts by these ids, so if a post is ever deleted and redone, record the new id.
7. **Upload the board pictures:** a review copy of every new X card, Instagram card, and slide goes to the Schedule Board's asset store and its `images` collection (Brief, "Shared run procedures", Board pictures), so Brian sees the cards on the board Saturday morning. Do the same for any card swapped later.
8. Rebuild the series log (Brief, "Record now, use later").
9. In the summary, say which playbook items and active tests the batch applied.

## Dispatch bank
A few verified, evergreen dispatches (inventions, home front stories), aim for 5 to 7, kept in `bank/` and listed in `status.md`, to drop into any slot whose photo is still missing on Friday night. The research run owns the bank (Research doc); the cards run uses it and removes what it used.

## Changelog
* 15 Oct 2026: Post card locked (photo with Field Telegram band, grain texture, handle in the bottom band, no logo mark). Long story captions replaced the 280 character rule.
* 16 Oct 2026: Two cards a day, the three evening formats, and one serial for every card. Engagement questions, carousels, the anniversary plan, and the soft ask rule added.
* 17 Oct 2026: X captions end #OTD #OnThisDay #WW2; Facebook the same that evening.
* 18 Oct 2026: Threads dropped #OnThisDay for the History Threads topic.
* 19 Oct 2026: Cards moved to their own Thursday run; `videoPhotos` handoff added. Rules moved here from the Project Brief.
* 21 Oct 2026: From Brian's screenshot of the B-17 Name This post, X's ALT badge covered the place line. The X image got extra room at the bottom of the bottom band (bottom only, to keep the photo large). Starts with the Thursday 22 Oct run; cards already scheduled were left as they are.
* 21 Oct 2026 (night): The Thursday run now reads `analytics/playbook.md` before picking events and tags each dispatch's `themes` (Analytics doc). Test A starts with this week's batch: the next two Spec Sheets open their captions with the human stakes, then the machine.
* 23 Oct 2026: Step 7 added: the run uploads review copies of the cards and slides to the Schedule Board, so Brian reviews the pictures there instead of in Buffer.
* 24 Oct 2026 (evening): For the Declass game (Envelope doc), `body` now holds the story only; add on lines live in `addons` and the hashtag line in `hashtags`, joined only when the Buffer caption is built, so nothing posted changes. Caption fixes go to the JSON first, then the Buffer post. Every existing record was split once (the extras were always at the end); launch week records that never carried a hashtag line in `body` got the standard "#OnThisDay #WW2".
* 24 Oct 2026: The cards run moved to Friday and now builds from the Wednesday research run's slate. Picking the events, the series mix, the never repeat rule, the photo hunt, the `videoPhotos` handoff, the theme tagging, and the dispatch numbers moved to the new Research doc; numbers are locked on Wednesday and never renumbered here. Every caption is written only from the dispatch's `facts` block. Research marks somber dispatches; the growth rules skip them.
* 25 Oct 2026: The Flash card added: full art from prepared, approved art in `flash/`, rendered by `drawFlash` in the renderer, with the normal caption rules; first one is Pearl Harbor, 7 Dec 2026.
