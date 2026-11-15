// Daily dispatch pages (/dispatches/NNN-slug, 15 Nov 2026): a page shows only once its post time has passed.
// Release times come from functions/_data/releases.json ("dispatches"), written by renderer/dispatch_pages.py.
//  * /dispatches/ itself goes to the On this day archive
//  * a page before its time sends the reader to the archive
//  * /dispatches/045 (number only) or an old slug goes to the page's current address
//  * on every page, data-release and data-until elements are kept or dropped (the next dispatch, the video link)
import releases from '../_data/releases.json';
import { nowFor, gateHtml, fullRequest, isHtml } from '../_lib/release.js';

export async function onRequest(context) {
  const url = new URL(context.request.url);
  const { now } = nowFor(context.request);
  const all = releases.dispatches || {};
  if (/^\/dispatches\/?$/.test(url.pathname)) return Response.redirect(new URL('/on-this-day/', url).toString(), 301);
  const m = url.pathname.match(/^\/dispatches\/(\d{3})(?:-([a-z0-9-]+))?(?:\.html)?\/?$/);
  if (m) {
    const d = all[m[1]];
    if (!d || Date.parse(d.at) > now) return Response.redirect(new URL('/on-this-day/', url).toString(), 302);
    if (url.pathname !== `/dispatches/${d.slug}`) return Response.redirect(new URL(`/dispatches/${d.slug}${url.search}`, url).toString(), 301);
  }
  const res = await context.next(fullRequest(context.request));
  if (isHtml(res)) return gateHtml(res, now);
  return res;
}
