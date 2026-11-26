# WW2 Dispatches: Lunch Drop

Brian's daily hand post into an X Community at lunch, around 1 p.m. Mountain, plus the page that makes it a two minute job. Added 30 Oct 2026 to help X grow: Communities put the day's story in front of history people who don't follow the account yet, the same way the History Threads community does on Threads. The Sunday Lunch Drop run follows this doc. Shared setup (writing rules, GitHub, Schedule Board tasks, push reminders) is in the Project Brief.

## What Brian does (about 2 minutes, then replies)
Open the pinned **Lunch Drop** page (Brian uses his laptop or desktop). It opens on today. Click the community button (it opens X), copy the photo and the post text into a new Community post (on a Tuesday with a 1 p.m. video, download the video from the page and attach it instead of the photo), leave "also post to followers" off, post, then reply to it with Reply 1 and the day's card, and reply to Reply 1 with Reply 2. He spends the rest of lunch answering comments on that post and the morning posts, using the quick facts on the page. **Mark posted** turns the day's tab green on that device.

## The Lunch Drop page
* Pinned artifact **Lunch Drop**: https://claude.ai/artifact/VvRUuFWpKjJaqbWefzhqdg (slug ea3563a7-5bda-400f-bdbb-6f737401195f). Rebuilt every Sunday, one tab per day, opening on today in Denver time.
* Built by `python3 renderer/lunch.py` from `lunch/YYYY-MM-DD.json` (named for the week's Sunday) into `lunch/lunch-page.html`, one self contained file with the photo previews embedded. Publish it to the same artifact with the Artifact tool's publish from files (`index.html` from that file), passing the slug and the live version (read it first with get_artifact). Never create a second Lunch Drop artifact.
* Each day shows: the series stamp, number, and title; a button that opens the day's X Community; the photo with its credit, Copy photo, and Open full photo (the raw GitHub link, for press and hold to save); Copy alt text; on a video day, the video with Download video and Open video above the photo, which becomes the backup; the post text; each reply, with the day's card, Copy card, and Open full card under Reply 1; the quick facts; the sources; Mark posted.
* The script prints PROBLEM lines (missing fields, a missing image, a posted card used as the main image, a missing reply card, a dash, a link in the post). Fix every one before publishing.

## What goes up each day
* **A plain archival photo of the same event, never a card.** The 8 a.m. card and the noon video already sit on the X profile, and a Community post shows there too, so reposting either one shows twice (decided 30 Oct 2026). No card frame, no number, nothing designed: just the photo. Pick, in order: (1) one of the dispatch's `videoPhotos` files that is not the card's lead photo; (2) on a Living Card day, a clean still frame grabbed with ffmpeg from the dispatch's source film in `footage/` on R2 (`python3 renderer/media.py get footage/<file>` fetches it) (a moment with people or the machine clearly in view, never a frame from the finished video with its card bands); (3) another public domain photo of the event or its subject, fetched per the Brief's photo rules (the English Wikipedia API and upload.wikimedia.org work best); (4) only if nothing else exists, the card's lead photo from `photos/`, unframed. Never a photo with a copyright stamp or a commercial photographer's mark. Save it as `lunch/img/YYYY-MM-DD.jpg` (about 1280 to 1600 px wide) and record its credit line in `imageCredit`.
* **The card rides on Reply 1** (decided 30 Oct 2026): the day's 8 a.m. card, the X version (`cards/dispatch-NNN-x.jpg`; the Flash card on a Flash day), attached to Reply 1. Replies sit on the profile's Replies tab, not its Posts tab, so the card never shows twice there, and everyone who opens the thread still sees the brand and the dispatch number. Record it in `replyCard`.
* **The community:** one per day, rotating History Hub, Modern History, History, continuing from the last day in the newest `lunch/` file. On Wednesday and Saturday, skip the community that day's Name This uses (the `community` in that date's `namethis/` file) and take the next one. Never the same community twice in a row when it can be helped. IDs are in `renderer/lunch.py` and the Name This doc.

