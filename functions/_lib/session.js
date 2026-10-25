// Signed session cookie: "<payload>.<hmac>", payload = base64url JSON {p: player id, e: expiry seconds}.
import { b64url, unb64url, hmac, hmacVerify, cookie } from './util.js';

const NAME = 'declass_session';
const DAYS = 180;

export async function makeSessionCookie(env, playerId) {
  const payload = b64url(new TextEncoder().encode(JSON.stringify({ p: playerId, e: Math.floor(Date.now() / 1000) + DAYS * 86400 })));
  const value = `${payload}.${await hmac(env.SIGNING_KEY, 'session:' + payload)}`;
  return `${NAME}=${value}; Path=/; Max-Age=${DAYS * 86400}; HttpOnly; Secure; SameSite=Lax`;
}

export const clearSessionCookie = () => `${NAME}=; Path=/; Max-Age=0; HttpOnly; Secure; SameSite=Lax`;

export async function readSession(env, request) {
  const value = cookie(request, NAME);
  if (!value) return null;
  const [payload, sig] = value.split('.');
  if (!payload || !sig || !(await hmacVerify(env.SIGNING_KEY, 'session:' + payload, sig))) return null;
  try {
    const data = JSON.parse(new TextDecoder().decode(unb64url(payload)));
    if (!data.p || data.e < Date.now() / 1000) return null;
    return data.p;
  } catch { return null; }
}
