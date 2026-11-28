# WW2 Dispatches: Index

Started 19 Nov 2026. The Index is the data layer under everything else: a **date bank** (verified candidate events for all 366 calendar dates) and an **entity layer** (the people, ships, units, aircraft, machines, places, and operations our cards are about). It exists so the archive can be browsed by more than date and series, so the research run starts from a stocked shelf, and so year two never runs dry. This doc holds the rules for both. The checker is `renderer/index_check.py` in the cards repo.

**Status (28 Nov 2026): built and wired in.** All 366 dates are banked (about 5,700 events after the 27 Nov clean pass), the entity layer is merged to `main`, the archive's date pages show the bank's headlines, and from Wed 2 Dec 2026 the research run starts from the bank (Research doc, "The date bank").

## Where it lives
* **The date bank is private:** repo `ww2dispatches/ww2dispatches-datebank`, folder `datebank/`, committed to `main`. It holds story notes on events we have not posted, so it stays out of the public cards repo (decided 19 Nov 2026, Brian).
* **The entity layer is in the cards repo,** folder `entities/`, with the checker at `renderer/index_check.py`. Built on the `index` branch and merged to `main` on 28 Nov 2026 (Brian). Background Index work may still use the `index` branch and is merged to `main` when done.
* The checker reads both: clone the two repos side by side.

## What it feeds
* **Research (Wednesday):** picks from the date bank instead of starting cold, marks what it uses, adds good new finds, and refreshes the date pages (wired in 28 Nov 2026, Brian; Research doc, "The date bank").
* **The archive date pages:** `renderer/export_timeline.py` writes the bank's open headlines to `timeline/onthisday.json` for the 366 pages at /on-this-day/ (live 28 Nov 2026).
* **The site:** entity pages (every card about USS Enterprise, about Patton, about the Eastern Front), a map from place coordinates, full "on this day" pages for dates with few cards yet, and a "your birthday in WW2" page.
* **Code Room:** groups can be planned ahead from the bank ("Approved groups waiting for cards") and found faster from shared entities.
* **Year two:** from 17 Oct 2027 every date needs three new events that have never run. The bank is that supply.

## Part A: the date bank
One file per calendar date, `datebank/MM-DD.json` in the private date bank repo, all years together.

**Target per date:** at least 8 open events, including at least 2 told from the Axis side (the 2:30 slot needs one every day) and at least 1 Home Front, spread across years, theaters, and series. Three cards a day use three events per date per year, so 8 or more is nearly three years of supply. **Never pad.** A date that honestly falls short is marked `"thin": true` with a note saying what it lacks.

**Era:** 1930 through 1949, the same span the dispatches cover.

**What an event holds:**
* `id`: `YYYY-MM-DD-short-name`. `year`, `title` (a working title, not a card title), `summary` (two or three plain sentences).
* `series`: Battle Lines, Home Front, Blueprint, or Statecraft. `theater`, `nations`, and `lens` use the values in `analytics/themes.md`, spelled exactly.
* `story`: the story test in three short notes, `person`, `stakes`, `twist`. Leave one empty rather than invent it.
* `tier`: **A** passes the whole story test and would carry an 8 a.m. slot. **B** is solid with one piece missing, or better suited to a format card. **C** is worth knowing, a filler or a callback.
* `sources`: at least two that are independent of each other, one of them an archive, museum, official history, or period document where possible. Title and link.
* `date_check`: `confirmed` when the sources agree on the date, or `disputed` with a `date_note` giving what each source says. A night action that crosses midnight, or a time zone that moves the date, gets a `date_note` too.
* `film`: leads only, as film index doc names or NARA numbers. `note`: photo leads, format ideas, cautions.
* `entities`: the one to five entities the event is about, by id.
* `status`: `open`, `used` (a dispatch covered this event), or `related` (a dispatch covered a neighboring part of the same story), the last two with the `dispatch` id.
* `somber`: true for loss and atrocity, as in the Research doc.

**The verification standard is the alternates standard.** A bank event is checked for its date, its core claim, and two sources. It is not a fact sheet. When research picks an event it still gets full verification, and no caption is ever written from a bank summary. Anything quoted, any number that could be challenged, and any "first" or "largest" is flagged in `note` for that later check.

**Flash dates and atrocities:** the sixteen Flash dates keep their Flash event out of the bank (it is decided already); bank the other events on those dates. Atrocities are banked as history from the victims' side, `somber`, and never tier ranked for drama: give them tier B and say so in `note`.

**Axis lens guardrails** from the Research doc apply to every Axis event banked.

## Part B: the entity layer
**The registry** is seven files in `entities/`, one per type, each a list keyed by id:

