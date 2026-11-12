// Name This (/name-this): the open case never carries its answer (Site Revamp doc).
// /name-this/cases.json lists only puzzles whose post time (10 a.m. Mountain) has passed;
// the newest of those is the open case and loses its answer, answer card, and historical date.
// Every older one is a closed case in the Evidence Drawer. Data from renderer/site_pages.py.
import { nowFor, gateHtml, fresh, fullRequest, isHtml } from '../_lib/release.js';

export async function onRequest(context) {
  const url = new URL(context.request.url);
  const { now } = nowFor(context.request);
  const res = await context.next(fullRequest(context.request));
  if (url.pathname === '/name-this/cases.json' && res.ok) {
    const data = await res.json();
    const live = (data.cases || []).filter(c => Date.parse(c.release) <= now);
    live.sort((a, b) => Date.parse(b.release) - Date.parse(a.release)); // newest first
    if (live[0]) {
      const open = { ...live[0], open: true };
      delete open.a; delete open.aImg; delete open.hist;
      live[0] = open;
    }
    return fresh(new Response(JSON.stringify({ cases: live }), { headers: res.headers }), 'application/json; charset=utf-8');
  }
  if (isHtml(res)) return gateHtml(res, now);
  return res;
}
