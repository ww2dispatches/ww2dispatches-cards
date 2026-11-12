// Release gating for the public pages that hold things before they post (Site Revamp doc):
// the Campaign Series volumes and day pages, and Name This. Times come from
// functions/_data/releases.json, written by renderer/site_pages.py.
//
// On any page served through these middlewares, an element with data-release (a UTC time)
// is removed until that time and an element with data-until is removed from that time on,
// so a page can carry a sealed row and a live row and the visitor sees the right one.
//
// Test date: on a preview address (*.pages.dev) ?asof=2026-12-01T07:00 (Denver time) or the
// asof cookie that site.js sets stands in for now. ww2dispatches.com ignores it.
import { zonedTime } from './time.js';

export function isPreview(url) {
  return /\.pages\.dev$/.test(url.hostname) || url.hostname === 'localhost' || url.hostname === '127.0.0.1';
}

export function nowFor(request) {
  const url = new URL(request.url);
  if (!isPreview(url)) return { now: Date.now(), test: '' };
  let asof = url.searchParams.get('asof');
  if (asof === null) {
    const m = (request.headers.get('Cookie') || '').match(/(?:^|;\s*)asof=([^;]*)/);
    asof = m ? decodeURIComponent(m[1]) : '';
  }
  const m = /^(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2})$/.exec(asof || '');
  if (!m) return { now: Date.now(), test: '' };
  return { now: zonedTime(m[1], m[2], 'America/Denver').getTime(), test: asof };
}

// Run the rewrite on an HTML response: drop the elements that should not show yet (or any more).
export function gateHtml(res, now) {
  const out = new HTMLRewriter()
    .on('[data-release]', {
      element(el) {
        if (Date.parse(el.getAttribute('data-release')) > now) el.remove();
        else el.removeAttribute('data-release');
      },
    })
    .on('[data-until]', {
      element(el) {
        if (Date.parse(el.getAttribute('data-until')) <= now) el.remove();
        else el.removeAttribute('data-until');
      },
    })
    .transform(res);
  return fresh(out);
}

// Every gated answer is worked out per request, so browsers must check back each time.
export function fresh(res, type) {
  const headers = new Headers(res.headers);
  headers.delete('ETag');
  headers.delete('Last-Modified');
  headers.set('Cache-Control', 'public, max-age=0, must-revalidate');
  if (type) headers.set('content-type', type);
  return new Response(res.body, { status: res.status, headers });
}

// Ask the static server for the whole file every time (the served answer changes even when the file doesn't).
export function fullRequest(request) {
  const req = new Request(request);
  req.headers.delete('If-None-Match');
  req.headers.delete('If-Modified-Since');
  return req;
}

export const isHtml = res => (res.headers.get('content-type') || '').includes('text/html');
