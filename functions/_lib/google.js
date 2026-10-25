// Checks a Google ID token (from Google Identity Services) against Google's public keys.
// Returns the Google account number ("sub") or throws.
import { unb64url } from './util.js';

const CERTS = 'https://www.googleapis.com/oauth2/v3/certs';
const ISSUERS = ['accounts.google.com', 'https://accounts.google.com'];

async function googleKeys() {
  const res = await fetch(CERTS, { cf: { cacheTtl: 3600, cacheEverything: true } });
  if (!res.ok) throw new Error('google keys unavailable');
  return (await res.json()).keys;
}

export async function verifyGoogleToken(token, clientId) {
  const parts = String(token || '').split('.');
  if (parts.length !== 3) throw new Error('bad token');
  const dec = s => JSON.parse(new TextDecoder().decode(unb64url(s)));
  const header = dec(parts[0]);
  const claims = dec(parts[1]);
  if (header.alg !== 'RS256') throw new Error('bad alg');

  const jwk = (await googleKeys()).find(k => k.kid === header.kid);
  if (!jwk) throw new Error('unknown key');
  const key = await crypto.subtle.importKey('jwk', jwk, { name: 'RSASSA-PKCS1-v1_5', hash: 'SHA-256' }, false, ['verify']);
  const ok = await crypto.subtle.verify('RSASSA-PKCS1-v1_5', key, unb64url(parts[2]), new TextEncoder().encode(parts[0] + '.' + parts[1]));
  if (!ok) throw new Error('bad signature');

  const now = Date.now() / 1000;
  if (!ISSUERS.includes(claims.iss)) throw new Error('bad issuer');
  if (claims.aud !== clientId) throw new Error('bad audience');
  if (!claims.exp || claims.exp < now - 60) throw new Error('expired');
  if (!claims.sub) throw new Error('no subject');
  return claims.sub; // nothing else (name, email, picture) is kept
}
