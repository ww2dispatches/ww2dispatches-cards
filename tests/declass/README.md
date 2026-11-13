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

Intercept (27 Oct 2026): with the local server and database from steps 3 and 4 and the real catalog, first swap in the test master list (`cp tests/declass/intercept-fixture.json functions/_data/intercept.json`; the live list holds only posted cards, so early on it can't deal a grid for a fake day), then `DB=<that sqlite file> node tests/declass/intercept.mjs` runs 42 server checks (deal once and no reroll, six starts at once, perfect solve and the 100 / 18 Intel payout, scores 90 and 80, already tried, three mistakes and the reveal, no card when not solved, four claims at once letting exactly one through, Silver or better on a perfect claim, parallel guesses, midnight Eastern expiry, the 90 day hard group rule with its fallback, no streak, Delete my dossier). `node --import ./tests/declass/json-loader.mjs tests/declass/intercept-check.mjs [day]` checks the master list and reports readiness; the Wednesday research run runs it. First run: 42 passed, 0 failed. Put the real list back afterwards: `git checkout functions/_data/intercept.json`; never commit the fixture as the live list.

Tester preview access (7 Nov 2026): `node --import ./tests/declass/json-loader.mjs tests/declass/preview-access.mjs` runs 14 checks in plain node, no server. After launch night wipes the players table, everyone signs in again with tester = 0, so the Code Room preview (?intercept=preview) also opens for file numbers on the admin list (`functions/_lib/admins.js` plus `ADMIN_FILES`) or in `TESTER_FILES`; `TESTER_FILES` never opens the admin console. The server suite above can't check this because the test clock opens the puzzle to everyone. First run: 14 passed, 0 failed (and 3 failed against the old check, as expected).

Carried starter pack (13 Nov 2026): `node --import ./tests/declass/json-loader.mjs tests/declass/carry-pack.mjs` runs 12 checks in plain node, no server. Social apps open links in their own built in browser, where Google refuses to sign anyone in, so the save screen there offers a link that carries the starter pack's signed token to the phone's real browser, and `POST /api/starter` with `{token}` reads it back (nothing drawn, nothing saved). Checks a good token, a tampered one, one edited to all gold, an expired one, and one signed with another key. First run: 12 passed, 0 failed. The page was also checked in a headless phone browser posing as Instagram and then as Safari (16 passed): the way out box replaces the Google button, the link carries the pack and the source, and the real browser lands on Save your dossier with the five cards. Not yet checked on a real phone inside a real app.

Automatic jump out of social app browsers (13 Nov 2026): a new visitor arriving at /declass inside a social app's browser is sent once to the phone's real browser (Safari on recent iPhones, the default browser on Android), carrying the source, any starter pack, the tester key on previews, and `out=1` so the arrival is counted. Checked in a headless phone browser posing as Threads on iPhone, Facebook on Android, Safari, and a desktop (13 checks): one jump per visit, none for a visitor already holding a pack, the right link for each phone, the game still usable when the jump is refused, `out_landed` counted and `out=1` removed on arrival, and visits with no ref named by the app itself (site/hit.js). A headless browser can only show that the jump is attempted, not that an app honors it. Not yet checked on a real phone inside a real app.
