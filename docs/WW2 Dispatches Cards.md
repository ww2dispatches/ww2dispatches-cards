# WW2 Dispatches: Cards

The rules for the two daily cards: the **8 a.m. story dispatch** and the **5 p.m. evening card**. The Thursday cards run follows this doc. Shared setup (series, brand, writing rules, photo rules and workarounds, Buffer channel IDs, Schedule Board tasks, record keeping) is in the Project Brief. The slot layout is in the Roadmap's "Posting schedule at a glance". The noon video is in the Videos doc. What the analytics have taught so far is in `analytics/playbook.md` (Analytics doc).

## The batch
Two cards a day, every day, on X, Instagram, Threads, and Facebook through Buffer:
* **8:00 a.m. Mountain: the story dispatch**, with the long story caption.
* **5:00 p.m. Mountain: the evening card**, in one of three formats (Photo of the Day, Quote of the Day, Spec Sheet) with a shorter caption.

The Thursday run does 14 cards for the coming Sunday through Saturday. It never schedules a card at noon (the daily video) or at 10 a.m. on Wednesday or Saturday (Name This). It checks Buffer first so a slot that is already scheduled is never duplicated.

## Picking the events
* **Read `analytics/playbook.md` first.** Follow its patterns and any active test that touches cards; lean toward its hunches when choosing between equally good events. These rules still come first.
* Pick the most interesting event of the era (1930s lead up through the late 1940s) that happened on that calendar date, any year. Favor a real story: a twist, a vivid human detail, high stakes, or clever engineering.
* The two cards on a day may cover different events or the same event from another angle (the 17 Oct 2026 pair: Kearny's torpedoing at 8 a.m., then the Spec Sheet on why her design kept her afloat at 5 p.m.).
* **Mix the four series** across the week, with at least one Home Front. Glance at `log/series-counts.csv`; if one series is falling behind, lean toward it.
* **Never repeat** an event already covered: check `log/series-log.csv` and `dispatches/`.
* Because a noon video follows each day, **favor events that have real film or can be told with four to six real archival photos**.
* Check the Roadmap's "Upcoming big dates" for anniversaries in the batch week; those get the strongest treatment.
* Verify every fact per the Brief's writing rules. Never guess.

## Photos for cards
* Follow the Brief's photo rules and fetching workarounds. Start the photo search early.
* **If a good photo cannot be fetched**, pick a different event that has one rather than leave a slot empty, and file a Schedule Board task naming the photo wanted and its exact page so Brian can supply it.
* **Handoff to the video run:** for each day, also line up three to five extra real public domain photos of that day's event and record them in the dispatch JSON as `videoPhotos` (page links and credits), plus any NARA film record noticed for a possible Living Card, as long as it doesn't slow the cards.

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

## Dispatch numbers (one serial)
* The dispatch number counts up by one with every card, 8 a.m. and 5 p.m. alike, in the order they post (date, then time). It counts cards, not events. Continue from the highest `num` already used in `dispatches/`.
* A noon video shares the number of the dispatch it covers. Name This and the welcome post never take a number.
* When a card is slotted between numbered ones, renumber in date and time order before any of them post. **Once a card has posted, its number never changes.**
* At 14 cards a week the serial passes 999 around late 2027; the renderer already handles four digits.

## Evening cards (5 p.m.)
Same card frame, bands, stamp, date, place, and handle as the 8 a.m. card; only the photo window and the format label change, so every post reads as the same brand. Each still ties to that calendar date and carries one of the four series stamps.
* **Photo of the Day** (`"format": "photo"`): a striking archival photo with a short caption. Nearly identical to the morning card; the label next to the number is the difference.
* **Quote of the Day** (`"format": "quote"`): the photo dimmed, the quote set large in Special Elite in cream, a short series color rule, and the speaker and occasion under it in Oswald. Fields: `quote`, `quoteBy`. The quote must be **verified word for word** against a reliable source, spoken or written on that date, and short enough to read at feed size (aim under 30 words).
* **Spec Sheet** (`"format": "spec"`): the photo in the top half of the window, a datasheet panel below with a title (`specTitle`) and up to six rows (`specs`: [[label, value], ...]) in two columns on the X card. Use it **whenever a machine, weapon, ship, aircraft, or system genuinely shaped that day's events**, not only on first flights or launches. Brian wants these often. **Every number must agree across sources; if sources disagree, leave that row out.** Usually Blueprint, but any series fits (a Home Front ration chart, a Battle Lines order of battle).
* **Mix** the three across the week, with **at least two Spec Sheets a week** when the dates allow. No fixed weekday per format.
* A Spec Sheet or Quote can cover a slot where a story photo is missing.

## Caption style
Every card gets a full story caption. **Hook first, always.** The opening line or two must grab a scroller on its own: a surprising fact, a vivid image, a twist, or the stakes. The X feed shows only about the first 280 characters before "Show more", and Instagram shows even less before "more", so the hook has to work alone. **Never open with the bare date.**
* **8 a.m. dispatches:** X, Instagram, and Facebook share the same long caption, **about 750 to 1,200 characters**. Structure: the hook, then a paragraph that starts with the date written out (for example "17 October 1941.") and tells what happened, then two or three short paragraphs with why it mattered, one vivid human or technical detail, and what came next. Then the hashtags.
* **5 p.m. evening cards:** shorter, **about 450 to 750 characters**, same rules (hook first, the dated paragraph, one strong detail). A Spec Sheet caption explains why the machine mattered that day; a Quote caption gives the context and repeats the quote.
* **Threads:** a trimmed version **under 500 characters** (the hook, the date and core story, one strong detail), no hashtag.
* Short paragraphs, plain words, no dashes. Every added detail is verified and the sources are listed in the dispatch JSON.
* Store the long caption (with the Instagram ending) in the JSON `body` field and the Threads version in `threads`.

## Hashtags and the Threads topic
* **Instagram:** ends `#OnThisDay #WW2`.
* **X and Facebook:** the same caption, but end `#OTD #OnThisDay #WW2` (#OTD is the tag historians and archives use most). The JSON `body` keeps the Instagram ending; swap the last line when scheduling X and Facebook.
* **Threads:** no hashtag. Every Threads post is filed in the **History Threads** community through Buffer's topic field (see the Brief's Buffer setup). Older JSON `threads` fields may still end with #OnThisDay; ignore that ending when scheduling.
* **Anniversary days:** Instagram may add one event hashtag after `#OnThisDay #WW2` (for example #PearlHarbor or #VeteransDay). X and Facebook stay at three tags by swapping #OnThisDay for the event tag (for example `#OTD #WW2 #PearlHarbor`).

## Growth rules
These add no time for Brian; the Thursday run applies them.
* **Engagement questions:** close some captions with a short open question, as the last line before the hashtags. Two or three a week, never on back to back days, so it never reads like a formula. Good questions invite family stories, opinions, or a guess ("Did anyone in your family work in a wartime factory?", "Would you have trusted this machine?", "Which do you think mattered more, the code breakers or the convoys?"). One plain line. Never on somber dispatches. Never in the same caption as the Ko-fi soft ask or the newsletter mention. The Threads version carries the same question and must still fit 500 characters; trim the story, not the question. Record `question: true`. Comments get answered under the reply plan.
* **Instagram carousels:** where good extra public domain photos of the same event exist, the Instagram post becomes a carousel. Aim for two to four a week; never pad with weak or unrelated photos. Slide 1 is always the normal card (cards/dispatch-NNN-instagram.jpg). Slides 2 to 4 are extra archival photos of the same event, same licensing rules. Add a `slides` array to the JSON: [{photo: "photos/<id>-2.jpg", caption: "short line, two lines max", credit: "source, record number"}]. Render with `node renderer/slides.js <dispatch-id>`, which writes cards/dispatch-NNN-slide-2.jpg and up (1080 x 1350, cream paper, the whole photo with no crop, caption and credit under it, "Dispatch No. NNN · 2 / 3" at top). Check each slide visually. In Buffer, the Instagram post gets the card first, then the slides in order, each with its own alt text; the card's alt text still starts "WW2 Dispatches card, Dispatch No. NNN, <Series>." X, Threads, and Facebook keep the single card.
* **Ko-fi soft ask:** about once every three weeks, add one soft ask to a single dispatch caption on X, Instagram, Threads, and Facebook, as the last line before the hashtags: "Enjoy these? You can buy us a coffee at the link in our bio." Pick an upbeat or fascinating dispatch (Blueprint and Home Front work well). Never on a somber dispatch. The Threads version must still fit 500 characters with the ask; trim the story, not the ask. No Ko-fi URL in captions. Record `soft_ask: true`; the newest dispatch carrying it shows when the last one ran, so the next lands about three weeks later.
* **Newsletter mention:** about once every two or three weeks, end one dispatch caption on X, Instagram, Threads, and Facebook with "Want the week's dispatches in your inbox? The free weekly roundup is at the link in our bio." as the last line before the hashtags. Same rules as the soft ask: never on a somber dispatch, never in the same caption as the soft ask or an engagement question, and **never in the same batch week as the soft ask**. The Threads version must still fit 500 characters; trim the story, not the line. No Substack URL in captions. Record `newsletter_mention: true`; the newest dispatch carrying it shows when the last one ran.
* **Newsletter launch announcement:** written by the cards run per the Newsletter doc.
* The start dates for each of these are in the Roadmap's First month section.

## Building and scheduling the cards
1. Write the dispatch JSON in `dispatches/` (with `time`, and `format` plus its fields on evening cards; all the fields in the Brief's "Record now, use later"). Put the photo in `photos/`.
2. **Tag its themes:** add the `themes` block (who, story, photo, theater, branch, nations), using only the values in `analytics/themes.md`, spelled exactly. Leave out `video`; the Friday run adds it.
3. Render with `node renderer/render.js <id>`; the `format` field picks the layout. File names: cards/dispatch-NNN-x.jpg (1600 x 1440) and cards/dispatch-NNN-instagram.jpg (1080 x 1350).
4. **Look at every card image**, adjust framing if needed, commit and push, and confirm the raw links return the new images. Apply the `?v=` rule if a file name was reused.
5. Schedule each card in Buffer on X, Instagram, Threads, and Facebook at its time. X gets the X image; Instagram, Threads, and Facebook get the Instagram image. X, Instagram, and Facebook carry the long caption; Threads the short one. **Alt text must begin "WW2 Dispatches card, Dispatch No. NNN, <Series>."** Use each channel's metadata from the Brief.
6. Record the Buffer post ids under `buffer` {x, instagram, threads, facebook}. The analytics match posts by these ids, so if a post is ever deleted and redone, record the new id.
7. **Upload the board pictures:** a review copy of every new X card, Instagram card, and slide goes to the Schedule Board's asset store and its `images` collection (Brief, "Shared run procedures", Board pictures), so Brian sees the cards on the board Friday morning and in the Saturday review. Do the same for any card swapped later.
8. Rebuild the series log (Brief, "Record now, use later").
9. In the summary, say which playbook items and active tests the batch applied.

## Dispatch bank
Keep a few verified, evergreen dispatches (inventions, home front stories), aim for 5 to 7, to drop into any day where the best event lacks a usable public domain photo. List them in `status.md` in the cards repo.

## Changelog
* 15 Oct 2026: Post card locked (photo with Field Telegram band, grain texture, handle in the bottom band, no logo mark). Long story captions replaced the 280 character rule.
* 16 Oct 2026: Two cards a day, the three evening formats, and one serial for every card. Engagement questions, carousels, the anniversary plan, and the soft ask rule added.
* 17 Oct 2026: X captions end #OTD #OnThisDay #WW2; Facebook the same that evening.
* 18 Oct 2026: Threads dropped #OnThisDay for the History Threads topic.
* 19 Oct 2026: Cards moved to their own Thursday run; `videoPhotos` handoff added. Rules moved here from the Project Brief.
* 21 Oct 2026: From Brian's screenshot of the B-17 Name This post, X's ALT badge covered the place line. The X image got extra room at the bottom of the bottom band (bottom only, to keep the photo large). Starts with the Thursday 22 Oct run; cards already scheduled were left as they are.
* 21 Oct 2026 (night): The Thursday run now reads `analytics/playbook.md` before picking events and tags each dispatch's `themes` (Analytics doc). Test A starts with this week's batch: the next two Spec Sheets open their captions with the human stakes, then the machine.
* 23 Oct 2026: Step 7 added: the run uploads review copies of the cards and slides to the Schedule Board, so Brian reviews the pictures there instead of in Buffer.
