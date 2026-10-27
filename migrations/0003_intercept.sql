-- Declass, third version (27 Oct 2026): Intercept, the daily puzzle. No console step is needed: the
-- server creates these tables itself the first time Intercept is used (functions/_lib/intercept.js,
-- ensureTables). Kept here for the record, one statement per line.
CREATE TABLE IF NOT EXISTS intercept (player_id TEXT NOT NULL, day TEXT NOT NULL, dealt_at TEXT NOT NULL, tok TEXT NOT NULL, grid TEXT NOT NULL, found TEXT NOT NULL DEFAULT '[]', tries TEXT NOT NULL DEFAULT '[]', mistakes INTEGER NOT NULL DEFAULT 0, status TEXT NOT NULL DEFAULT 'play', score INTEGER, intel INTEGER, fin TEXT, claimed TEXT, moves INTEGER NOT NULL DEFAULT 0, PRIMARY KEY (player_id, day));
CREATE INDEX IF NOT EXISTS intercept_day ON intercept(day);
CREATE TABLE IF NOT EXISTS intercept_seen (player_id TEXT NOT NULL, group_id TEXT NOT NULL, last_day TEXT NOT NULL, PRIMARY KEY (player_id, group_id));
