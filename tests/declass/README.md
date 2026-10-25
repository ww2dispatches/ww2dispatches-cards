# Declass server tests

Fake day tests for the opening logic (build session 3). They run against a local copy of the
server and a throwaway database, never the live site.

1. `node tests/declass/odds.mjs` checks the finish tables and the 1 in 6 living rate over 2 million rolls.
2. Swap in the synthetic catalog (two dispatches a day, 1 Aug 2026 to 31 Jan 2027, film every third
   morning, Name This on Wednesdays and Saturdays):
   `python3 tests/declass/synth.py functions/_data/catalog.json`
3. Start a local server with the test clock on:
   `npx wrangler pages dev site --d1 DB=declass --binding SIGNING_KEY=s ID_SALT=i GOOGLE_CLIENT_ID=g TESTER_KEY=t ALLOW_FAKE_NOW=1 --port 8799 --persist-to <tmp dir>`
4. Touch the database once (any signed in request), run `migrations/0001_init.sql` into the local
   D1 sqlite file under `<tmp dir>/v3/d1/`, and insert test players `A` to `F` and `P0` to `P29`
   (ids are the letter plus 31 `x`).
5. `DB=<that sqlite file> node tests/declass/sim.mjs` runs 35 days of a daily player, streaks and
   priority envelopes, a missed day, Sunday deep archives, Pearl Harbor's commemorative file, the
   reroll guard (including 8 parallel tries), the waiting lock, expired and future envelopes,
   30 players racing for Top Secret serials, signatures, and the gate.
6. Put the real catalog back: `git checkout functions/_data/catalog.json`. Never commit the synthetic one.

First run, 24 Oct 2026: 548 passed, 0 failed.
