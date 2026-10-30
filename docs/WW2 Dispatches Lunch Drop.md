# WW2 Dispatches: Lunch Drop

Brian's daily hand post into an X Community at lunch, around 1 p.m. Mountain, plus the page that makes it a two minute job. Added 30 Oct 2026 to help X grow: Communities put a card in front of history people who don't follow the account yet, the same way the History Threads community does on Threads. The Sunday Lunch Drop run follows this doc. Shared setup (writing rules, GitHub, Schedule Board tasks, push reminders) is in the Project Brief.

## What Brian does (about 2 minutes, then replies)
Open the pinned **Lunch Drop** page on his phone. It opens on today. Tap the community button (it opens X), copy the photo and the post text into a new Community post, leave "also post to followers" off, post, then add Reply 1 and Reply 2 under it. He spends the rest of lunch answering comments on that post and the morning posts, using the quick facts on the page. **Mark posted** turns the day's tab green on that device.

## The Lunch Drop page
* Pinned artifact **Lunch Drop**: https://claude.ai/artifact/VvRUuFWpKjJaqbWefzhqdg (slug ea3563a7-5bda-400f-bdbb-6f737401195f). Rebuilt every Sunday, one tab per day, opening on today in Denver time.
* Built by `python3 renderer/lunch.py` from `lunch/YYYY-MM-DD.json` (named for the week's Sunday) into `lunch/lunch-page.html`, one self contained file with the card previews embedded. Publish it to the same artifact with the Artifact tool's publish from files (`index.html` from that file), passing the slug and the live version (read it first with get_artifact). Never create a second Lunch Drop artifact.
* Each day shows: the series stamp, number, and title; a button that opens the day's X Community; the photo with its credit, Copy photo, and Open full photo (the raw GitHub link, for press and hold to save); Copy alt text; the post text; each reply; the quick facts; the sources; Mark posted.
* The script prints PROBLEM lines (missing fields, a missing image, a posted card used as the image, a dash, a link in the post). Fix every one before publishing.

## What goes up each day
* **A plain archival photo of the same event, never a card.** The 8 a.m. card and the noon video already sit on the X profile, and a Community post shows there too, so reposting either one shows twice (decided 30 Oct 2026). No card frame, no number, nothing designed: just the photo. Pick, in order: (1) one of the dispatch's `videoPhotos` files that is not the card's lead photo; (2) on a Living Card day, a clean still frame grabbed with ffmpeg from the dispatch's source film in the videos repo's `footage/` (a moment with people or the machine clearly in view, never a frame from the finished video with its card bands); (3) another public domain photo of the event or its subject, fetched per the Brief's photo rules (the English Wikipedia API and upload.wikimedia.org work best); (4) only if nothing else exists, the card's lead photo from `photos/`, unframed. Never a photo with a copyright stamp or a commercial photographer's mark. Save it as `lunch/img/YYYY-MM-DD.jpg` (about 1280 to 1600 px wide) and record its credit line in `imageCredit`.
* **Credit:** Reply 2 credits this photo, not the card's photo.
* **The community:** one per day, rotating History Hub, Modern History, History, continuing from the last day in the newest `lunch/` file. On Wednesday and Saturday, skip the community that day's Name This uses (the `community` in that date's `namethis/` file) and take the next one. Never the same community twice in a row when it can be helped. IDs are in `renderer/lunch.py` and the Name This doc.

## Writing the post
Written for history people in a Community, not the general feed, so it is different from the 8 a.m. caption. Draw only from the dispatch's `facts` block (the `body` on older dispatches that have no `facts`). Never add a fact, and never use the `declassified` block, which belongs to the Declass game.
* **Hook first, a new angle.** Not the 8 a.m. hook. Lead with the lesser known detail, the irony, or the decision at the heart of it.
* **Two short paragraphs of story,** plain words, with the date in them.
* **End with a real question history people would argue about** (a judgment, a what if, a "was this the moment"), never a quiz or "thoughts?". On a dispatch marked `somber`, no question: end on a plain closing line instead, and set `somber` so the page shows the warning.
* About 400 to 800 characters. No hashtags, no links, no @ mentions, no dashes of any kind (proper names like B-17 are fine), no Ko-fi, newsletter, or Declass lines.

## The replies
* **Reply 1:** one more strong detail or what happened next, from the facts.
* **Reply 2:** the photo credit (the dispatch's `photoCredit`) and the sources by name, no links.
* A third reply only when the facts hold a second strong detail worth it. Never more than three.
* **Quick facts:** five to eight short lines from the facts block that Brian can paste when he answers comments.
* **alt:** the card's alt text from its dispatch JSON.

## The record (`lunch/YYYY-MM-DD.json`)
`week` (the Sunday) and `days`, one per day Sunday to Saturday, each with: date, dispatch (the file id), num, series, title, community, image (`lunch/img/YYYY-MM-DD.jpg`), imageCredit, somber, post, replies, alt (written for this photo), facts, sources ({title, url}, including the photo's page). Brian's posts are by hand, so Buffer never sees them; the record is what the Tuesday review can compare against when Brian shares results.

## The Sunday Lunch Drop run
"WW2 Dispatches Lunch Drop prep", Sunday 5:43 a.m. Mountain, on Opus 5.5, a Claude Code scheduled task with both repos attached, push and email when done. It runs after Saturday's review, so every card and caption is final.
1. Pull the cards repo. Read this doc, the Brief's writing rules, `analytics/playbook.md` (anything about X, hooks, or questions), and the newest `lunch/` file for the rotation.
2. For today (Sunday) through Saturday, find each day's 8 a.m. dispatch in `dispatches/` (the 8 a.m. record whose `links.posted` or Buffer schedule falls on that date; check Buffer if unsure, and the Flash card on a Flash day). Choose and save each day's photo per "What goes up each day", and LOOK at every one before using it.
3. Pick each day's community, then write the post, replies, alt, and quick facts per this doc. Write `lunch/<Sunday>.json`.
4. Run `python3 renderer/lunch.py`, fix every PROBLEM, and look at the page in a 390 px wide browser window (screenshot it) to check that each day reads cleanly.
5. Publish `lunch/lunch-page.html` to the Lunch Drop artifact (above). Commit and push `lunch/` (the JSON, `lunch/img/`, and the page).
6. If a day's dispatch is missing (a swap still open, a failed run), leave that day out, say so, and never invent one.
7. Send Brian a short summary: each day's subject, community, and opening line, any day left out, and the page link. Dash free.

## Changelog
* 30 Oct 2026: Lunch Drop started. Brian posts the day's 8 a.m. card into one X Community at lunch with a new hook and a debate question, plus two replies, from a pinned page built by a new Sunday morning run. First page built by hand for Fri 30 and Sat 31 Oct; the first Sunday run is 1 Nov.
* 30 Oct 2026 (afternoon): The Lunch Drop now posts a plain archival photo of the event instead of the 8 a.m. card, because a Community post also shows on the X profile and the card appeared twice there. No new cards: just the photo, chosen from the dispatch's extra photos, a still from its film, or a fetched public domain photo.
