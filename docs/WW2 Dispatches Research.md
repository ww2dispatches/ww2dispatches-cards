# WW2 Dispatches: Research

The rules for the **Wednesday research run**, the first build run of the week. It picks and locks the coming week's 14 slots, verifies everything, secures the film and photos, and publishes the slate the Thursday video run and the Friday cards run build from. Shared setup (series, brand, writing rules, photo rules and fetching workarounds, GitHub repos, Schedule Board tasks, push reminders, record keeping) is in the Project Brief. Film sources are in the Videos doc. The evening card formats are in the Cards doc. The slot layout is in the Roadmap. What the analytics have taught so far is in `analytics/playbook.md` (Analytics doc); **read it first** and follow its patterns and active tests.

## The job
By the end of Wednesday night, for each of the seven days from the coming Sunday through Saturday:
* the 8 a.m. event and the 5 p.m. event are chosen and verified,
* both dispatch numbers are assigned and locked,
* the film for the noon video is downloaded and checked, or the day is marked a Story Card,
* the lead photo for each card and the photos for any Story Card are downloaded,
* the dispatch JSON holds the fact sheet, the sources, the photo and film records, the short name and photo credit, the Declassified extra, and the theme tags,
* and the slate lists it all, with alternates, for Brian.

Research writes no captions, cuts no film, and renders nothing. Thursday and Friday do that.

## Video picks first
The noon video is the priority for growth, so **the 8 a.m. slot goes to the event on that date with the best usable film.** Of the events that happened on that calendar date in the era (1930s lead up through the late 1940s), look at the ones with a real story and pick the one with real public domain film that is clear, shows the event or its moment, and can open on motion (Videos doc, Living Cards). Clean period sound is a tiebreaker, never a requirement, and never at the price of weaker film. Film from a few days either side of the event is fine if the caption will say so (Aachen, No. 009, is the model). Only when no event on that date has usable film does the 8 a.m. slot go to the strongest story that can be told with four to six real archival photos, as a Story Card.

The 8 a.m. event is always the noon video's event. The noon video never switches to the 5 p.m. story.

## Picking the events
* **Read `analytics/playbook.md` first.** Follow its patterns and any active test; lean toward its hunches when choosing between equally good events. These rules still come first.
* Favor a real story: a twist, a vivid human detail, high stakes, or clever engineering.
* **The 5 p.m. evening card** is picked for the still card, in one of the three formats (Photo of the Day, Quote of the Day, Spec Sheet; the rules for each are in the Cards doc). It may cover a different event or the same event from another angle (the Kearny torpedoing at 8 a.m., then the Spec Sheet on why her design kept her afloat at 5 p.m.). At least two Spec Sheets a week when the dates allow, and no fixed weekday per format. A quote is verified word for word; every spec row must agree across sources or it is left out. Research picks the format and verifies its content; Friday renders it.
* **Mix the four series** across the week, with at least one Home Front. Glance at `log/series-counts.csv`; if one series is falling behind, lean toward it.
* **Never repeat** an event already covered: check `log/series-log.csv` and `dispatches/`.
* Check the Roadmap's "Upcoming big dates" for anniversaries in the batch week; those get the strongest treatment and the hardest film hunt (the iconic shot rule, Videos doc).
* Verify every fact per the Brief's writing rules. Never guess.
* Mark somber subjects `"somber": true` so Friday never adds an engagement question, a Ko-fi soft ask, or a newsletter mention to them.
* **Flash days** have their own rules (next section); on those days the 8 a.m. slot is already decided.

## Flash days
A **Flash card** is the rare fifth card type, for the war's biggest days (Roadmap, "Flash cards plan"). It has `"series": "flash"` and `"flash": true`, and it is a full art card made from prepared art rather than a photo hunt. The ten Flash dates are the Declass commemorative days: 19 Feb (Iwo Jima), 8 May (VE Day), 4 Jun (Midway), 6 Jun (D Day), 15 Aug (VJ Day), 1 Sep (the invasion of Poland), 2 Sep (the formal surrender), 15 Sep (Battle of Britain Day), 7 Dec (Pearl Harbor), 16 Dec (the Bulge). The first is **Mon 7 Dec 2026, Pearl Harbor** (the 85th anniversary).

