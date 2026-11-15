# WW2 Dispatches: Campaign Series

A daily social media serial that follows one campaign day by day, told as it happened, the RealTimeWWII way. Each series is researched, written, rendered, and scheduled **in one sitting** with the `campaign-series` skill, in the Campaign Series chat. **No scheduled task** runs it. The weekly runs only read its files so their wording never repeats it (Cards and Videos docs).

## Status
| Series | Dates | Days | State |
|---|---|---|---|
| Pearl Harbor | 26 Nov to 7 Dec 1941 (posts 26 Nov to 7 Dec 2026) | 12 | **Built and scheduled 11 Nov 2026**: all 48 posts in Buffer. Records in `campaign-series/pearl-harbor-1941/`. Volume: Part 1 mocked up 14 Nov; Parts 1 to 3 to finish before 30 Nov. |
| The Bulge | 16 Dec 1944 to 14 Jan 1945 | 30 | Planned (anchor days below). Build sitting: Thanksgiving weekend, 26 to 29 Nov 2026, for the 30 days of posts only. Its 4 Substack parts are written in short sittings about a week before each goes live (about 24 Dec, 1 Jan, 8 Jan, 15 Jan; dates set by the split). |
| Next series | Anzio (landing 22 Jan 1944), then Remagen, Okinawa, Black May or Coral Sea, D Day or Midway, Kursk or Sicily, Battle of Britain, Market Garden, Leyte Gulf or El Alamein, Guadalcanal or Tarawa, Pearl Harbor and Wake Island | | Same campaigns as the Campaigns Roadmap, but each series runs on the real dates, not the game month. Alternates not decided. |

## Decided (11 Nov 2026, Brian)
* **Slot: 6:30 a.m. Mountain**, its own slot, separate from every other (8 a.m., 10 a.m. Name This, noon video, 2:30 p.m., 5 p.m., 7 p.m. video).
* **Platforms: X, Threads, Instagram, Facebook.** No YouTube or TikTok version, never Story Cards.
* **Not a card and never in Declass.** No dispatch number, no series stamp, no Declass line, no `dispatches/` record.
* **Same event allowed in the regular slots, only the wording differs.** The series is written first; the cards and video runs read `campaign-series/<series>/day-NN.json` and never reuse its sentences or hooks (Cards and Videos docs).
* **Built in one sitting per series**, no new scheduled task.
* **Same campaigns as the Campaigns Roadmap, on the real timeline** (12 Nov 2026, Brian): the game releases each campaign on the 1st of its month, but its Campaign Series starts on the event's actual dates (Anzio begins with the 22 January 1944 landing, while the game opens 1 February). Where two real timelines overlap, both run.
* **Overlaps are staggered** (12 Nov 2026, Brian): more content is a good thing. The series that started first keeps 6:30; the next one posts at 6:45 for as long as both run, and a third (rare) at 7:00. A series keeps its slot for its whole run, so followers know when to look. The day record's `time` holds the slot. Nothing in the series ever posts at 8 a.m. or later.
* **Focused windows, never overextended** (12 Nov 2026, Brian): real campaigns ran for months; a series covers only the stretch that tells the story best (the decisive days the game chapters cover, plus a short lead in), usually about two to four weeks. The window is chosen in that series' sitting.
* **Hard cap: 30 days** (12 Nov 2026, Brian). No series runs longer than 30 days, no exceptions, so no sitting gets out of hand.

