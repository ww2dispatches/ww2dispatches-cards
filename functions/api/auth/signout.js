import { json } from '../../_lib/util.js';
import { clearSessionCookie } from '../../_lib/session.js';

export async function onRequestPost() {
  return json({ ok: true }, 200, { 'set-cookie': clearSessionCookie() });
}