When a Flash date falls in the batch week:
* **The 8 a.m. slot is the Flash card, always.** The event is the one on the list; the "never repeat" rule does not apply to it (each Flash date gets a new card every year, with a fresh angle and new art). No alternates are needed for that slot.
* **Start from the prepared record in `flash/`** (`flash/README.md`): copy `flash/YYYY-MM-DD-<event>.json` into `dispatches/<id>.json`, keep every field it carries (id, date, series, flash, title, short, place, pull, photo, photoUrl, photoNote, photoCredit, framing, somber) exactly as prepared, and add the fields research always writes: `num`, `facts`, `sources`, `themes`, `film`, `kind`, `videoPhotos`. The `photo` path points into `flash/`; that is the finished full art, already colorized and approved by Brian, so **do not download or swap the lead photo**. If no prepared record exists for the date, file a Schedule Board task and push reminder for Brian at once, and research the day as a normal 8 a.m. dispatch in the event's usual series, saying so in the summary.
* **The fact sheet, sources, and themes are researched as for any dispatch.** Verify every fact. The facts are what Friday writes the caption from.
* **Film is hunted as hard as for any big date** (the iconic shot rule, Videos doc): the noon video that day is the event's Living Card when usable film exists (Navy film of Pearl Harbor is in NARA's 428-NPC series), otherwise a Story Card. The video keeps the normal card frame with a FLASH stamp (Videos doc).
* **Numbers:** the Flash card takes its slot's number like any other card.
* **The 5 p.m. card that day** is picked and verified as usual, in a normal series. A Spec Sheet or Quote tied to the same event fits well.
* **Somber:** the prepared record carries `somber` where it applies (Pearl Harbor does); Friday skips the growth rules on it.
* **Never change the art.** The flash/ art is the card. Framing (focusX, focusY, zoom) is set in the prepared record and Friday keeps it.

