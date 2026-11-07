# Campaigns engine checks

Build session 1 (6 Nov 2026). Plan: the Project doc "WW2 Dispatches Campaigns Build".

* `site/declass/campaigns/engine.js` holds every Campaigns rule as one plain module with no screen code.
  The page will play with it and the server will import the same file to replay a finished run from its
  seed and its list of choices before ranking it.
* `functions/_data/campaigns/` holds one campaign file per month (format 1, described in the Build doc).
  The Battle of Britain (August 1940) is the reference campaign. Bundled with the server, never served
  whole. Add each month's file shortly before that month, since the repo is public.

Run from the repo root, no server needed:

```
node --import ./tests/declass/json-loader.mjs tests/campaigns/engine.mjs
```

It checks the campaign file, deck rules, the seeded shuffle and replay (same seed and choices, same
result; unfinished or illegal runs refused), the opening hand and mulligan, the calm opening, the setup
turn, Supply, blocking and Rearming, escorts first, Statecraft (free, one a round, fixed reaches), the
airfield raids twist, and the score order. Then the automatic player (`bot.mjs`, the test bench's bot)
plays every chapter with the bench's two ready made decks, 400 runs each (`RUNS=` to change), and its win
rates must land where the bench's did.

The decks in `decks.mjs` are made up test cards, never posted dispatches: real card numbers stay in the
private score sheet until the seal reveal.

First run, 6 Nov 2026: 273 passed, 0 failed. Win rates (Fighter Command / Statecraft heavy):
chapter 1 about 90% / 52%, chapter 2 about 50% / 13%, chapter 3 about 29% / 4%.

One change from the test bench: an attack put off twice by Ultimatum no longer skips a step of its
unit's script (the bench advanced the script on the second hold as well).

## Server checks (build session 2, 6 Nov 2026)

`functions/_lib/campaigns.js` and `functions/api/campaign/` (index, start, finish, rank). The tables are
created on first use, like Intercept's; `migrations/0005_campaigns.sql` holds the same for the record, so
there is nothing to run in the D1 console. Campaigns stays closed until `CAMPAIGNS_LIVE` is true, except
to a tester sending `x-campaigns-preview: 1` (who gets the reference campaign with every chapter open).

With a local server and database as in `tests/declass/README.md` (steps 3 and 4, migrations 0001 to 0005):

```
DB=<the local D1 sqlite file> node --import ./tests/declass/json-loader.mjs tests/campaigns/server.mjs
```

It checks the campaign view signed out and in, chapter locks, runs left, deck checks on the server (size,
branch, dossier, no number yet, era), a full run replayed by the server with the same result as the page,
finishing once, another player's ticket, shared seeds (same run number same day, new seeds for the next
run and the next day), refused runs (unfinished, illegal) never ranked, three runs a day with abandoned runs
counted, winning to unlock the next chapter, each player counted once in the histograms, the percentile,
three finishes at once counted once, release dates to the minute, and the launch gate.

First run, 6 Nov 2026: 40 passed, 0 failed.

Build session 3 added two checks for the deck builder's reasons (42 passed, 0 failed).

## Page checks (build session 3, 6 Nov 2026)

`site/declass/campaigns/campaigns.js` and `campaigns.css`: the Campaigns door on the Declass home (only for
a preview tester: `?campaigns=preview` once in the browser, `?campaigns=off` to stop), the month and its
three chapters with release dates and locks, the chapter briefing, the deck builder (suggested deck, the
plain words check, greyed out cards stamped with the reason), and a run on the plotting table up to the
first raid: the opening hand and mulligan, the calm opening, card plays checked by the engine, Undo, and a
run that survives a reload. The raid itself is build session 4. With the same local server:

```
DB=<the local D1 sqlite file> PLAYWRIGHT=<path to playwright's index.mjs> node tests/campaigns/page.mjs
```

`SHOTS=<dir>` saves a phone sized screenshot of each step. First run, 6 Nov 2026: 27 passed, 0 failed.

Build session 4 (6 Nov 2026) added the battlefield: blocking in the raid with plotting plaques, the red
plaque for damage getting through, the forecast beside the button (the check makes sure the raid lands
exactly as forecast), the War Cabinet in the round menu, attacks in your turn with escorts first, the
Ultimatum's HELD OFF, debriefs when a wave breaks, and the end screen. The check then plays the whole run
out by tapping, and the server must replay and save it with the same result: 37 passed, 0 failed.

Build session 5, part 1 (7 Nov 2026): ranks on the chapter screens and end screen, and the month end
payout. Server checks add the month end (midnight Eastern on the 1st), the bands, paying once even with
three loads at once, the Intel log, and no payout without a run: 51 passed. The page check adds the rank
on the end screen and the month end results on the home screen: 39 passed.
