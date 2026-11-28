# Bulge Map Room clips: scheduling brief

For a fresh Campaign Series: The Map Room session that has the five R2 values in its environment. Written 27 Nov 2026 by the Map Room chat, which ran the fact check. Read it all before touching Buffer.

**Who posts (Brian, 27 Nov 2026):** this Claude Code session, "Bulge Map Room upload readiness" on claude.ai/code (Default environment, which holds the R2 values), owns every Map Room upload and Buffer post. The Map Room Project chat checks the clips and hands off here; it never schedules. Prep was done 27 Nov: R2 sweep, all six Buffer channels and the Schedule Board all pass. Still needed: the Bulge Clips folder shared with this session through the Claude desktop app.

## Where things stand
* **The fact check is closed. All 30 days pass** (`campaign-series/bulge-1944/verify/FACTCHECK.md`, Closed). Don't redo it, and never change a record's position or line.
* **Clips:** the desktop renders all 30 into OneDrive `D:\OneDrive\Personal\Claude\WW2 Dispatches\The Map Room\Bulge Clips` (HANDOFF request of 27 Nov). Read its Done note in `map-room/HANDOFF.md` first: render time, any failed day, and its look at the key card (Days 1 to 3), the Day 8 drop and the Day 9 reach.
* **The kickoff is already scheduled** for Tue 15 Dec, 6 p.m., on X, Facebook, Instagram and Threads (ids in `campaign-series/bulge-1944/kickoff.json`). Don't schedule it again.
* **Gate 2:** Brian watches Days 1 to 5 by Fri 4 Dec. Schedule nothing until he approves them. If he turns down the look or pace, the fix goes to the desktop through HANDOFF and all 30 render again.

## Order of work
1. Check R2 with `python3 renderer/media.py sweep`; it must report no WARNING. If it does, stop and tell Brian; don't fall back to the videos repo.
2. Stage the clips from OneDrive (the device bridge), and watch Days 1 to 5 yourself before Brian does: a contact strip of frames plus a full play. Check the key card size on a phone sized frame, the tab and strip are clear, the sound is the Ops room bed, and nothing reads TEST.
3. Brian's Gate 2.
4. Upload each approved clip with `python3 renderer/media.py put videos/map-room/bulge-1944/day-NN.mp4` (copy the clip to that repo path first; renders are never committed). Use the link it prints. A re-render gets a new name (`-r2`), never an overwrite.
5. Schedule in batches: Days 1 to 5 after Gate 2, then the rest. Record the six Buffer ids in each day record under `buffer` {x, instagram, threads, facebook, youtube, tiktok}, then commit and push (pull and rebase main first).
6. Put each clip on the Schedule Board (below).
7. Final check (below), then tell Brian in a few lines.

## Buffer, per day (6 posts)
Org 6ad05f69516ac0f2b606b889, America/Denver. `mode: customScheduled`, `schedulingType: automatic`, `dueAt: <date>T06:30:00-07:00` (every date is in standard time). **The post date is the record's `date` moved to 2026 or 2027: Day 1 is Wed 16 Dec 2026, Day 30 is Thu 14 Jan 2027.** Every post carries the same vertical clip. No AI flag anywhere (the table is rendered, not generated).

| Channel | id | Text | Metadata |
|---|---|---|---|
| X | 6ad05fad778b240e2f141d29 | body, blank line, footer, blank line, bookLine, blank line, hashtags_xf | |
| Instagram | 6ad0600c778b240e2f1428f3 | body, footer, bookLineIG, hashtags (blank lines between) | instagram {type: reel, shouldShareToFeed: true} |
| Threads | 6b030a9b8541f09ecb6548b3 (new channel since 22 Nov) | threads, blank line, bookLine. No # at all | threads {type: post, topic: History Threads} |
| Facebook | 6ad2ced7778b240e2f32d873 | as X | facebook {type: reel} |
| YouTube | 6ad2cebb778b240e2f32d7b8 | description: body, footer, bookLine | youtube {title, categoryId "27"} |
| TikTok | 6ad2ce8f778b240e2f32d67c | body, footer, bookLineIG, hashtags | tiktok {title} |

* **Titles (YouTube and TikTok):** `Battle of the Bulge, Day N: <subtitle>`, for example "Battle of the Bulge, Day 3: The 101st races into Bastogne". All are under 100 characters. No dashes.
* **No Campaigns line on Days 17 and 27** (records hold `campaignsLine`; leave it out). A Campaign Series chat reminder on Fri 11 Dec, 5:31 p.m., adds it after the Campaigns go or no go. It will edit these posts, so record the ids carefully.
* **Check every text** for dashes (-, en, em) and Threads for #, and that each Threads text stays under 500 characters with the book line added. X and the rest take the full text, as Pearl Harbor did. **Known:** Day 1's Threads text plus the book line is 520 characters. The Campaign Series chat was asked on 27 Nov to trim Day 1's `threads` by at least 20; if it hasn't, ask before scheduling Day 1.
* **Daily limits:** the 6:30 clip adds one post on every channel on top of the regular day. If Buffer refuses a post over a channel limit, stop and tell Brian with the channel and day.

## Schedule Board (Dispatch Schedule, slug 152aeb53-3e76-45fe-9089-cc765cccefed)
* The 6:30 row finds Campaign Series posts by "Campaign Series" in the alt text and titles them from the footer, so keep the footer exact.
* **Board pictures:** upload the opening still (`campaign-series/bulge-1944/images/day-NN-instagram.jpg`, resized to 1200 px, JPEG 82) and record it in `images` as `bulge-1944-day-NN-instagram` (campaign-series skill, step 7b).
* **Board videos:** the board matches a video to its `videos` document by a dispatch number in the file name, and a Map Room clip has none. Upload one clip, then check on the board whether it plays in its slot. If it doesn't, the 6:30 slot still shows the still and the post text, which is enough for Brian's Saturday review. Ask the Website chat (or whoever owns the board) for a match on `map-room/bulge-1944/day-NN` rather than renaming clips.

## Final check
* 180 posts: 30 days × 6 channels, every one at 6:30 a.m. on the right date.
* Spot check three days' text on every platform against the records; no Campaigns line on 17 and 27; book line present; IG and TikTok say link in bio.
* Every day record has six Buffer ids, committed.
* Mark "Schedule all 30 Bulge clips in Buffer" done on the Planning Board (artifact 4c9ae739-1c5d-4c40-b672-e5d33d618b67, `items/mr-schedule`).
