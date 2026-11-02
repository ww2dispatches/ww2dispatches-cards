-- Site and game tallies (2 Nov 2026). Created on first use by functions/_lib/tally.js; here for the record.
CREATE TABLE IF NOT EXISTS tally (day TEXT NOT NULL, metric TEXT NOT NULL, k TEXT NOT NULL DEFAULT '', n INTEGER NOT NULL DEFAULT 0, PRIMARY KEY (day, metric, k));
