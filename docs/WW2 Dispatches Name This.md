# WW2 Dispatches: Name This

A puzzle card, twice a week, built to get people commenting and to reach new audiences through X Communities and the Threads History Threads community. It sits outside the dispatch series: **no dispatch number, ever**, so it never affects the serial and a skipped one leaves no gap. The Saturday Name This run follows this doc. Shared setup (brand, writing rules, photo rules and workarounds, Buffer channel IDs, Schedule Board tasks and push reminders) is in the Project Brief.

## The format
* A real public domain archival photo of something people can identify by sight: a ship, aircraft, tank, weapon, vehicle, place, or now and then a person. Tied to that calendar date like every dispatch, any year of the era (1930s lead up through late 1940s). Never a generated image.
* The subject stands on its own. Never the same event as a dispatch (check `log/series-log.csv` and `dispatches/` for those dates), and never one already used in `namethis/`.
* **No giveaways in the photo:** no visible names, hull numbers, tail codes, captions, or signage that name the answer. Pick another photo or crop it out. Prefer a clear side view. If a photo cannot be fetched, choose a different subject that has one.
* Medium difficulty: an enthusiast should get it, a casual reader should have to think. Vary the subject types against the most recent cards (not two battleships in a row when it can be helped).
* Verify the date and every fact per the Brief's writing rules.
* No answer reveal post is scheduled. The ww2dispatches.com home page shows the newest Name This card and reveals the previous puzzle's answer once the next one posts (Project Brief, "Domain and website"). Brian replies to guesses when he has time.

