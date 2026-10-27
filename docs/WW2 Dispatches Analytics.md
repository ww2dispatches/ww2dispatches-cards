# WW2 Dispatches: Analytics

The rules for the **Tuesday analytics review**: how posts are measured, scored, and turned into lessons for the Wednesday research run, the Thursday video run, and the Friday cards run. The Tuesday run follows this doc. Shared setup (Buffer, GitHub, Schedule Board tasks, push reminders, record keeping) is in the Project Brief. The files and the snapshot format are in `analytics/README.md` in the cards repo.

## The goal
Learn what works, a little more each week, without adding to Brian's time. Each Tuesday night the review measures every post, scores it fairly, updates the playbook the next three runs read, and sends Brian a short summary. Brian's part is about five minutes reading it, plus any decision it files for him.

## What gets measured
Buffer is the source: it reads each platform's numbers about once a day, so its figures trail the apps by up to a day. That is fine, because every post is compared with other posts that have the same lag. Exact counts will always trail what the apps show.

In order of importance:
1. **Followers gained** per platform (the real goal). Buffer reports follows per post on Instagram; the rest come from a monthly check (see "Gaps").
2. **Reach:** views or impressions.
3. **Video hold:** average seconds watched as a share of the video's length. It shows whether the hook and first frame work.
4. **Response:** reactions, comments, shares, reposts, and saves.

Engagement rate as Buffer reports it is not used; on small numbers it misleads (one like on 7 views reads as 14%).

