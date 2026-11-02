// Site and game tallies (2 Nov 2026), for the admin console's Growth tab. Only counts are stored: one row
// per day, metric, and key (for example 2026-11-02 / view / home / 41). No visitor ids, no cookies, no
// internet addresses. Created on first use, like the Intercept tables (also in migrations/0004_tally.sql).
export const TALLY_SCHEMA = [
  `CREATE TABLE IF NOT EXISTS tally (day TEXT NOT NULL, metric TEXT NOT NULL, k TEXT NOT NULL DEFAULT '', n INTEGER NOT NULL DEFAULT 0, PRIMARY KEY (day, metric, k))`,
];
let ready = null;
export function ensureTally(db) {
  if (!ready) ready = db.batch(TALLY_SCHEMA.map(s => db.prepare(s))).catch(err => { ready = null; throw err; });
  return ready;
}
// rows: [[metric, key, n]]
export async function bump(db, day, rows) {
  if (!rows.length) return;
  await ensureTally(db);
  await db.batch(rows.map(([m, k, n]) => db.prepare('INSERT INTO tally (day, metric, k, n) VALUES (?, ?, ?, ?) ON CONFLICT (day, metric, k) DO UPDATE SET n = n + excluded.n').bind(day, m, k, n || 1)));
}

// Where a visit came from, as a short name. The page sends what it saw (utm_source, ?ref=, or the referring site).
const HOSTS = [[/(^|\.)(x|twitter)\.com$|^t\.co$/, 'x'], [/instagram\.com$/, 'instagram'], [/threads\.(net|com)$/, 'threads'], [/tiktok\.com$/, 'tiktok'],
  [/youtube\.com$|youtu\.be$/, 'youtube'], [/facebook\.com$|^fb\.(me|com)$|messenger\.com$/, 'facebook'], [/reddit\.com$/, 'reddit'], [/substack\.com$/, 'newsletter'],
  [/(^|\.)google\./, 'google'], [/bing\.com$|duckduckgo\.com$|yahoo\.com$|ecosia\.org$|search\.brave\.com$/, 'search'], [/linktr\.ee$|beacons\.ai$|bio\.link$/, 'link in bio'],
  [/ko-fi\.com$/, 'ko-fi'], [/buffer\.com$|start\.page$/, 'link in bio'], [/mail\.|outlook\.|gmail/, 'email']];
const NAMES = new Set(['x', 'instagram', 'threads', 'tiktok', 'youtube', 'facebook', 'reddit', 'newsletter', 'google', 'search', 'link in bio', 'ko-fi', 'email', 'direct', 'other']);
export function sourceName(raw) {
  let s = String(raw || '').toLowerCase().trim().slice(0, 80);
  if (!s) return 'direct';
  if (s === 'twitter') s = 'x';
  if (s === 'ig') s = 'instagram';
  if (s === 'yt') s = 'youtube';
  if (s === 'substack') s = 'newsletter';
  if (NAMES.has(s)) return s;
  const host = s.replace(/^https?:\/\//, '').split(/[/?#]/)[0].replace(/^www\.|^m\.|^l\.|^lm\./, '');
  for (const [re, name] of HOSTS) if (re.test(host)) return name;
  return 'other';
}
export const deviceOf = ua => /iPad|Tablet/i.test(ua) ? 'tablet' : /Mobi|iPhone|Android/i.test(ua) ? 'phone' : 'computer';
export const isBot = ua => !ua || /bot|crawl|spider|slurp|preview|headless|lighthouse|facebookexternalhit|embedly|monitor/i.test(ua);