## Securing the film
Finding film is not enough; a film that can't be fetched on Thursday night is a Story Card by default. So the research run gets the film into the repos.
* Use the film sources and the avoid list in the Videos doc. Read the Signal Corps shot cards to find the right moments.
* **U.S. government film on the NARA catalog:** download the MP4 into the videos repo's `footage/` (the whole reel if it is a reasonable size, otherwise the stretch that holds the shots), play enough of it to confirm it shows what the record says, note whether it carries its own period sound, and commit and push it.
* **Wikimedia Commons film** (the workspace can't download it): file a Schedule Board task for Brian with the exact file link and the 480p transcode link, due **Thursday 5:00 p.m. Mountain**, with a push reminder, asking him to save it into the WW2 Dispatches\Source Film folder. Mark the day's film `needs brian`. On Thursday the video run looks in Source Film first; if the file isn't there, the day becomes a Story Card for the same event.
* **Universal Newsreel:** confirm its public domain status on the NARA record before relying on it.
* Record everything in the dispatch JSON's `film` block (below). Also note promising film that wasn't used, in the slate's alternates, for later weeks.

## Securing the photos
* Follow the Brief's photo rules and fetching workarounds. Start early and space requests out; photo fetching is the slow, flaky part of the week, which is why it lives in this run.
* **Every card** gets its lead photo downloaded into `photos/` with its source page, license, and credit recorded (`photoUrl`, `photoNote`, and the clean `photoCredit` line).
* **Every Story Card day** gets four to six real archival photos of the event downloaded into `photos/` and listed in `videoPhotos` (file, page, credit). Living Card days get three to five photo leads as links only, in case the film falls through.
* **If a photo can't be fetched**, first try another event with one. If the event is worth keeping, file a Schedule Board task naming the photo wanted and its exact page, due Thursday 5:00 p.m. Mountain for a video photo or Friday 5:00 p.m. Mountain for a card photo, with a push reminder. Never leave a slot without a plan.

## The fact sheet
Every dispatch JSON gets a `facts` block: six to twelve verified facts in plain sentences, each with its source or sources, covering what happened, when, where, who, why it mattered, one vivid human or technical detail, and what came next. Dates, numbers, names, and ranks are exact.

**Everything written later draws only from the fact sheet:** the card caption and its Threads version (Friday), the Living Card caption, the Story Card script, and the vertical hook line (Thursday), and the newsletter's short version. No run adds a fact the sheet doesn't hold. If a later run needs a fact that isn't there, it writes around it rather than looking it up and adding it.

## Numbers are locked on Wednesday
* Work out the next dispatch number (one more than the highest `num` in `dispatches/`) and assign all 14 in date and time order: Sunday 8 a.m., Sunday 5 p.m., Monday 8 a.m., and so on.
* **A number belongs to its slot, not its event.** Once the slate is pushed, no run renumbers anything, because Thursday renders the number into every video frame. Swapping a day's event keeps its number.
* A noon video shares the number of the 8 a.m. dispatch it covers. Name This and the welcome post never take a number.

## What research writes in each dispatch JSON
Research owns: the file name and `id`, `num`, `date`, `time`, `series` (one of the four, or `flash` on a Flash day with `flash: true`), `title`, `short`, `place`, `pull`, `format` and its `quote`/`quoteBy` or `specTitle`/`specs` on evening cards, `facts`, `sources`, `photo` (the file in `photos/`) with `photoUrl`, `photoNote`, and `photoCredit`, `videoPhotos`, `film`, `somber`, `kind` (the planned noon video kind, `living` or `story`), and the `themes` block (who, story, photo, theater, branch, nations) using only the values in `analytics/themes.md`, and `declassified` (below).

Two of those are kept for the Declass game (Envelope doc) under the Brief's "Record now, use later" rule, and cost nothing extra once the research is done:
* **`short`:** a one to three word name for the card's subject, the way people would say it ("Aachen", "Leyte", "Taffy 3", "USS Reuben James"). It is the headline on Declass share pictures and the card's dossier label, so it names the subject only, never the card type: an evening card about the same event keeps the same name (the Kearny story and its Spec Sheet are both "USS Kearny"), because the game shows the format (Spec Sheet, Photo of the Day, Quote of the Day) on its own line. Ships take their prefix ("USS Hornet").
* **`photoCredit`:** one clean public line about the lead photo: what it shows, when, the archive and number, and the license, such as "Tirpitz in Bogen Bay, Norway, 1943 to 1944. NHHC NH 71390, public domain." No working notes, no "supplied by Brian", no framing advice; those stay in `photoNote`, which remains the team's working note.

**`declassified` (added 29 Oct 2026):** the reward a Declass player unlocks by holding the card in Gold, Top Secret, or Flash (Envelope doc). Research always finds more than one card can carry; this keeps the best leftover. Every dispatch gets one:
* `fact`: two or three plain sentences with one verified detail the card and its caption won't use, the kind a reader would want to repeat to someone: a behind the scenes moment, an odd number, what happened to a person afterward. Verified like any fact, never a guess. It must not repeat a fact sheet line, and Friday never uses it in the caption, Threads, or newsletter, so it stays a reward.
* `sources`: the source or sources for it (title and url, as in `sources`).
* `photo` (optional): one more real archival photo of the event that is not the card's lead photo, when a good one exists: `file` (in `photos/`), `page`, `credit` (a clean public line like `photoCredit`), and `caption` (one sentence on what it shows). On a Story Card day one of the `videoPhotos` that isn't the lead can be named here with no extra download. Leave it out rather than use a weak or unrelated picture.

Research leaves to Thursday: the `video` block (footage, focus, hook, source note), `themes.video`, `kit`, `story`, the film keys under `buffer`, and the cut clips. It leaves to Friday: `body`, `threads`, `addons`, `hashtags`, the framing (focusX, focusY, zoom), `slides`, `question`, `soft_ask`, `newsletter_mention`, `newsletter`, the card keys under `buffer`, and `links`.

The `film` block: `status` (`secured`, `needs brian`, or `none`), `record` (for example "111-ADC-2654 (NARA 16458)"), `url`, `file` (the path in the videos repo once downloaded), `sound` (true or false), `shot_notes` (which stretch holds the shots and what they show), `license`, and `date_note` when the film is from a different day than the event.

## The slate
`slate/YYYY-MM-DD.md` in the cards repo, named for the Sunday the week starts, committed and pushed with the dispatch JSON. One section per day, with for each slot: the number, time, series, event and year, planned kind (Living Card or Story Card), film record and sound, photo status, and anything open (a Brian task, an unconfirmed license). Under each 8 a.m. slot, **one or two alternates**: the event, the film record if known, and one line on why it is the backup. Alternates are lightly checked (event, date, likely film and photo), not fully verified; whichever is chosen gets full verification.

The slate is a picture of the week for Brian. It is not read by the renderers; the dispatch JSON is the record.

## Alternates and swaps
* Brian reads the slate in the research summary. If a default is fine, he does nothing.
* To swap a day, **he tells Claude in the Project by Thursday 7:00 p.m. Mountain.** Claude verifies the alternate fully, rewrites that dispatch JSON (same number, same slot), secures its film and photo, updates the slate, and pushes. The Thursday run builds whatever the JSON says when it starts.
* Research never waits for an answer. If nothing is said, the defaults build.

## Dispatch bank
Research owns the dispatch bank in `status.md` (aim for 5 to 7 verified evergreen dispatches with a secured photo, kept in `bank/`), adding to it when a strong undated story turns up and removing anything used. The video bank stays with the Thursday run (Videos doc).

## If a run fails
* **Research fails or doesn't push:** the Thursday video run does the minimum research itself for the seven 8 a.m. slots (film first, numbers locked for all 14 slots including the still empty evening ones, fact sheets, photos), builds the videos, and says so. The Friday cards run then fills the evening slots and writes the captions as usual.
* **Video run fails:** Friday builds the cards from the slate as usual, and the Schedule Board shows the empty noon slots. Claude in the Project builds the missing videos when Brian asks, or they are left for the next Thursday run, which fills any empty noon slot in the next seven days.
* **Cards run fails:** the videos are already scheduled. Claude builds the cards in the Project when Brian asks.
No run ever changes a locked number, a verified fact, or another run's fields to recover.

## Tasks, reminders, and the summary
File Schedule Board tasks and push reminders per the Brief's "Shared run procedures" for every film or photo Brian needs to supply and for anything uncertain. The summary to Brian (SendUserMessage) is the slate in short form: each day's 8 a.m. event, planned kind, film source and sound, and its alternates; each 5 p.m. card's format and subject; which playbook items shaped the picks; what Brian needs to supply and by when; and the line "Swap any day by telling me here before Thursday 7 p.m."

## Changelog
* 24 Oct 2026: Doc created. Research moved out of the Thursday cards run into its own Wednesday run, picking for film first, locking the numbers, writing one fact sheet per dispatch, and securing film and photos before the build runs. The week's order became Tuesday analytics, Wednesday research, Thursday videos, Friday cards.
* 24 Oct 2026 (evening): Research also writes `short` and `photoCredit` on every dispatch, for the Declass game (Envelope doc). Every existing dispatch and bank record was filled in once.
* 24 Oct 2026 (night): `short` now names the subject only, never the card type, since the Declass share picture shows the format on its own line. Twelve existing short names were cleaned up (for example "Kearny Hull" became "USS Kearny", "V-2 Photo" became "Earth from Space").
* 25 Oct 2026: Flash days added. On the ten Flash dates (the Declass commemorative days, first Pearl Harbor on 7 Dec 2026) the 8 a.m. slot is the Flash card, built from the prepared art and record in `flash/`; the never repeat rule does not apply to it, and research adds the number, facts, sources, themes, and film as usual.
* 27 Oct 2026: The Intercept master list upkeep was briefly written into this run, then moved the same day to the Tuesday analytics run (Analytics doc), so it only ever works from posted cards. Research does nothing for Intercept.
* 29 Oct 2026: Research also writes a `declassified` block on every dispatch (one unused verified fact with its source, and optionally one extra archival photo), for the Declass gold reward. Friday never uses it in captions. The 30 existing dispatches are being back filled once.
