// POST /api/hit: a page visit or a few game actions, added to the day's tallies (see _lib/tally.js).
// Body: { p: page, v: first visit today (1), nw: first visit ever (1), s: source on arrival, e: [action names],
//         d: which dispatch, series part or issue (dv: first view of it today), c: [clicks], pg: page the clicks were on }
// Open to every visitor (no tester key): the home page and newsletter count too. Nothing that identifies anyone is kept.
import { json, fail } from '../_lib/util.js';
import { gameDay } from '../_lib/time.js';
import { bump, sourceName, deviceOf, isBot, PAGES } from '../_lib/tally.js';

// Platform Console counts (18 Nov 2026), all still plain daily totals:
//   dview / dvisitor  one dispatch page, one Campaign Series part, or one newsletter issue
//   out               a click on a link that leaves the site, by where it goes
//   cta               a click on a button into Declass, the newsletter signup, or a Name This guess, by the page it was on
//   collect           a click on Collect this card, by card;  ntopen: a Name This file opened, by case
// Only shapes on these lists are kept, so nobody can fill the table with made up names.
const DETAIL = /^(dispatch\/\d{3}-[a-z0-9-]{1,60}|campaign\/[a-z0-9-]{1,50}(\/(day|part)-\d{2})?|issue\/[a-z0-9-]{1,60})$/;
const OUTS = new Set(['substack', 'instagram', 'threads', 'x', 'tiktok', 'youtube', 'facebook', 'ko-fi', 'other']);
const CTAS = new Set(['play', 'collect', 'subscribe', 'guess']);
const ID = /^[a-z0-9-]{1,70}$/;
const EVENTS = new Set(['card', 'zoom', 'file', 'share', 'shared', 'guest_starter', 'save_screen', 'dossier', 'sets', 'intercept', 'tour_done', 'tour_skip', 'save_skip', 'save_google', 'save_done', 'save_fail', 'signin_fail', 'case_open', 'case_edit', 'case_share', 'case_callsign', 'card_link', 'save_inapp', 'inapp_copy', 'inapp_open', 'pack_carried', 'inapp_arrive', 'inapp_auto', 'out_landed', 'inapp_stuck', 'email_ask', 'email_sent', 'email_wrong', 'email_done']);

export async function onRequestPost({ request, env }) {
  const ua = request.headers.get('user-agent') || '';
  if (isBot(ua)) return json({ ok: true });
  let b;
  try { b = (await request.json()) || {}; } catch { return fail(400, 'bad request'); }
  const day = gameDay(new Date()), rows = [];
  // A browser that has signed in as admin (or opened the console) sends only this: one excluded page view.
  if (b.admin) { await bump(env.DB, day, [['admin', 'views', 1]]); return json({ ok: true }); }
  if (b.p) {
    const p = PAGES.has(b.p) ? b.p : 'other';
    rows.push(['view', p, 1]);
    if (b.v) { rows.push(['visitor', p, 1]); }
    if (b.day1) { rows.push(['visitors', '', 1]); rows.push(['device', deviceOf(ua), 1]); }
    if (b.nw) rows.push(['new', '', 1]);
    if (b.s !== undefined) rows.push(['source', sourceName(b.s), 1]);
    if (typeof b.d === 'string' && DETAIL.test(b.d) && b.d.split('/')[0] === p) { rows.push(['dview', b.d, 1]); if (b.dv) rows.push(['dvisitor', b.d, 1]); }
  }
  if (Array.isArray(b.c)) {
    const pg = PAGES.has(b.pg) ? b.pg : 'other';
    b.c.slice(0, 6).forEach(s => {
      if (typeof s !== 'string') return;
      const i = s.indexOf(':'), kind = s.slice(0, i), v = s.slice(i + 1);
      if (kind === 'out' && OUTS.has(v)) rows.push(['out', v, 1]);
      else if (kind === 'cta' && CTAS.has(v)) rows.push(['cta', v + '@' + pg, 1]);
      else if ((kind === 'collect' || kind === 'ntopen') && ID.test(v)) rows.push([kind, v, 1]);
    });
  }
  const ev = {};
  (Array.isArray(b.e) ? b.e.slice(0, 40) : []).forEach(e => { if (EVENTS.has(e)) ev[e] = (ev[e] || 0) + 1; });
  Object.entries(ev).forEach(([k, n]) => rows.push(['ev', k, n]));
  if (rows.length) await bump(env.DB, day, rows);
  return json({ ok: true });
}
