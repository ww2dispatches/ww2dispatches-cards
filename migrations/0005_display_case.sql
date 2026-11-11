-- Display Case (11 Nov 2026). Created on first use by functions/_lib/displaycase.js; here for the record.
CREATE TABLE IF NOT EXISTS display_case (player TEXT PRIMARY KEY, call_a TEXT, call_b TEXT, slots TEXT NOT NULL DEFAULT '[]', updated_at TEXT NOT NULL);
