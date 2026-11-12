// The Campaign Shelf (/campaign-series): a day shows only once its post time has passed
// (6:30 a.m. Mountain on its run date). Release times come from renderer/site_pages.py.
//  * a day page before its time sends the reader to the volume page
//  * a thumbnail before its time is not served
//  * the volume data (/campaign-series/<series>.json) lists unreleased days as sealed stubs
//  * on every page, data-release and data-until elements are kept or dropped (sealed and live rows)
import releases from '../_data/releases.json';
import { nowFor, gateHtml, fresh, fullRequest, isHtml } from '../_lib/release.js';

export async function onRequest(context) {
  const url = new URL(context.request.url);
  const { now } = nowFor(context.request);
  const series = releases.campaigns || {};
  let m = url.pathname.match(/^\/campaign-series\/([a-z0-9-]+)\/(?:day-(\d{2})(?:\.html)?\/?|thumbs\/day-(\d{2})\.\w+)$/);
  if (m && series[m[1]]) {
    const at = series[m[1]][m[2] || m[3]];
    if (at && Date.parse(at) > now) {
      if (m[2]) return Response.redirect(new URL(`/campaign-series/${m[1]}/`, url).toString(), 302);
      return new Response('Not yet', { status: 404 });
    }
  }
  const res = await context.next(fullRequest(context.request));
  m = url.pathname.match(/^\/campaign-series\/([a-z0-9-]+)\.json$/);
  if (m && res.ok) {
    const data = await res.json();
    data.days = (data.days || []).map(d => (Date.parse(d.release) > now ? { n: d.n, release: d.release, arrives: d.arrives, sealed: true } : d));
    return fresh(new Response(JSON.stringify(data), { headers: res.headers }), 'application/json; charset=utf-8');
  }
  if (isHtml(res)) return gateHtml(res, now);
  return res;
}
