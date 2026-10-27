# Declass server tests

Fake day tests for the opening logic (build session 3). They run against a local copy of the
server and a throwaway database, never the live site.

1. `node tests/declass/odds.mjs` checks the finish tables and the 1 in 6 living rate over 2 million rolls.
2. Swap in the synthetic catalog (two dispatches a day, 1 Aug 2026 to 31 Jan 2027, film every third
   morning, Name This on Wednesdays and Saturdays):
   `python3 tests/declass/synth.py functions/_data/catalog.json`
3. Start a local server with the test clock on:
   `npx wrangler pages dev site --d1 DB=declass --binding SIGNING_KEY=s ID_SALT=i GOOGLE_CLIENT_ID=g TESTER_KEY=t ALLOW_FAKE_NOW=1 --port 8799 --persist-to <tmp dir>`
4. Touch the database once (any signed in request), run `migrations/0001_init.sql` and `migrations/0002_intel.sql` into the local
   D1 sqlite file under `<tmp dir>/v3/d1/`, and insert test players `A` to `F` and `P0` to `P29`
   (ids are the letter plus 31 `x`).
5. `DB=<that sqlite file> node tests/declass/sim.mjs` runs 35 days of a daily player, streaks and
   priority envelopes, a missed day, Sunday deep archives, Pearl Harbor's commemorative file, the
   reroll guard (including 8 parallel tries), the waiting lock, expired and future envelopes,
   30 players racing for Top Secret serials, signatures, and the gate.
6. Put the real catalog back: `git checkout functions/_data/catalog.json`. Never commit the synthetic one.

First run, 24 Oct 2026: 548 passed, 0 failed. Session 4 rerun: 548 passed after fixing the serial check (the slot card can also come up as an archive pull, so it can get more than 30 serials).

The page itself was tested in a headless phone browser (390 by 844) with card images served from the repo. Locally, `x-declass-fake-google: <name>` on `/api/auth/google` signs in a test player without Google (only with `ALLOW_FAKE_NOW=1`).

Intel, requests, and ranks (25 Oct 2026) were checked by hand against a local server: 5 Intel per envelope, duplicates converting (first copy kept, Top Secret never), the today sum, requests (price, already held, today's card, unposted card, Name This, living price 30, a Top Secret request taking serial 1, the waiting lock, parallel requests with Intel for only one), and the rank endpoint. A year of simulated daily play earns about 117 Intel a week and fills about 1,280 spots. `sim.mjs` doesn't cover Intel yet; add cases when it next runs.

Intercept (27 Oct 2026): with the local server and database from steps 3 and 4 and the real catalog, `DB=<that sqlite file> node tests/declass/intercept.mjs` runs 42 server checks (deal once and no reroll, six starts at once, perfect solve and the 100 / 18 Intel payout, scores 90 and 80, already tried, three mistakes and the reveal, no card when not solved, four claims at once letting exactly one through, Silver or better on a perfect claim, parallel guesses, midnight Eastern expiry, the 90 day hard group rule with its fallback, no streak, Delete my dossier). `node --import ./tests/declass/json-loader.mjs tests/declass/intercept-check.mjs [day]` checks the master list and reports readiness; the Wednesday research run runs it. First run: 42 passed, 0 failed.
