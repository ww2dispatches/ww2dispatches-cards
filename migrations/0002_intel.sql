-- Declass, second version (25 Oct 2026): Intel, requests, and ranks. Run once in the Cloudflare D1
-- console, one line at a time, after 0001_init.sql. Safe to run before the new code is deployed:
-- it only adds columns with defaults and a new table.
ALTER TABLE players ADD COLUMN intel INTEGER NOT NULL DEFAULT 0;
ALTER TABLE players ADD COLUMN rank_seen INTEGER NOT NULL DEFAULT 0;
ALTER TABLE pulls ADD COLUMN intel INTEGER NOT NULL DEFAULT 0;
CREATE TABLE IF NOT EXISTS intel_log (id INTEGER PRIMARY KEY AUTOINCREMENT, player_id TEXT NOT NULL REFERENCES players(id) ON DELETE CASCADE, at TEXT NOT NULL, delta INTEGER NOT NULL, reason TEXT NOT NULL, slot_key TEXT, card_id TEXT, variant TEXT, finish TEXT);
CREATE INDEX IF NOT EXISTS intel_log_player ON intel_log(player_id, id);
