-- Declass database, first version. Run once in the Cloudflare D1 console.
-- Times are stored as UTC ISO strings. Player ids are scrambled Google ids (HMAC with ID_SALT).

CREATE TABLE IF NOT EXISTS players (
  id                TEXT PRIMARY KEY,
  created_at        TEXT NOT NULL,
  streak            INTEGER NOT NULL DEFAULT 0,
  last_day_played   TEXT,
  priority_waiting  INTEGER NOT NULL DEFAULT 0,
  starter_done      INTEGER NOT NULL DEFAULT 0,
  tester            INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS pulls (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  player_id   TEXT NOT NULL REFERENCES players(id) ON DELETE CASCADE,
  card_id     TEXT NOT NULL,
  variant     TEXT NOT NULL CHECK (variant IN ('still','living')),
  finish      TEXT NOT NULL CHECK (finish IN ('copper','silver','gold','topsecret')),
  serial      INTEGER,
  slot_key    TEXT NOT NULL,
  pulled_at   TEXT NOT NULL,
  signature   TEXT NOT NULL,
  turned      INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS pulls_player ON pulls(player_id);
CREATE INDEX IF NOT EXISTS pulls_waiting ON pulls(player_id, turned);

CREATE TABLE IF NOT EXISTS opened (
  player_id  TEXT NOT NULL REFERENCES players(id) ON DELETE CASCADE,
  slot_key   TEXT NOT NULL,
  opened_at  TEXT NOT NULL,
  PRIMARY KEY (player_id, slot_key)
);

CREATE TABLE IF NOT EXISTS serials (
  card_id  TEXT NOT NULL,
  variant  TEXT NOT NULL,
  last     INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (card_id, variant)
);

CREATE TABLE IF NOT EXISTS months (
  player_id    TEXT NOT NULL REFERENCES players(id) ON DELETE CASCADE,
  month        TEXT NOT NULL,
  finished_at  TEXT NOT NULL,
  PRIMARY KEY (player_id, month)
);
