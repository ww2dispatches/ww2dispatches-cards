# WW2 Dispatches: Lunch Drop

Brian's daily hand post into an X Community at lunch, around 1 p.m. Mountain, plus the page that makes it a two minute job. Added 30 Oct 2026 to help X grow: Communities put a card in front of history people who don't follow the account yet, the same way the History Threads community does on Threads. The Sunday Lunch Drop run follows this doc. Shared setup (writing rules, GitHub, Schedule Board tasks, push reminders) is in the Project Brief.

## What Brian does (about 2 minutes, then replies)
Open the pinned **Lunch Drop** page on his phone. It opens on today. Tap the community button (it opens X), copy the card and the post text into a new Community post, leave "also post to followers" off, post, then add Reply 1 and Reply 2 under it. He spends the rest of lunch answering comments on that post and the morning posts, using the quick facts on the page. **Mark posted** turns the day's tab green on that device.

## The Lunch Drop page
* Pinned artifact **Lunch Drop**: https://claude.ai/artifact/VvRUuFWpKjJaqbWefzhqdg (slug ea3563a7-5bda-400f-bdbb-6f737401195f). Rebuilt every Sunday, one tab per day, opening on today in Denver time.
* Built by `python3 renderer/lunch.py` from `lunch/YYYY-MM-DD.json` (named for the week's Sunday) into `lunch/lunch-page.html`, one self contained file with the card previews embedded. Publish it to the same artifact with the Artifact tool's publish from files (`index.html` from that file), passing the slug and the live version (read it first with get_artifact). Never create a second Lunch Drop artifact.
* Each day shows: the series stamp, number, and title; a button that opens the day's X Community; the card with Copy card, Open full card (the raw GitHub link, for press and hold to save), and on video days Open the video; Copy alt text; the post text; each reply; the quick facts; the sources; Mark posted.
* The script prints PROBLEM lines (missing fields, a missing card file, a dash, a link in the post). Fix every one before publishing.

## What goes up each day
* **The card:** that day's 8 a.m. card, the X version (`cards/dispatch-NNN-x.jpg`), already posted that morning. Never a new card, never a number of its own, never the 5 p.m. card. On a Flash day, the Flash card.
* **The video option:** on a day whose noon video exists, record its X file (`videos/dispatch-NNN-x.mp4` for a Living Card, the Story Card file named in its `story` block) so Brian can post the film instead. Living Cards are the better pick when the film is strong.
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
`week` (the Sunday) and `days`, one per day Sunday to Saturday, each with: date, dispatch (the file id), num, series, title, community, card, video (or null), videoKind ("Living Card", "Story Card", or null), somber, post, replies, alt, facts, sources ({title, url}). Brian's posts are by hand, so Buffer never sees them; the record is what the Tuesday review can compare against when Brian shares results.

## The Sunday Lunch Drop run
"WW2 Dispatches Lunch Drop prep", Sunday 5:43 a.m. Mountain, on Opus 5.5, a Claude Code scheduled task with both repos attached, push and email when done. It runs after Saturday's review, so every card and caption is final.
1. Pull the cards repo. Read this doc, the Brief's writing rules, `analytics/playbook.md` (anything about X, hooks, or questions), and the newest `lunch/` file for the rotation.
2. For today (Sunday) through Saturday, find each day's 8 a.m. dispatch in `dispatches/` (the 8 a.m. record whose `links.posted` or Buffer schedule falls on that date; check Buffer if unsure, and the Flash card on a Flash day). Confirm its card file is in `cards/` and its raw link returns it. Note any noon video for that date.
3. Pick each day's community, then write the post, replies, alt, and quick facts per this doc. Write `lunch/<Sunday>.json`.
4. Run `python3 renderer/lunch.py`, fix every PROBLEM, and look at the page in a 390 px wide browser window (screenshot it) to check that each day reads cleanly.
5. Publish `lunch/lunch-page.html` to the Lunch Drop artifact (above). Commit and push `lunch/`.
6. If a day's card is missing (a swap still open, a failed run), leave that day out, say so, and never invent a card.
7. Send Brian a short summary: each day's subject, community, and opening line, any day left out, and the page link. Dash free.

## Changelog
* 30 Oct 2026: Lunch Drop started. Brian posts the day's 8 a.m. card into one X Community at lunch with a new hook and a debate question, plus two replies, from a pinned page built by a new Sunday morning run. First page built by hand for Fri 30 and Sat 31 Oct; the first Sunday run is 1 Nov.