## The Substack tab (added 26 Nov 2026, Brian)
A two week test of **Substack Notes**, the short feed that shows the publication to readers outside the email list (Newsletter doc, "Growing the list"). Brian posts it by hand in the same lunch session; Buffer's Substack channel would cost an extra paid channel, so it waits until the test proves itself.
* **What goes up:** the day's **8 a.m. card and its caption, exactly as posted** (the dispatch's `body`), as one note. No new writing, no hashtags. During a Campaign Series it is still the 8 a.m. card, not the series post.
* **The page:** a switch at the top, **X Community** or **Substack**, remembered per browser (address `#sub` opens the Substack side). The Substack side shows, for the picked day: an Open Substack Notes button (https://substack.com/notes), the caption with Copy caption, the card (the Instagram 4:5 version, `cards/dispatch-NNN-instagram.jpg`, falling back to the X card) with Copy card, Open full card, and Copy alt text, and its own Mark posted, kept apart from the X Community mark.
* **Filled automatically:** `renderer/lunch.py` finds each date's 8 a.m. dispatch itself (historical month and day equal to the posting date, `time` "08:00"), so the Sunday run writes nothing extra. Optional per day override in the record: `substack` {`dispatch` (file id), `card`, `caption`, or `skip`: true}. On a Flash day (7 Dec 2026) set `substack.dispatch` to the Flash dispatch if it is not the 08:00 record. A missing card or a dash prints a PROBLEM line.
* **Judging it:** after two weeks of notes (about 10 Dec 2026), Brian compares new Substack subscribers. Keep, move to Buffer, or stop.

## During a Campaign Series (added 16 Nov 2026, Brian)
While a Campaign Series runs (Campaign Series doc; Pearl Harbor 26 Nov to 6 Dec 2026), the Lunch Drop carries **that day's Campaign Series story** instead of the 8 a.m. dispatch, so the countdown reaches the History Communities every day (except on a Tuesday with a 1 p.m. video; see "Tuesday: the 1 p.m. video"). Nothing else changes: the 8 a.m. card still posts on all four platforms as usual, and the Lunch Drop stays an extra hand post into one X Community.
* **Source:** the day's `campaign-series/<series>/day-NN.json` (its `body` and `sources` stand in for the `facts` block). Never add a fact the record and its sources don't hold.
* **New angle, new words:** the 6:30 series post is already on the X profile that morning, so the Lunch Drop post shares no sentence or hook with it. Lead with a different detail from the record, the irony, or what the people that day could not know yet.
* **Photo:** a different public domain photo of the same moment or subject, never the series image and never its photo. Pick per "What goes up each day" (an extra photo already in `photos/campaign/`, then a fetched one). If none exists, use that day's 8 a.m. dispatch as normal and say so in the summary.
* **Reply 1** carries the day's series image (`campaign-series/<series>/images/day-NN-x.jpg`) in place of the 8 a.m. card, so readers see the series look, and ends with the series footer line ("Campaign Series: Pearl Harbor · Day by Day · Day 3 of 12"). Record it in `replyCard`.
* **Flash days stay on the day's event:** on 7 Dec 2026 the Lunch Drop covers the attack itself from the Flash dispatch (the Flash card on Reply 1), as the Flash day plan sets out (Roadmap), not the series' Day 12.
* Somber series days follow the usual somber rule (no question).

## Tuesday: the 1 p.m. video (added 25 Nov 2026, Brian)
On Tuesdays the Lunch Drop is a brand new Living Card instead of a photo: the Tuesday 1 p.m. video (Videos doc, "Tuesday 1 p.m. video"). Buffer posts it on the other five channels at 1 p.m. and never on X, so Brian's Community post is its only X post and it shows on the profile once.
* **Source:** the Tuesday dispatch marked `"videoTime": "13:00"` whose video is built (it has a `video` block, and `python3 renderer/media.py url videos/dispatch-NNN-x.mp4` returns the X cut on R2). The day's record takes that card's `dispatch`, `num`, `series`, and `title`, and adds `dropVideo`, the X cut's path (`videos/dispatch-NNN-x.mp4`).
* **No video that Tuesday** (no card marked 13:00, the slot still open for Brian, or a Flash day): build the day the usual way and say so in the summary.
* **Post text:** from that card's `facts`, by "Writing the post". It shares no sentence or hook with the video's caption in the kit, that card's own caption, or the day's other posts.
* **Backup photo:** still save `image` and `imageCredit` as usual (a clean still from the source film, or another photo of the event), so the page has a preview and Brian has a photo to post if the video won't upload.
* **Reply 1** carries that card's X still (`cards/dispatch-NNN-x.jpg`) in `replyCard`. **Reply 2** credits the film (the dispatch's `film.record`) and the card's photo.
* **alt** describes what the video shows in one or two plain sentences.
* **During a Campaign Series** the video still takes Tuesday. The series' 6:30 post is untouched, and the Lunch Drop goes back to the series story on Wednesday.

## Writing the post
Written for history people in a Community, not the general feed, so it is different from the 8 a.m. caption. Draw only from the dispatch's `facts` block (the `body` on older dispatches that have no `facts`). Never add a fact, and never use the `declassified` block, which belongs to the Declass game.
* **Hook first, a new angle.** Not the 8 a.m. hook. Lead with the lesser known detail, the irony, or the decision at the heart of it.
* **Two short paragraphs of story,** plain words, with the date in them.
* **End with a real question history people would argue about** (a judgment, a what if, a "was this the moment"), never a quiz or "thoughts?". On a dispatch marked `somber`, no question: end on a plain closing line instead, and set `somber` so the page shows the warning.
* About 400 to 800 characters. No hashtags, no links, no @ mentions, no dashes of any kind (proper names like B-17 are fine), no Ko-fi, newsletter, or Declass lines.

