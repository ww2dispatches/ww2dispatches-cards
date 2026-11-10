// POST /api/hit: a page visit or a few game actions, added to the day's tallies (see _lib/tally.js).
// Body: { p: page, v: first visit today (1), nw: first visit ever (1), s: source on arrival, e: [action names] }
// Open to every visitor (no tester key): the home page and newsletter count too. Nothing that identifies anyone is kept.
import { json, fail } from '../_lib/util.js';
import { gameDay } from '../_lib/time.js';
import { bump, sourceName, deviceOf, isBot } from '../_lib/tally.js';

const PAGES = new Set(['home', 'declass', 'newsletter', 'issue', 'privacy', 'support', 'other']);
const EVENTS = new Set(['card', 'zoom', 'file', 'share', 'shared', 'guest_starter', 'save_screen', 'dossier', 'sets', 'intercept', 'tour_done', 'tour_skip', 'save_skip', 'save_google', 'save_done', 'save_fail', 'signin_fail']);

export async function onRequestPost({ request, env }) {
  const ua = request.headers.get('user-agent') || '';
  if (isBot(ua)) return json({ ok: true });
  let b;
  try { b = (await request.json()) || {}; } catch { return fail(400, 'bad request'); }
  const day = gameDay(new Date()), rows = [];
  if (b.p) {
    const p = PAGES.has(b.p) ? b.p : 'other';
    rows.push(['view', p, 1]);
    if (b.v) { rows.push(['visitor', p, 1]); }
    if (b.day1) { rows.push(['visitors', '', 1]); rows.push(['device', deviceOf(ua), 1]); }
    if (b.nw) rows.push(['new', '', 1]);
    if (b.s !== undefined) rows.push(['source', sourceName(b.s), 1]);
  }
  const ev = {};
  (Array.isArray(b.e) ? b.e.slice(0, 40) : []).forEach(e => { if (EVENTS.has(e)) ev[e] = (ev[e] || 0) + 1; });
  Object.entries(ev).forEach(([k, n]) => rows.push(['ev', k, n]));
  if (rows.length) await bump(env.DB, day, rows);
  return json({ ok: true });
}