## The card (renderer: `node renderer/namethis.js <id>`)
* Same Field Telegram frame as the dispatch cards. Top band: wordmark, then "Can you name it?" in Special Elite where the dispatch number would be. A **NAME THIS** stamp and a round **?** seal sit in the top band, never over the photo.
* Color: **Mimeograph Violet #5B4B8A** for the stamp, the ? seal, and the clue (not a series color).
* Bottom band: the date and place as usual, and the clue in the pull line spot, written "Clue: ..." (short enough for two lines, never naming the answer).
* One image only: `cards/namethis-<id>-x.jpg` (1600 x 1440), used on every platform, Instagram included (its 1.11 to 1 shape is inside Instagram's allowed range). Like every X image it has extra room at the bottom of the bottom band so X's ALT badge never covers the place line (Cards doc), so that bottom strip shows on all four platforms.
* Put the photo in `photos/`, render, **look at each card image**, adjust framing if needed, commit and push, and confirm the raw link returns the image. **Always commit both the photo and the card:** the home page shows the card from `cards/`. (The B-17 and Tirpitz cards were never committed, so their JSON carries `cardImage`, the Buffer hosted copy, as a fallback.)
* Record in `namethis/<id>.json`: id, format "namethis", answer, `short` (a one or two word name for the card, such as "Musashi" or "Clark Gable"), date, place, pull (the clue), `body` (the post text exactly as it goes to Buffer and Typefully, without the X hashtags), photo, framing (focusX, focusY, zoom), community (the X Community used), photoUrl, photoNote (the team's working note on what the photo really shows and when, plus license), `photoCredit` (one clean public line: what the photo shows, when, the archive and number, and the license, such as "Tirpitz in Bogen Bay, Norway, 1943 to 1944. NHHC NH 71390, public domain."), sources, `themes` (who, story, photo, theater, branch, nations, using only the values in `analytics/themes.md`; see the Analytics doc), and once scheduled `typefully` (draft id), `buffer` {threads, facebook, instagram}, and `post_date`. Once posted, add `links` {x, threads, facebook, instagram, posted} from Typefully (x_published_url) and Buffer (externalLink). The analytics match the X post by `links.x` or `post_date`, so keep both accurate.
* The renderer can also run inside a browser tab (fonts are bundled in `renderer/fonts/fonts-b64.json`), which is how cards get into Typefully when Claude's workspace can't upload there.

## The post text
Same text on every platform, hook first, no dashes:

> Can you name this ship? (or aircraft, tank, weapon, place, man)
>
> Two or three sentences on what happened that day, with enough detail to help but without naming it.
>
> The clue is on the card. Drop your guess below.

X ends with "#WW2 #OTD #OnThisDay". Threads, Facebook, and Instagram have no hashtags.

**Alt text:** "WW2 Dispatches Name This card. <what the photo shows without naming it>. <date>, <place>. Clue: <clue>." Never "Dispatch No." (the Schedule Board reads that phrase). The analytics also use the opening words to recognize Name This posts on X, so keep them exactly.

## Where and when it posts
Twice a week, **Wednesday and Saturday, all at 10:00 a.m. Mountain**, so it never shares a slot with the noon daily video. List scheduled posts in Buffer and Typefully first so nothing is duplicated.
* **X, through Typefully** (free plan, 10 posts a month; two a week fits). Typefully social set 344895. Posted into an X Community with settings {community_id: <id>, share_with_followers: true}. Rotate in this order, continuing from the community in the most recent `namethis/` file: History Hub (1670486568966946821), Modern History (1810183095208837171), History (1691711931751534664). Draft title "Name This: <answer> (<date>) to <community>". Put the answer and key facts in the draft's notes (scratchpad_text), never in the post. Add alt text on the media.
* **Threads, through Buffer** with the History Threads topic metadata (Brief, Buffer setup). Image: the raw GitHub link to the card.
* **Facebook Page, through Buffer**, type "post". Not in Facebook Groups: the big WWII groups ban quizzes and Page promotion.
* **Instagram, through Buffer**, schedulingType automatic, metadata {instagram: {type: "post", shouldShareToFeed: true}}. Same image, same text, same alt text, no hashtags. A **two week test** (Wed 21 Oct to Sat 31 Oct 2026, four cards); see Later.
* Channel IDs are in the Brief's Buffer setup.
* **How the Schedule Board finds Name This:** the Typefully draft title starting "Name This:" and the Buffer post text starting "Can you name this", so keep both. The Instagram posts use the same opening text, so the board should list them too, but that has not been checked yet.

## Getting the card into Typefully
Typefully needs the image uploaded to its own storage: create_media_upload with alt text, then PUT the card file to the upload URL with `curl -T`. If the upload works, wait for the media to be ready and create the draft with media_ids and publish_at at the post time. Claude's cloud workspace may be blocked from that upload host. If it is:
1. Create the Typefully draft anyway with the text, community, and notes, as a **planned** draft (plan_at the post time) without media, so it never posts without its image.
2. If a browser is available (Claude in Chrome), open the draft at typefully.com, render or fetch the card in the page, and drop it into the composer's file input; then set publish_at to the planned time.
3. If no browser is available, file a Schedule Board task, "Attach the Name This cards in Typefully", due this Saturday 09:00, with each card's raw GitHub link and Typefully private_url and "attach the card, then click schedule", plus a push reminder at that time (Brief, "Shared run procedures"). Brian downloads the card, attaches it in Typefully, and clicks schedule (about a minute each), or asks Claude in chat to do it.

## Weekly routine
"WW2 Dispatches Name This prep" runs every Saturday at 6:13 a.m. Mountain and prepares the two cards for the coming Wednesday and Saturday on X, Threads, Facebook, and Instagram. It reads the Name This notes in `analytics/playbook.md` first, tags each card's `themes`, records the ids and any links in the namethis JSON, rebuilds the logs (`python3 renderer/series_log.py`, which writes `log/namethis-log.csv` and refreshes the home page data), and sends Brian a short summary (each card's day, answer, clue, community, scheduling on all four platforms, and whether the Typefully image attached or needs his minute on Saturday). The Instagram test comparison now comes from the Wednesday analytics review instead.

## Later
* At the 4 Nov analytics review, compare Name This views and replies with regular posts on each platform (on Reach only, since a quiz draws comments by design), and compare the Instagram Name This posts (Wed 21, Sat 24, Wed 28, Sat 31 Oct) with the regular Instagram cards on comments, reach, and follower growth. The reasoning for the test: Instagram has no communities, but puzzle comments are engagement the algorithm rewards, and it costs almost no extra work. The worry is the permanent grid (Name This cards sit outside the series) and a fourth post a day. If Instagram does clearly better than the regular cards, keep it; if it is flat or the grid looks cluttered, drop it. If Name This clearly does better overall, consider a third weekly card (Roadmap, optional extra slots).
* Facebook Groups only later, posted by Brian personally as an unbranded "Did you know?" with the answer included, to fit group rules.

## Changelog
* 18 Oct 2026: Name This started; the live test was Tirpitz (posted 11:54 a.m. on X and 12:30 p.m. on Threads and Facebook, confirmed working on all three, including the Community on Typefully's free plan) (Wednesday and Saturday, X Communities through Typefully, Threads and Facebook through Buffer). Mimeograph Violet chosen. Threads and Facebook moved from noon to 10 a.m. to clear the noon video slot; the Wed 21 and Sat 24 Oct posts were rescheduled. The Schedule Board started reading Typefully.
* 19 Oct 2026: X moved from 9 a.m. to 10 a.m. ("all Name This at 10 a.m. across the board"); the Wed 21 and Sat 24 Oct Typefully drafts were rescheduled. Instagram added as a two week test. Buffer channel IDs now point to the Brief; Typefully upload details moved here from the scheduled task. The Log section was removed: every card's record is its namethis JSON and `log/namethis-log.csv` (the run works out the next community from the newest namethis file).
* 21 Oct 2026: The card got extra room at the bottom of the bottom band, the same as every X image, after X's ALT badge covered the place line on the B-17 card. Starts with the Saturday 24 Oct run; the cards already scheduled stay as they are. Later: Name This added to the ww2dispatches.com home page (a slide on its day, plus a panel with the newest card and the previous answer), so the photo and card must always be committed.
* 21 Oct 2026 (night): Every Name This record gets a `themes` block, and the Saturday run reads the playbook first. Name This is scored only against other Name This cards (Analytics doc). The Instagram test comparison moved to the Wednesday analytics review.
* 24 Oct 2026 (evening): Every Name This record now also keeps `body` (the post text), `short`, and `photoCredit`, per the Brief's "Record now, use later", for the Declass game (Envelope doc). The five existing cards were filled in once from Buffer.
