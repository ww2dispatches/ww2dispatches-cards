// The On this day archive (/on-this-day/, 15 Nov 2026): every row, calendar dot and Today block carries
// data-release or data-until, so the archive never lists a dispatch before its post time.
import { nowFor, gateHtml, fullRequest, isHtml } from '../_lib/release.js';

export async function onRequest(context) {
  const { now } = nowFor(context.request);
  const res = await context.next(fullRequest(context.request));
  if (isHtml(res)) return gateHtml(res, now);
  return res;
}
