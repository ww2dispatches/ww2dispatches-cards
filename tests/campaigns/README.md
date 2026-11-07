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