## How posts are scored
* **Each post is matched to its record** in `dispatches/` or `namethis/` by its Buffer id. X Name This posts, sent by Typefully, match by their X link or post date. Anything else is listed as unmatched on the Scoreboard and never guessed (replaced posts and Facebook's duplicate copies are expected there).
* **Age rules.** Under 48 hours old a post is "too early" and not scored. From 48 hours it gets a provisional score; from 7 days its score is final. Every post is pulled again each week for 14 days, so it reaches its final score.
* **Same kind, same platform.** Cards, Name This, and videos are each judged only against their own kind on the same platform, over the last 28 days. A quiz asks for comments outright, so Name This is never compared with cards on Response; across kinds, only Reach and followers are compared.
* **Reach** = (views + 10) / (typical views + 10), where typical is the median. 1.0 is typical, 2.0 is twice the views. The 10 keeps tiny numbers from swinging wildly.
* **Response** = weighted actions per 100 views, divided by the typical figure. Weights: like 1, comment 3, repost, quote, share, or save 2. Only posts with 50 or more views get a Response.
* **The floor.** A platform counts toward a post's score only once its typical post reaches 50 views and at least 5 posts of that kind have been scored there. Below that it is shown but not scored. At launch only Threads counted for cards.
* **A post's score** is the average of its Reach (and Response) over the platforms that count.
* **Groups** (series, format, slot, the theme tags, engagement question or not, and for videos the opening shot and sound) need 5 or more posts, or they show "not enough data".

## Theme tags
Every dispatch and Name This record carries a `themes` block, so the review can tell what a post was about as well as its series: who it centers on, the kind of story, what the photo shows, theater, branch, and nations, plus the opening shot, kind, and sound for videos. The fixed list of values is `analytics/themes.md`; only the Tuesday review adds new ones. The Wednesday research run tags each dispatch (who, story, photo, theater, branch, nations), the Saturday Name This run tags each Name This card, and the Thursday video run tags each video from its actual first frame. The era (road to war, the war, the aftermath) comes from the event date.

The tags exist to separate causes that travel together. Example: the WAVES dispatch drew the best response of launch week; the tags let later weeks show whether that came from the subject (a barrier broken by Black women) or the hook.

## From numbers to decisions
Every finding sits on one rung:
1. **Hunch:** seen in one review, or fewer than 5 posts. The runs may lean toward it; it never changes anything on its own.
2. **Pattern:** holds across 3 weekly reviews with 5 or more posts on each side. The runs follow it.
3. **Rule change:** a pattern that would change a Project doc (posting times, a format, a platform). Filed for Brian as a Schedule Board task; nothing reaches the docs without his OK.

**Tests** change one thing at a time so the result can be read clearly, each with a review date. New tests start only with Brian's OK; the review proposes them in its summary.

## Where it lives
* **The playbook** (`analytics/playbook.md`): the current patterns, hunches, active tests, things to watch, and anything for Brian to decide. The Wednesday research run reads it before picking events, the Thursday video run before building videos, and the Friday cards run before writing hooks and captions.
* **The Scoreboard** (pinned, https://claude.ai/artifact/H3ry2Cg3jM8mkxsTYrV7hP): This week (the summary, best and weakest posts, decisions needed), Posts (every post with Reach, Response, and each platform), Trends (views per week, typical posts, groups), and Playbook. Rebuilt every Tuesday.
* **The log** (`log/performance-log.csv`): one row per post per platform with every number, score, and tag. Opens in Excel. Never edited by hand.
* **The record:** `analytics/snapshots/` (each week's raw pull, never edited) and `analytics/reviews/` (each week's written review).

## The Tuesday run
"WW2 Dispatches weekly analytics review", Tuesday 7:47 p.m. Mountain, on Opus 5.5, a Claude Code scheduled task with both repos attached, Buffer connected, push and email when done. Posts from Sunday and Monday are still "too early" on Tuesday and get their score the following week.
1. Attach and clone the cards repo (Brief, "GitHub repos and hosting").
2. Pull every post sent in the last 14 days from Buffer with the query in `analytics/README.md`, and save it as `analytics/snapshots/YYYY-MM-DD.json` in the format given there.
3. Run `python3 renderer/analytics.py`. Fix any tag problems it lists using `analytics/themes.md` (the opening shot tag needs the video's real first frame), and look over any unmatched posts.
4. Read the scores against the playbook. Move findings up or down the ladder, close any test past its review date with its result, and write the week's review to `analytics/reviews/YYYY-MM-DD.md`: the summary, best and weakest posts and why, what changed, test results, and anything for Brian. Rewrite `analytics/playbook.md` to match. Plain words, no dashes.
5. Run `python3 renderer/analytics.py` again so the Scoreboard picks up the new review and playbook, commit and push, then publish `analytics/scoreboard-page.html` to the Scoreboard artifact (read it first).
6. File a Schedule Board task for each decision Brian needs to make, with a push reminder if it has a due time (Brief, "Shared run procedures").
7. **Intercept master list** (next section): add the week's posted cards to the groups they fit, add 5 to 10 hard groups, run the check, commit and push.
8. Send Brian the summary with SendUserMessage: three things that worked, two that didn't, the tests running, whether anything needs him, and the week's new Intercept hard groups (link lines only) with the check's readiness line and "Veto any Intercept group by telling me here". About six lines.

## Intercept master list
**Intercept** is the daily puzzle inside Declass (Intercept doc): twelve cards in four hidden groups of three. Each player's grid is dealt from the master list, `functions/_data/intercept.json` in the cards repo, which this run grows every week. It lives here, not in research, because this run works on the week that has closed: every card it sees has posted, so a day dropped or swapped at the Saturday review can never reach the list, and anything added by hand (a Flash day's extra posts, a deep dive session) is caught too. Cards reach the list about a week after they post, which is fine.

**The posted only rule (decided 27 Oct 2026):** the list names only cards that have already posted (a Name This card once its answer is public). Never a planned or scheduled card, never anything from a slate. The check tool (step 3) refuses any other id.

Each group has: `id` (short, never reused: `e-`, `m-`, or `h-` plus a name), `link` (the typed line shown when it locks, a full sentence such as "All three involve the USS Hornet."), `difficulty`, `cards` (every posted card the group can be dealt from), `alsoFits` (posted cards that also fit the link but shouldn't be dealt in it; the server keeps them off any board holding this group), `source` (one or two lines backing the link), and `added`.

Every week, after the review is written:
1. **Add the week's posted cards to every existing group they fit**: every dispatch and Name This card in the catalog that posted since the last run (the catalog, `functions/_data/catalog.json`, is rebuilt by the log rebuild and holds only cards with a rendered image and their post times). Ask of every group, not just the obvious ones. A card that clearly fits goes in `cards`; one that fits only on a generous reading goes in `alsoFits`. Getting this complete is what keeps grids fair: a card left out of a group it fits can sit on a board where a player files it with that group and is wrongly rejected. Work from the records in `dispatches/` and `namethis/` (facts, place, photo credit, themes).
2. **Add 5 to 10 new hard groups** from posted cards: shared operations, campaigns, ships, commanders, units, and clever links ("Each ship was named for a man of the U.S. Navy"). A group needs 3 posted cards before the server can deal it, ideally 5 or more; with fewer it sits dormant and grows.
3. **Run the check** and fix anything it flags: `node --import ./tests/declass/json-loader.mjs tests/declass/intercept-check.mjs`. It refuses a broken list or any card that hasn't posted (`--prune` removes those and rewrites the file), and reports live and dormant groups, how often a fair grid deals, how many different grids exist, hard groups that never deal, and launch readiness. Commit and push the list with the week's other files.

The rules for links:
* **Historically airtight.** History buffs will publicly challenge anything debatable. Verify every link against the dispatch records and a solid source, and when in doubt leave it out.
* **Easy** is visible in the photo (aircraft, warships, a national leader). **Medium** is knowable from the place or subject (a theater, a battle named on every card, a nation, a branch, a person). **Hard** takes real knowledge: shared operations, ships, commanders, and clever links. A link the cards print outright (the place line, a kicker naming it) is medium at most.
* **Printed details are never links:** the date and the series stamp are just reading. No group may be "all from 1942" or "all Battle Lines".
* **Tone:** a link must never treat tragedy as a gimmick. Sensitive cards (Loss and tragedy) can be in groups, but never grouped by the loss itself ("ships that sank", "men who died").
* **Card faces only:** players see only the card face during play, never the story. A link must be reachable from what the face shows plus real knowledge.
* Never use the word Connections anywhere in the list.

**Brian's part is optional:** the summary lists the week's new hard groups with their link lines. He can veto any by saying so in the Project; Claude then sets `"vetoed": true` on it (never deletes it, so it isn't added again) and pushes. Nothing waits on him.

## Gaps
* **Followers:** Buffer gives no follower totals. Once a month, around the first Tuesday, the review asks Brian for a screenshot of each app's follower count (or reads public counts where it can), and records them in the review. Instagram's per post follows are summed every week.
* **YouTube retention curves and Threads viewers** aren't in Buffer. Views and average watch time are enough to compare posts.
* **Spot check:** once a month Brian can send one or two app screenshots so the review can confirm Buffer is tracking in the right direction.
* **Substack:** open rates and signups come from Substack itself; the review notes them when Brian shares them.

## Changelog
* 21 Oct 2026: Analytics started. Method settled step by step with Brian on launch week data (a test run, then erased): the 48 hour and 7 day age rules, the 50 view floor, scoring each kind only against itself, Reach and weighted Response, the 5 post group minimum, and the hunch, pattern, rule change ladder. Theme tags added to every dispatch, Name This card, and video. Tests A (human first Spec Sheet hooks) and B (action first Living Card openings) approved, reviewed 4 Nov. Scoreboard built and pinned; first real review Wed 28 Oct 2026.
* 24 Oct 2026: The review moved to Tuesday night so its playbook is fresh for the new Wednesday research run, the Thursday video run, and the Friday cards run (Project Brief, "Weekly workflow"). First real review Tue 27 Oct 2026; Tests A and B are reviewed 3 Nov. Research now tags each dispatch's themes; the video run still tags each video.
* 27 Oct 2026: The Intercept master list upkeep added as step 7, moved here from the Wednesday research run the same day, so it only ever works from posted cards (the posted only rule) and catches posts added by hand. The summary gains the week's new hard groups for Brian's optional veto.
