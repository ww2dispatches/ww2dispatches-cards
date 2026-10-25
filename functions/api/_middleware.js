// Runs before every /api request: the test gate and the same site check.
import { fail } from '../_lib/util.js';
import { testerKeyOk, sameOrigin } from '../_lib/gate.js';

const OPEN_PATHS = new Set(['/api/config']); // safe without the key

export async function onRequest(context) {
  const { request, env } = context;
  const path = new URL(request.url).pathname;
  if (!env.DB || !env.SIGNING_KEY || !env.ID_SALT || !env.GOOGLE_CLIENT_ID) return fail(503, 'not configured');
  if (request.method !== 'GET' && !sameOrigin(request)) return fail(403, 'bad origin');
  if (!OPEN_PATHS.has(path) && !testerKeyOk(env, request)) return fail(403, 'coming soon');
  try {
    return await context.next();
  } catch (err) {
    console.error('declass api error', path, err && err.stack || err);
    return fail(500, 'server error');
  }
}
