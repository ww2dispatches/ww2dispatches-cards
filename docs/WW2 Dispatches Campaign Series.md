# WW2 Dispatches: Campaign Series

A daily social media serial that follows one campaign day by day, told as it happened, the RealTimeWWII way. Each series is researched, written, rendered, and scheduled **in one sitting** with the `campaign-series` skill, in the Campaign Series chat. **No scheduled task** runs it. The weekly runs only read its files so their wording never repeats it (Cards and Videos docs).

## Status
| Series | Dates | Days | State |
|---|---|---|---|
| Pearl Harbor | 26 Nov to 7 Dec 1941 (posts 26 Nov to 7 Dec 2026) | 12 | **Built and scheduled 11 Nov 2026**: all 48 posts in Buffer. Records in `campaign-series/pearl-harbor-1941/`. Volume: Part 1 mocked up 14 Nov; Parts 1 to 3 to finish before 30 Nov. |
| The Bulge | 16 Dec 1944 to 14 Jan 1945 | 30 | Planned (anchor days below). Build sitting: Thanksgiving weekend, 26 to 29 Nov 2026, including its 4 Substack parts. |
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
* **Cover:** the Teletype look, drawn by `renderer/campaign_article.html` with `node renderer/campaign_article.js <series> <part>`: grayscale photo, cream tab "CAMPAIGN SERIES / <SERIES> / PART N OF M" (part in red), strip with the part title, "BULLETINS · 26 TO 29 NOV 1941", and WW2 DISPATCHES. 1456 x 1048 (Substack's 14:10 thumbnail), with everything inside the middle 1.91:1 band so social previews keep it all. Set as the post's thumbnail and placed at the top of the post. (Weekly Dispatch covers are a dark photo with a white serif title and a gold tab.)
* **Title:** "<Series>, Part N: <Part title>", subtitle opens with the dates ("26 to 29 November 1941. ...").
* **Bulletin breaks:** each day opens with a Substack code block of one line, "BULLETIN · 26 NOV 1941 · HITOKAPPU BAY", which shows as a strip of typewriter text. The Weekly Dispatch never uses code blocks, so this is the series' signature.
* **Set off documents and voices** as block quotes with a label line in bold (PRIMARY DOCUMENT ·, FROM THE RECORD ·, IN THEIR WORDS ·) and a source line under the quote.
* **End of part:** a code block "END OF PART 1 · NEXT · 30 NOV TO 3 DEC 1941", one line on what Part 2 covers and the day it arrives, then "ON OUR FEEDS · DAYS 1 TO 4" with a gallery of that part's daily images (Substack's image gallery), then Sources.
* **Section:** a **Campaign Series** section on the Substack with its own email banner, `campaign-series/brand/campaign-series-email-banner.png` (1100 x 220, and @2x): a cream teletype tape with feed holes on the night color, "CAMPAIGN SERIES" and "WW2 DISPATCHES · THE CAMPAIGN, DAY BY DAY, IN FULL" in red. No photo, so it fits every campaign. (Check in the browser that Substack shows a section's own banner on its emails; if not, the cover at the top of the post does that job.) Readers can opt in or out of the section's emails apart from the Weekly Dispatch.

**Files:** `campaign-series/<series>/articles/part-NN.json` (part, parts, days [first, last], first, last, title, substackTitle, subtitle, publish, coverPhoto, coverCredit, focusX, focusY, status) and `part-NN.md` (the article). `python3 renderer/campaign_article_preview.py <series> <part>` builds a preview styled like the Substack post page in `articles/preview/`. Extra photos and maps go in `photos/campaign/`.

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
**Change decided 14 Nov 2026 (for the site revamp chat):** each book on the shelf holds the series in its **Substack form**. The volume page opens to its 3 or 4 parts (title, dates, cover), and each part page is the full article from `articles/part-NN.md`, with its maps, documents, and photos. The daily posts stay, but only as a compact "day by day" timeline inside each part (day, image, subtitle, one line), not as the main pages. A part shows on the site once its `publish` time has passed, the same way days do now. Until a part is live, the book shows the days already run as it does today.

Until that change ships, the shelf works as built: every series is a volume on the Campaign Shelf at ww2dispatches.com/campaign-series (Site Revamp doc). `renderer/site_pages.py` builds the volume page and one page per day from the day records, and the server shows a day only once its post time has passed. **In each build sitting:** add the volume to `campaign-series/shelf.json` (its `id` must match the folder name, so the Bulge is `bulge-1944`; set the cover photo, cloth color, intro, and blurb), then run `python3 renderer/series_log.py` before the commit, which refreshes the pages with the logs. A volume turns live on the shelf as soon as its folder holds day records.

## Open
* Pearl Harbor volume: Brian approves the Part 1 mock up; then finish Part 1 and write Parts 2 and 3; make the Campaign Series section on Substack with its banner and schedule all three (Part 1 by Mon 30 Nov, 9 a.m.).
* The site revamp chat: switch the Campaign Shelf books to the Substack form (above).
* The Bulge build sitting (Thanksgiving weekend), with its 4 parts split at the story's turns.

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