## The replies
* **Reply 1:** one more strong detail or what happened next, from the facts, posted with the card attached.
* **Reply 2:** the credits for both pictures in the thread (the day's photo from `imageCredit`, then the card's photo from the dispatch's `photoCredit`) and the sources by name, no links.
* A third reply only when the facts hold a second strong detail worth it. Never more than three.
* **Quick facts:** five to eight short lines from the facts block that Brian can paste when he answers comments.
* **alt:** plain alt text describing the day's photo.

## The record (`lunch/YYYY-MM-DD.json`)
`week` (the Sunday) and `days`, one per day Sunday to Saturday, each with: date, dispatch (the file id), num, series, title, community, image (`lunch/img/YYYY-MM-DD.jpg`), imageCredit, replyCard (`cards/dispatch-NNN-x.jpg`), dropVideo (only on a Tuesday with a 1 p.m. video), somber, post, replies, alt (written for this photo), facts, sources ({title, url}, including the photo's page). Brian's posts are by hand, so Buffer never sees them; the record is what the Tuesday review can compare against when Brian shares results.

## The Sunday Lunch Drop run
"WW2 Dispatches Lunch Drop prep", Sunday 5:43 a.m. Mountain, on Opus 5.5, a Claude Code scheduled task with both repos attached, push and email when done. It runs after Saturday's review, so every card and caption is final.
1. Pull the cards repo. Read this doc, the Brief's writing rules, `analytics/playbook.md` (anything about X, hooks, or questions), and the newest `lunch/` file for the rotation.
2. For today (Sunday) through Saturday: on Tuesday, check first for the 1 p.m. video (see "Tuesday: the 1 p.m. video"); on days a Campaign Series runs use its day record instead (see "During a Campaign Series"); otherwise find each day's 8 a.m. dispatch in `dispatches/` (the 8 a.m. record whose `links.posted` or Buffer schedule falls on that date; check Buffer if unsure, and the Flash card on a Flash day). Choose and save each day's photo per "What goes up each day", and LOOK at every one before using it.
3. Pick each day's community, then write the post, replies, alt, and quick facts per this doc. Write `lunch/<Sunday>.json`.
4. Run `python3 renderer/lunch.py`, fix every PROBLEM (including the Substack tab's, which needs each day's 8 a.m. card rendered), and look at the page in a 390 px wide browser window (screenshot it, both the X Community and Substack sides) to check that each day reads cleanly.
5. Publish `lunch/lunch-page.html` to the Lunch Drop artifact (above). Commit and push `lunch/` (the JSON, `lunch/img/`, and the page).
6. If a day's dispatch is missing (a swap still open, a failed run), leave that day out, say so, and never invent one.
7. Send Brian a short summary: each day's subject, community, and opening line, any day left out, and the page link. Dash free.

## Changelog
* 30 Oct 2026: Lunch Drop started. Brian posts the day's 8 a.m. card into one X Community at lunch with a new hook and a debate question, plus two replies, from a pinned page built by a new Sunday morning run. First page built by hand for Fri 30 and Sat 31 Oct; the first Sunday run is 1 Nov.
* 30 Oct 2026 (afternoon): The Lunch Drop now posts a plain archival photo of the event instead of the 8 a.m. card, because a Community post also shows on the X profile and the card appeared twice there. No new cards: just the photo, chosen from the dispatch's extra photos, a still from its film, or a fetched public domain photo.
* 30 Oct 2026 (later): The day's card goes on Reply 1, so the brand and dispatch number still reach Community readers without the card showing twice on the profile's Posts tab. Reply 2 credits both pictures.
* 16 Nov 2026: **During a Campaign Series the Lunch Drop carries that day's series story** (Brian), first for Pearl Harbor (26 Nov to 6 Dec 2026), so the countdown reaches the Communities daily: new angle and photo, the series image on Reply 1; Flash days stay on the day's event. The 8 a.m. card is unchanged.
* 25 Nov 2026: **Tuesday is a video** (Brian): on Tuesdays the Lunch Drop is the new Tuesday 1 p.m. video, a Living Card made for it, which Buffer posts on the other five channels and never on X. The page shows the video with a download button, the photo stays as a backup, and Reply 1 carries the video's card. During a Campaign Series the video still takes Tuesday. First one Tue 1 Dec 2026.
* 26 Nov 2026: **Substack tab added** (Brian): a switch on the page between X Community and Substack. The Substack side carries each day's 8 a.m. card and caption, as posted, for a hand posted Substack note at lunch, a two week test judged by new subscribers. The builder fills it from `dispatches/` with no extra work for the Sunday run. First notes Thu 26 Nov.