| File | Id starts | Holds |
|---|---|---|
| `people.json` | `person-` | named individuals |
| `ships.json` | `ship-` | individual ships, with hull number in the name where one exists |
| `units.json` | `unit-` | armies, divisions, wings, squadrons, crews, agencies |
| `aircraft.json` | `aircraft-` | aircraft types, and single named aircraft |
| `machines.json` | `machine-` | tanks, vehicles, weapons, devices, objects |
| `places.json` | `place-` | cities, islands, bases, buildings, with `lat` and `lon` |
| `operations.json` | `op-` | battles, operations, campaigns, conferences, programs |

Each entity has `name`, `kind` (a few plain words), `nation`, `source` (a page that was opened and confirms it), `wikidata` (the Q number, or `null`), and optionally `aka` and `note`. Ids are lowercase words joined by hyphens and never change once used.

**Three rules keep it clean:**
1. **Search before adding.** Check the registry, including `aka`, before creating an entity. The checker warns on matching names and Q numbers.
2. **Never guess a number.** A Wikidata number or a coordinate is copied from the page, or left `null`. The checker counts what is missing; a later pass fills it.
3. **Types, not instances, unless the instance is the story.** The B-29 is one entity; "Dauntless Dotty" earns her own only because a card is about her.

**Links** live in one file, `entities/links.json`: each record id from `dispatches/`, `namethis/`, or `bank/` with its entities and a role for each.
* `subject`: what the card is about. One to three.
* `involved`: takes part in the card's facts.
* `mentioned`: named in passing, such as a callback.

**Links come only from the record.** Tag what the record's own title, place, facts, caption, specs, photo credit, and Declassified fact say. Nothing is added from outside knowledge, so a link can never claim more than the card does. Name This cards are linked only after their answer is public.

Links sit in their own file, not in the dispatch records, so the backfill never touches a file the weekly runs are editing.

## The checker
`python3 renderer/index_check.py` from the repo root. It refuses bad ids, values not in `themes.md`, events with fewer than two sources, a disputed date with no note, a tier A with a missing story piece, links to unknown entities or records, and dashes used as punctuation. It reports coverage: dates done of 366, events, entities missing a Wikidata number or coordinates, and which records are still unlinked. Run it before every commit.

## Build order
1. **Entity backfill** (small, do first): link every posted dispatch, Name This card with a public answer, and bank record, growing the registry as it goes. About 150 records.
2. **Date bank, forward from 29 Nov**, a week at a time: 29 Nov to 5 Dec, then on through December and around the calendar, so the dates the research run reaches first are stocked first. Mark `used` and `related` from `log/series-log.csv` and `dispatches/` as each date is built.
3. **Second pass:** thin dates, missing Wikidata numbers and coordinates, and a blind recheck of dates on a sample (a fresh helper gets only the event titles and years and looks the dates up itself, as the Campaigns blind check does).
4. **Wiring, each needing Brian's OK:** research reads the bank and writes links for new cards; the site builds entity pages and the map; Code Room planning reads the bank.

**Working rules for the build:** commit and push in small batches (a week of dates, or 25 records) so a stopped session loses little; entities go to the `index` branch of the cards repo, the date bank to `main` of its own repo; change no dispatch record, no scheduled task, and no other doc.

## Decisions
* **Private date bank, public entities** (19 Nov 2026, Brian). See "Where it lives".
* **Depth: 8 or more open events per date** (19 Nov 2026, Brian), about 3,000 events.
* **Helper agents may run in parallel** during the build (19 Nov 2026, Brian): one per week of dates, plus the blind date check. Helpers return their work to the main session, which runs the checker and makes every commit, so two helpers never write the registry at once.

## Pilot (19 Nov 2026)
`datebank/11-29.json` holds 8 events as the worked example, including one disputed date (the Soviet recapture of Rostov, 28 or 29 November) and three `related` events. `entities/links.json` links No. 019 (USS Hornet) and the 24 Nov 1944 Tokyo B-29 dispatch. The pilot's 38 entities have no Wikidata numbers or coordinates yet, and their `source` links were written from memory, not opened: the build confirms each one first.

## Changelog
* 19 Nov 2026: Doc created with Brian. Format, checker, and pilot built and committed. Decided: the date bank in a private repo, 8 or more events per date, helper agents allowed.
* 27 Nov 2026: Clean pass applied (disputed dates, conflicting counts, lens values axis_romania, axis_hungary, vichy_france).
* 28 Nov 2026: Index merged to `main` (Brian). Research wired to the bank from Wed 2 Dec 2026, and the date pages read the bank's export. Lens values for the remaining Axis partners added in the date bank.
