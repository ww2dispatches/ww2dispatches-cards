// Weekly Dispatch archive (/newsletter): keeps each issue hidden until it is sent,
// Sunday 7 a.m. Mountain. Release times come from renderer/newsletter_archive.py.
// An unreleased issue page sends the reader to the list, issues.json lists only
// released issues (the home page's Latest line), and on any page an element
// with a data-release time still in the future is removed before it is served.
import releases from '../_data/newsletter.json';

export async function onRequest(context) {
  const url = new URL(context.request.url);
  const now = Date.now();
  const m = url.pathname.match(/^\/newsletter\/(\d{3})(?:\.html)?\/?$/);
  if (m) {
    const at = releases[m[1]];
    if (!at || Date.parse(at) > now) return Response.redirect(new URL('/newsletter/', url).toString(), 302);
  }
  // Ask for the full file every time: the served page changes at release even when the file doesn't.
  const req = new Request(context.request);
  req.headers.delete('If-None-Match');
  req.headers.delete('If-Modified-Since');
  const res = await context.next(req);
  if (url.pathname === '/newsletter/issues.json' && res.ok) {
    const list = (await res.json()).filter((it) => Date.parse(it.release) <= now);
    return new Response(JSON.stringify(list), {
      headers: { 'content-type': 'application/json; charset=utf-8', 'Cache-Control': 'public, max-age=300' },
    });
  }
  if (!(res.headers.get('content-type') || '').includes('text/html')) return res;
  const out = new HTMLRewriter()
    .on('[data-release]', {
      element(el) {
        const at = Date.parse(el.getAttribute('data-release'));
        if (at > now) el.remove();
        else el.removeAttribute('data-release');
      },
    })
    .transform(res);
  const headers = new Headers(out.headers);
  headers.delete('ETag');
  headers.delete('Last-Modified');
  headers.set('Cache-Control', 'public, max-age=0, must-revalidate'); // a new issue shows at 7 a.m., not hours later
  return new Response(out.body, { status: out.status, headers });
}