## The look (locked 11 Nov 2026: C, Teletype tape)
Canvas: "Campaign Series Bulletin Mockup" (https://claude.ai/artifact/HKsV6D4kmGzoZ7X3nimzE3). Drawn by `renderer/campaign.html` with `node renderer/campaign.js <series> [day ...]`.
* The archival photo fills the frame, in grayscale.
* **Top tab** (cream #EFE6D2 with grain, top left): "CAMPAIGN SERIES" small in Oswald over the series name in Oswald bold ink navy and "DAY N" in teletype red #B04A3E.
* **Bottom strip** (cream, full width, a little above the bottom): the one line subtitle in Oswald bold (38 characters max, present tense, says what today's post is about; the renderer shrinks it slightly or prints a PROBLEM line), then "BULLETIN · 28 NOV 1941 · PEARL HARBOR, HAWAII" in Special Elite and @ww2dispatches at right.
* **Sizes:** X 1600 x 1440 (strip lifted clear of X's ALT badge); Instagram 1080 x 1350, also used for Threads and Facebook. Files: `campaign-series/<series>/images/day-NN-x.jpg` and `-instagram.jpg`.
* Japanese and other foreign events go by their own local date (the fleet left Hitokappu Bay on 26 Nov, Tokyo time).

## Caption style
* **Present tense, told as it happens, hook first.** X, Instagram, Facebook about 400 to 700 characters; Threads under 500.
* **No hindsight past the series' end.** Dramatic irony is fair ("Hawaii is not on the list").
* Written only from verified facts, two sources for each, with the sources listed in the day record. No dashes.
* **Fixed last line:** "Pearl Harbor · Day 3 of 12" (the series name and day).
* **Hashtags:** Instagram `#OnThisDay #WW2 #<Event>`; X and Facebook `#OTD #WW2 #<Event>`; Threads none, filed in History Threads.
* **No add on lines ever** (no question, newsletter, support, or Declass line). The one exception: the Bulge posts on 1 and 11 January carry one Campaigns line, since those are Campaigns chapter days.
* **Alt text** starts "WW2 Dispatches Campaign Series, <Series>, Day N." then the photo credit.
* **Flash days:** the series post on a Flash day (Pearl Harbor 7 Dec, the Bulge 16 Dec) must not use the moment a Flash Traffic bulletin covers (Roadmap). Pearl Harbor Day 12 is the midget submarines' release, leaving the Condor sighting to the 6:50 bulletin.

## The day record
`campaign-series/<series>/day-NN.json`: campaign, seriesName, day, days, date (YYYY-MM-DD, the historical date), time ("06:30"), series (battle, home, blue, state, for the analytics), place, subtitle, photo, photoCredit, focusX, focusY, zoom, body, threads (complete, with the footer), footer, hashtags (Instagram), hashtags_xf (X and Facebook), alt, sources, somber (optional), and `buffer` {x, instagram, threads, facebook}. Fixes go to the record first, then the Buffer post.

## The volume: Substack parts (decided 14 Nov 2026, Brian; replaces the weekly roundups)
The socials stay exactly as they are. The deep version of each series is its **volume**: 3 or 4 long parts on Substack, and the same parts are what the series' book on the Campaign Shelf holds. Each part reads like a chapter of a bound history of the campaign, not a recap of the posts.

**Every part carries (the chapter standard):**
* **An authentic map**, period or official history (U.S. Army, Navy, or Marine Corps histories, West Point atlas maps, wartime situation maps), public domain, captioned to say what it shows. At least one per part; Part 1 always opens on the campaign map.
* **The decision makers in their own words**: presidents, prime ministers, ministers, generals, admirals, on both sides, from diaries, memoirs, cables, minutes, and testimony.
* **First hand accounts**: soldiers, sailors, airmen, civilians, reporters who were there (letters, diaries, oral histories, after action reports, interviews).
* **At least one primary document set off in full or in a long extract** (an order, cable, broadcast, or report), labeled PRIMARY DOCUMENT or FROM THE RECORD.
* **Photos that tell the story on their own**: real public domain archival photos chosen so that someone who only looked at the pictures and captions would follow the part. Captions advance the story and give the credit. Better and more photos than the daily posts had.
* **The hindsight the daily posts can't have**: what the people on the day could not know, put side by side.
* **Length:** about 400 words for each day the part covers, so a 4 day part runs about 1,600 to 2,000 words and an 8 day part about 3,000 to 3,500.
* **Sources section** at the end, as a book's notes would.
* Quoting: public domain government records (orders, cables, testimony, official histories) can be quoted at length. Copyrighted memoirs and books get short quotes only (under 15 words, one per source) and are otherwise paraphrased and cited. Every quote is checked against its source; no quote from memory. No dashes.

**Splitting and timing**
* **3 parts** for a series up to about 15 days, **4 parts** for a longer one (the 30 day cap means never more than 4).
* Parts split at the story's turning points, kept roughly even (3 to 10 days each).
* **Each part goes live at 9 a.m. Mountain the morning after its last day runs.** If that morning is a Sunday, it moves to Monday, so it never shares a day with the Weekly Dispatch. Timing follows the campaign timeline, not a fixed weekday.
* It is never published before its last day has run, so it never gets ahead of the daily posts.

**The look (different from the Weekly Dispatch)**
Substack sets one theme for the whole publication (night background, brass gold, Anton titles, Libre Baskerville body, drop caps) and allows no custom code, so the difference comes from inside the post:
* **Cover** (revised 14 Nov 2026, Brian), drawn by `renderer/campaign_article.html` with `node renderer/campaign_article.js <series> <part>`: the grayscale photo on top with **nothing laid over it**, then a cream panel under a thin red rule holding "CAMPAIGN SERIES · <SERIES> · PART N OF M" (part in red), the part title in Oswald bold, a **one line synopsis** in Libre Baskerville italic (`synopsis` in the part record), and the dates ("26 TO 29 NOVEMBER 1941") with WW2 DISPATCHES at right. No "bulletins". 1456 x 1048 (Substack's 14:10 thumbnail), with the panel text inside the middle 1.91:1 band so social previews keep it all. Set as the post's thumbnail and placed at the top of the post. (Weekly Dispatch covers are a dark photo with a white serif title and a gold tab.)
* **Every part has its own cover photo** (Brian, 14 Nov 2026): a photo of that part's defining moment, never the book's cover on the Campaign Shelf, never another part's photo, and preferably not a photo the daily posts already used, so each part opens on something new. Read in order, the part covers should tell the volume's story by themselves. Pearl Harbor: Part 1, Zuikaku weighing anchor at Hitokappu Bay, 26 Nov 1941 (80-G-71198); Part 2, Kaga in heavy North Pacific seas with Zuikaku beyond, early Dec 1941, a frame from film shot aboard Akagi and found on Kiska in 1943 (NH 75483); Part 3, a Kate taking off from Shokaku on the morning of 7 Dec (80-G-182249; backup 80-G-182248, Shokaku's captain watching the launch). Chosen clear of the Flash card's moment.
* **Title:** "<Series>, Part N: <Part title>", subtitle opens with the dates ("26 to 29 November 1941. ...").
* **Written as a book chapter, not bulletins** (14 Nov 2026, Brian: the Substack audience are readers, so no teletype devices in the text). Each day is a section with a short literary title as a heading ("The Sortie") and an italic dateline under it ("*Hitokappu Bay, Kuril Islands, 26 November 1941*").
* **Set off documents and voices** as block quotes that open with a bold label in sentence case (**Primary document.**, **From the record.**, **In their words.**) and end with a source line.
* **End of part:** a rule, then one italic line "*Next: Part 2, 30 November to 3 December 1941.*" with a sentence on what it covers and the day it arrives, then a heading "The daily dispatches, Days 1 to 4" with a gallery of that part's daily images (Substack's image gallery), then Sources.
* **Section:** a **Campaign Series** section on the Substack with its own email banner, `campaign-series/brand/campaign-series-email-banner.png` (1100 x 220, and @2x): a cream teletype tape with feed holes on the night color, "CAMPAIGN SERIES" and "WW2 DISPATCHES · THE CAMPAIGN, DAY BY DAY, IN FULL" in red. No photo, so it fits every campaign. (Check in the browser that Substack shows a section's own banner on its emails; if not, the cover at the top of the post does that job.) Readers can opt in or out of the section's emails apart from the Weekly Dispatch.

**Files:** `campaign-series/<series>/articles/part-NN.json` (part, parts, days [first, last], first, last, title, substackTitle, subtitle, synopsis, publish, coverPhoto, coverCredit, focusX, focusY, status) and `part-NN.md` (the article). `python3 renderer/campaign_article_preview.py <series> <part>` builds a preview styled like the Substack post page in `articles/preview/`. Extra photos and maps go in `photos/campaign/`.

**Posting:** Substack has no connector or API. In the build sitting Claude writes and checks every part and makes the covers; the parts are then set up in Substack as scheduled posts (Claude in the built in browser if Brian is signed in, otherwise Brian pastes each part from the preview, about 10 minutes a part).

**Pearl Harbor volume (3 parts)**
| Part | Days | Title | Goes live |
|---|---|---|---|
| 1 | 1 to 4 (26 to 29 Nov) | The Fleet Slips Away | Mon 30 Nov, 9 a.m. (mock up written 14 Nov) |
| 2 | 5 to 8 (30 Nov to 3 Dec) | to write | Fri 4 Dec, 9 a.m. |
| 3 | 9 to 12 (4 to 7 Dec) | to write | Tue 8 Dec, 9 a.m. |

## Pearl Harbor (26 Nov to 7 Dec 1941, scheduled)
| Day | Date | Subtitle | Photo |
|---|---|---|---|
| 1 | 26 Nov | Six carriers slip out of the Kurils | Zuikaku at Hitokappu Bay, Nov 1941 |
| 2 | 27 Nov | Washington sends a war warning | Adm. Stark, NH 49967 |
| 3 | 28 Nov | Enterprise sails under war conditions | Enterprise, June 1941 |
| 4 | 29 Nov | Old prime ministers voice doubts | Adm. Okada |
| 5 | 30 Nov | A prince warns his brother | Prince Takamatsu |
| 6 | 1 Dec | Tokyo decides on war | Tojo, 1941 |
| 7 | 2 Dec | Climb Mount Niitaka | Akagi's flight deck, Hitokappu Bay |
| 8 | 3 Dec | Japan's embassies burn their codes | US built Purple machine, NARA 518142 |
| 9 | 4 Dec | A secret war plan hits page one | Wedemeyer, author of Rainbow Five, about 1942, Signal Corps 196260 (supplied by Brian; small original) |
| 10 | 5 Dec | The last carrier leaves Pearl Harbor | Lexington, 80 G 416362 |
| 11 | 6 Dec | Washington reads Tokyo's answer | Hull, Nomura, Kurusu, 17 Nov 1941 (small original, a bit soft) |
| 12 | 7 Dec | Five midget submarines in the dark | HA 19 aground, Dec 1941 |

## The Bulge (16 Dec 1944 to 14 Jan 1945, Days 1 to 30, to build)
Anchor days, each to be verified in the sitting (two sources); the rest are filled there, with Home Front and Blueprint days mixed in (the proximity fuze's first ground use, the Christmas news at home).
* D1 16 Dec: the barrage opens in the Ardennes before dawn (also the Bulge Flash day; avoid the Flash card's moment).
* D2 17 Dec: the Baugnez crossroads massacre near Malmedy (somber, plain facts).
* D3 18 Dec: the 101st Airborne races to Bastogne; engineers blow the bridge in front of Peiper.
* D4 19 Dec: two regiments of the 106th surrender on the Schnee Eifel; at Verdun, Patton promises to attack within days.
* D5 20 Dec: Eisenhower gives Montgomery the northern armies.
* D6 21 Dec: St. Vith falls; the ring closes on Bastogne.
* D7 22 Dec: the surrender demand and McAuliffe's answer, told in new words (the Campaigns debrief already uses its own).
* D8 23 Dec: the skies clear and the drops begin.
* D9 24 Dec: the high water mark near the Meuse; Christmas Eve.
* D10 25 Dec: the Christmas attack at Bastogne; 2nd Armored at Celles.
* D11 26 Dec: Abrams's tanks break into Bastogne.
* D17 1 Jan: Bodenplatte (Campaigns chapter 1 opens: Campaigns line).
* D19 3 Jan: First Army attacks from the north.
* D23 7 Jan: Montgomery's press conference.
* D24 8 Jan: Hitler allows the pullback.
* D27 11 Jan: Campaigns chapter 2 opens (Campaigns line).
* D28 12 Jan: the Soviet winter offensive opens in Poland.
* D30 14 Jan: the last day; the First and Third Armies close on Houffalize from both sides (the link up comes on the 16th, after the series ends).

## On ww2dispatches.com (the Campaign Shelf)
**All website work belongs to the Website: Build and Fixes chat** (Brian, 15 Nov 2026). This chat and the build sittings only write the series files (day records, `articles/part-NN.json` and `.md`, covers, photos) and keep `shelf.json` current; the Website chat decides how the site shows them.

**Handed to the Website chat (15 Nov 2026): rebuild the Campaign Shelf around the Substack parts.** The parts are the main pull. The proposal from this chat, for the Website chat and Brian to adopt or change:
* **The shelf** stays as built (a row of spines).
* **A book opens to a title page and contents:** the book's cover, a short introduction (the campaign, its dates, why it mattered), then the parts as chapters, each with its own part cover, title, synopsis, and dates. A published part reads "Read Part 1"; a part not yet out shows sealed with "Arrives 4 December" (like the sealed Flash cards in Declass).
* **A part page is the chapter:** the full article from `articles/part-NN.md` (maps, documents, photos, sources), styled as a page of the book (cream paper, serif type), with previous and next part links and a subscribe on Substack box. A part appears once its `publish` time has passed.
* **The daily 6:30 posts are secondary. Options for Brian to choose from (or combine):**
  * **(a) A strip at the end of each part:** that part's days in a row (day, image, subtitle), tap one for the caption as it ran.
  * **(b) An appendix at the back of the book,** "The Dispatches, Day by Day": every post in order, after the last part. Keeps the chapters pure reading; fits the book idea best.
  * **(c) Margin notes beside each day's section:** each dated section in a chapter carries a small card in the margin (thumbnail, "Day 3 · as it ran at 6:30", subtitle) that opens the post. The reader sees the feed version right next to the deeper telling of the same day. On phones it sits as a slim line under the dateline.
  * **(d) Two editions of the book:** a toggle at the top of the volume page, "The book" (the parts) and "The daily edition" (the posts as a day by day log). One volume, two ways to read it; the book is the default.
  * **(e) A timeline ribbon on the title page:** one mark per day across the top of the volume page, with each part's span shaded and labeled. Tapping a day shows its post in a small pop up; tapping a shaded span opens that part. Shows the shape of the campaign at a glance.
  * **(f) Loose dispatch slips tucked in the book:** at the end of each part, the day posts appear as loose cream slips you can flip through like papers tucked between the pages (a small swipeable stack), in the daily posts' Teletype look.
  * **(g) Links only:** no posts on the site. Each part ends with a line inviting readers to follow the next series live at 6:30 on Threads and the other platforms, with links to the original posts for that part's days.
  * **(h) Dropped from the site** entirely, with no links.
  * With any option that shows the posts (a to f), a series whose Part 1 is not out yet shows the days already run under "In progress", so the book is never empty in its first days. With (g) or (h), the book shows a sealed Part 1 with its date and a link to follow the series live.

* Files the site can read: `campaign-series/<series>/articles/part-NN.json` (part, parts, days, first, last, title, substackTitle, subtitle, synopsis, publish, coverPhoto, coverCredit, focusX, focusY) and `part-NN.md` (markdown: `##` section titles with an italic dateline under each, `![caption](photo)` images, block quotes opening with a bold label, a `---` before the closing "Next" line, then Sources); covers in `articles/images/part-NN-cover.jpg`; `renderer/campaign_article_preview.py` shows how the Substack version reads.

Until that change ships, the shelf works as built: every series is a volume on the Campaign Shelf at ww2dispatches.com/campaign-series (Site Revamp doc). `renderer/site_pages.py` builds the volume page and one page per day from the day records, and the server shows a day only once its post time has passed. **In each build sitting:** add the volume to `campaign-series/shelf.json` (its `id` must match the folder name, so the Bulge is `bulge-1944`; set the cover photo, cloth color, intro, and blurb), then run `python3 renderer/series_log.py` before the commit, which refreshes the pages with the logs. A volume turns live on the shelf as soon as its folder holds day records.

## Open
* Pearl Harbor volume: download the three part cover photos (80-G-71198, NH 75483, 80-G-182249) and rerender Part 1's cover; Brian approves the Part 1 mock up; then finish Part 1 and write Parts 2 and 3; make the Campaign Series section on Substack with its banner and schedule all three (Part 1 by Mon 30 Nov, 9 a.m.).
* Website: Build and Fixes chat: rebuild the Campaign Shelf around the Substack parts (above), ideally before Part 1 goes live on Mon 30 Nov; Brian picks the daily posts option (a to h) there.
* The Bulge build sitting (Thanksgiving weekend): the 30 days of posts and the split into 4 parts; each part then written in its own short sitting about a week ahead.
* **From now on, long series work the same way** (Brian, 14 Nov 2026): the build sitting does the daily posts and the part split; parts are written in short sittings ahead of their dates. Short series like Pearl Harbor can do the parts in one sitting.

## Changelog
* 11 Nov 2026: Idea decided in principle and handed off (slot, platforms, not a card, Bulge dates, Pearl Harbor first, one sitting per series).
* 11 Nov 2026 (night, Campaign Series chat): Look C locked and drawn by the new `renderer/campaign.html`; caption style set; Pearl Harbor set at 26 Nov to 7 Dec (12 days), researched, written, rendered, and 44 posts scheduled in Buffer (Day 9 waits on a photo); same event allowed in the regular slots with different wording (rule added to the Cards and Videos docs); Substack set as weekly web only roundups in a Campaign Series section; the `campaign-series` skill built.
* 11 Nov 2026 (later): Day 9 scheduled with Brian's Signal Corps photo of Wedemeyer; its caption now names him as the plan's author under suspicion.
* 12 Nov 2026 (site revamp chat): the Campaign Shelf built on the `site-revamp` preview branch; build sitting step added (shelf.json, then series_log.py).
* 12 Nov 2026: Series follow the Campaigns Roadmap's campaigns on their real dates, not the game months (Brian); Stalingrad dropped from the list.
* 12 Nov 2026 (later): overlapping series run together, staggered at 6:30, 6:45, and 7:00 (Brian).
* 12 Nov 2026 (later): series keep to a focused window of the campaign, never the whole thing (Brian).
* 12 Nov 2026 (later): hard cap of 30 days per series (Brian); the Bulge trimmed to 16 Dec to 14 Jan (30 days), so it no longer overlaps Anzio.
* 14 Nov 2026: Substack plan replaced (Brian): no weekly roundups; each series becomes a volume of 3 or 4 in depth parts that read as chapters of a bound book (authentic maps, decision makers in their own words, first hand accounts, a primary document, photos that tell the story), each live at 9 a.m. the morning after its last day (Sunday moves to Monday), in its own Campaign Series section with a teletype tape banner and Teletype look covers; the Campaign Shelf to hold the parts, with the daily posts as a timeline inside. New `renderer/campaign_article.html`, `campaign_article.js`, and `campaign_article_preview.py`; Pearl Harbor Part 1 mocked up.
* 14 Nov 2026 (later): each part gets its own cover photo tied to that part's moment (Brian); Pearl Harbor's three picked.
* 14 Nov 2026 (later): cover redone with the photo clear and a cream panel carrying a one line synopsis instead of "bulletins"; the article drops the teletype bulletin breaks for titled, datelined sections, written for readers (Brian).
* 14 Nov 2026 (later): the Bulge sitting covers only the posts; its parts are written in short sittings ahead of each date (Brian).
* 15 Nov 2026: all website work moved to the Website: Build and Fixes chat (Brian); the Campaign Shelf rebuild handed there with this chat's proposal and eight options (a to h) for the daily posts.
