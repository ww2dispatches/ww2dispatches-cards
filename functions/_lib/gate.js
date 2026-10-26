// Private test gate. Until LAUNCHED is "1", sign in and every game request needs the tester key,
// sent by the page in the X-Declass-Key header (the page remembers it from ?key=...).
export function testerKeyOk(env, request) {
  if (env.LAUNCHED === '1') return true;
  const key = request.headers.get('x-declass-key') || '';
  return Boolean(env.TESTER_KEY) && key.length > 0 && key === env.TESTER_KEY;
}

// Same site check for anything that changes data: the browser must say it came from our own pages.
export function sameOrigin(request) {
  const origin = request.headers.get('origin');
  if (!origin) return false;
  try { return new URL(origin).host === new URL(request.url).host; } catch { return false; } // e.g. Origin: null
}
