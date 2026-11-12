# WW2 Dispatches: Campaign Series

A daily social media serial that follows one campaign day by day, told as it happened, the RealTimeWWII way. Each series is researched, written, rendered, and scheduled **in one sitting** with the `campaign-series` skill, in the Campaign Series chat. **No scheduled task** runs it. The weekly runs only read its files so their wording never repeats it (Cards and Videos docs).

## Status
| Series | Dates | Days | State |
|---|---|---|---|
| Pearl Harbor | 26 Nov to 7 Dec 1941 (posts 26 Nov to 7 Dec 2026) | 12 | **Built and scheduled 11 Nov 2026**: 44 posts in Buffer (Days 1 to 8 and 10 to 12). **Day 9 waits on a photo from Brian** (Rainbow Five, 4 Dec). Records in `campaign-series/pearl-harbor-1941/`. |
| The Bulge | 16 Dec 1944 to 25 Jan 1945 | 41 | Planned (anchor days below). Build sitting: Thanksgiving weekend, 26 to 29 Nov 2026. |
| Stalingrad | later year | | Candidate (photos mostly Soviet or German, so harder). |

## Decided (11 Nov 2026, Brian)
* **Slot: 6:30 a.m. Mountain**, its own slot, separate from every other (8 a.m., 10 a.m. Name This, noon video, 2:30 p.m., 5 p.m., 7 p.m. video).
* **Platforms: X, Threads, Instagram, Facebook.** No YouTube or TikTok version, never Story Cards.
* **Not a card and never in Declass.** No dispatch number, no series stamp, no Declass line, no `dispatches/` record.
* **Same event allowed in the regular slots, only the wording differs.** The series is written first; the cards and video runs read `campaign-series/<series>/day-NN.json` and never reuse its sentences or hooks (Cards and Videos docs).
* **Built in one sitting per series**, no new scheduled task.

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
* **No add on lines ever** (no question, newsletter, support, or Declass line). The one exception: the Bulge posts on 1, 11, and 21 January carry one Campaigns line, since those are Campaigns chapter days.
* **Alt text** starts "WW2 Dispatches Campaign Series, <Series>, Day N." then the photo credit.
* **Flash days:** the series post on a Flash day (Pearl Harbor 7 Dec, the Bulge 16 Dec) must not use the moment a Flash Traffic bulletin covers (Roadmap). Pearl Harbor Day 12 is the midget submarines' release, leaving the Condor sighting to the 6:50 bulletin.

## The day record
`campaign-series/<series>/day-NN.json`: campaign, seriesName, day, days, date (YYYY-MM-DD, the historical date), time ("06:30"), series (battle, home, blue, state, for the analytics), place, subtitle, photo, photoCredit, focusX, focusY, zoom, body, threads (complete, with the footer), footer, hashtags (Instagram), hashtags_xf (X and Facebook), alt, sources, somber (optional), and `buffer` {x, instagram, threads, facebook}. Fixes go to the record first, then the Buffer post.

## Substack (decided 11 Nov 2026)
* **Weekly roundups**, not daily posts: each daily post is about 100 words, so one per day would be thin and repeat the socials; a week gathers 5 to 7 days into a 600 to 900 word diary with the photos.
* Filed in a **Campaign Series section** on the Weekly Dispatch Substack, **web only** (no email sent). The Sunday Weekly Dispatch can link the latest roundup.
* Pearl Harbor: two roundups, Sun 29 Nov (Days 1 to 4) and Mon 7 Dec evening (Days 5 to 12). The Bulge: one each Sunday plus a final one on 25 Jan.
* Made and scheduled in the build sitting through the browser (Substack has no posting API). **Not yet done for Pearl Harbor**: the section and the two roundups are made in the Bulge sitting, before 29 Nov.

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
| 9 | 4 Dec | A secret war plan hits page one | **Waiting on Brian's photo** (a 1929 Stimson portrait is rendered as a placeholder; not scheduled) |
| 10 | 5 Dec | The last carrier leaves Pearl Harbor | Lexington, 80 G 416362 |
| 11 | 6 Dec | Washington reads Tokyo's answer | Hull, Nomura, Kurusu, 17 Nov 1941 (small original, a bit soft) |
| 12 | 7 Dec | Five midget submarines in the dark | HA 19 aground, Dec 1941 |

## The Bulge (16 Dec 1944 to 25 Jan 1945, Days 1 to 41, to build)
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
* D32 16 Jan: First and Third Armies meet at Houffalize.
* D34 18 Jan: Churchill tells the Commons it is the greatest American battle of the war.
* D37 21 Jan: Campaigns chapter 3 opens (Campaigns line).
* D39 23 Jan: St. Vith retaken.
* D41 25 Jan: the battle's official end.

## Open
* Day 9 photo (Brian), then render, push, and schedule Day 9.
* The Substack section and the two Pearl Harbor roundups (Bulge sitting, before 29 Nov).
* The Bulge build sitting (Thanksgiving weekend).
* Idea for its own chat (Brian, 11 Nov 2026): a page on ww2dispatches.com holding every Campaign Series, styled a bit like a bookshelf. The day records in `campaign-series/<series>/` (images, captions, sources) are the data it would read.

## Changelog
* 11 Nov 2026: Idea decided in principle and handed off (slot, platforms, not a card, Bulge dates, Pearl Harbor first, one sitting per series).
* 11 Nov 2026 (night, Campaign Series chat): Look C locked and drawn by the new `renderer/campaign.html`; caption style set; Pearl Harbor set at 26 Nov to 7 Dec (12 days), researched, written, rendered, and 44 posts scheduled in Buffer (Day 9 waits on a photo); same event allowed in the regular slots with different wording (rule added to the Cards and Videos docs); Substack set as weekly web only roundups in a Campaign Series section; the `campaign-series` skill built.
