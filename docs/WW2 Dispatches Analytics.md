# WW2 Dispatches: Analytics

The rules for the **Wednesday analytics review**: how posts are measured, scored, and turned into lessons for the Thursday and Friday builds. The Wednesday run follows this doc. Shared setup (Buffer, GitHub, Schedule Board tasks, push reminders, record keeping) is in the Project Brief. The files and the snapshot format are in `analytics/README.md` in the cards repo.

## The goal
Learn what works, a little more each week, without adding to Brian's time. Each Wednesday night the review measures every post, scores it fairly, updates the playbook the Thursday and Friday runs read, and sends Brian a short summary. Brian's part is about five minutes reading it, plus any decision it files for him.

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
Every dispatch and Name This record carries a `themes` block, so the review can tell what a post was about as well as its series: who it centers on, the kind of story, what the photo shows, theater, branch, and nations, plus the opening shot, kind, and sound for videos. The fixed list of values is `analytics/themes.md`; only the Wednesday review adds new ones. The Thursday cards run tags each dispatch, the Saturday Name This run tags each Name This card, and the Friday video run tags each video from its actual first frame. The era (road to war, the war, the aftermath) comes from the event date.

The tags exist to separate causes that travel together. Example: the WAVES dispatch drew the best response of launch week; the tags let later weeks show whether that came from the subject (a barrier broken by Black women) or the hook.

## From numbers to decisions
Every finding sits on one rung:
1. **Hunch:** seen in one review, or fewer than 5 posts. The runs may lean toward it; it never changes anything on its own.
2. **Pattern:** holds across 3 weekly reviews with 5 or more posts on each side. The runs follow it.
3. **Rule change:** a pattern that would change a Project doc (posting times, a format, a platform). Filed for Brian as a Schedule Board task; nothing reaches the docs without his OK.

**Tests** change one thing at a time so the result can be read clearly, each with a review date. New tests start only with Brian's OK; the review proposes them in its summary.

## Where it lives
* **The playbook** (`analytics/playbook.md`): the current patterns, hunches, active tests, things to watch, and anything for Brian to decide. The Thursday cards run and the Friday video run read it before picking events, writing hooks, and building videos.
* **The Scoreboard** (pinned, https://claude.ai/artifact/H3ry2Cg3jM8mkxsTYrV7hP): This week (the summary, best and weakest posts, decisions needed), Posts (every post with Reach, Response, and each platform), Trends (views per week, typical posts, groups), and Playbook. Rebuilt every Wednesday.
* **The log** (`log/performance-log.csv`): one row per post per platform with every number, score, and tag. Opens in Excel. Never edited by hand.
* **The record:** `analytics/snapshots/` (each week's raw pull, never edited) and `analytics/reviews/` (each week's written review).

## The Wednesday run
"WW2 Dispatches weekly analytics review", Wednesday 7:47 p.m. Mountain, on Opus 5.5, in Claude's cloud with Buffer and GitHub connected, push and email when done.
1. Attach and clone the cards repo (Brief, "GitHub repos and hosting").
2. Pull every post sent in the last 14 days from Buffer with the query in `analytics/README.md`, and save it as `analytics/snapshots/YYYY-MM-DD.json` in the format given there.
3. Run `python3 renderer/analytics.py`. Fix any tag problems it lists using `analytics/themes.md` (the opening shot tag needs the video's real first frame), and look over any unmatched posts.
4. Read the scores against the playbook. Move findings up or down the ladder, close any test past its review date with its result, and write the week's review to `analytics/reviews/YYYY-MM-DD.md`: the summary, best and weakest posts and why, what changed, test results, and anything for Brian. Rewrite `analytics/playbook.md` to match. Plain words, no dashes.
5. Run `python3 renderer/analytics.py` again so the Scoreboard picks up the new review and playbook, commit and push, then publish `analytics/scoreboard-page.html` to the Scoreboard artifact (read it first).
6. File a Schedule Board task for each decision Brian needs to make, with a push reminder if it has a due time (Brief, "Shared run procedures").
7. Send Brian the summary with SendUserMessage: three things that worked, two that didn't, the tests running, and whether anything needs him. About five lines.

## Gaps
* **Followers:** Buffer gives no follower totals. Once a month, around the first Wednesday, the review asks Brian for a screenshot of each app's follower count (or reads public counts where it can), and records them in the review. Instagram's per post follows are summed every week.
* **YouTube retention curves and Threads viewers** aren't in Buffer. Views and average watch time are enough to compare posts.
* **Spot check:** once a month Brian can send one or two app screenshots so the review can confirm Buffer is tracking in the right direction.
* **Substack:** open rates and signups come from Substack itself; the review notes them when Brian shares them.

## Changelog
* 21 Oct 2026: Analytics started. Method settled step by step with Brian on launch week data (a test run, then erased): the 48 hour and 7 day age rules, the 50 view floor, scoring each kind only against itself, Reach and weighted Response, the 5 post group minimum, and the hunch, pattern, rule change ladder. Theme tags added to every dispatch, Name This card, and video. Tests A (human first Spec Sheet hooks) and B (action first Living Card openings) approved, reviewed 4 Nov. Scoreboard built and pinned; first real review Wed 28 Oct 2026.
