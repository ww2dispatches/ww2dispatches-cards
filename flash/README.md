# Flash cards: prepared art and records

A Flash card is the rare fifth card type, posted on the war's biggest days (Roadmap, "Flash cards plan"). Its art is prepared and approved here ahead of time, because the full art treatment (a careful colorization in the Kodachrome look) is not something an unattended run can do well.

Each Flash date gets two files, named for the posting date:

* `YYYY-MM-DD-<event>.jpg`: the finished full art, already colorized and approved by Brian. Full resolution, 4:5 or wider; the renderer crops it to the card.
* `YYYY-MM-DD-<event>.json`: the prepared partial dispatch record (id, date, series `flash`, title, short name, place, pull line, photo path, credits, framing, somber flag). The Wednesday research run copies it into `dispatches/` and fills in the rest (Research doc, "Flash days").
* `colorize-YYYY-MM-DD-<event>.py`: the colorization script that made the art, kept so it can be rerun or adjusted.

Prepared so far:
* **2026-12-07, Pearl Harbor** (the first Flash card): the USS Shaw explosion, NHHC NH 86118, colorized 25 Oct 2026 (treatment C2, Kodachrome, approved by Brian). Kicker "The Attack on Pearl Harbor" added 19 Nov 2026.
* **2026-12-16, The Bulge:** a German soldier points the attack west beside a German halftrack, NARA 208-AA-202B-4 (German photo, captured, U.S. National Archives; NARA's own copy, allowed under Brian's 19 Nov 2026 rule). Colorized 19 Nov 2026 (C2 Kodachrome, warm grade, Method A: `colorize-2026-12-16-the-bulge.py`, notes in `colors-2026-12-16-the-bulge.md`), approved by Brian. Kicker "The Battle of the Bulge", pull line "Germany strikes west". Somber.
