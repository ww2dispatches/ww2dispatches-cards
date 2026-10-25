// File numbers. Each signed pull gets one, printed on share pictures, so anyone can check that
// a card in a picture was really pulled. Format: the pull's number in Crockford base 32 (no I, L,
// O, or U, so nothing is misread), a dash, and four characters taken from the pull's signature.
// Without the signing key nobody can make a number that checks out.
import { unb64url } from './util.js';

const ALPHA = '0123456789ABCDEFGHJKMNPQRSTVWXYZ';

function b32(n, min = 3) {
  let s = '';
  do { s = ALPHA[n % 32] + s; n = Math.floor(n / 32); } while (n > 0);
  return s.padStart(min, '0');
}
function bytesB32(bytes, len) {
  let bits = 0, val = 0, out = '';
  for (const b of bytes) {
    val = (val << 8) | b; bits += 8;
    while (bits >= 5 && out.length < len) { out += ALPHA[(val >>> (bits - 5)) & 31]; bits -= 5; }
    if (out.length >= len) break;
    val &= (1 << bits) - 1;
  }
  return out;
}

export function fileNumber(row) {
  if (!row || !row.signature) return null;
  return b32(row.id) + '-' + bytesB32(unb64url(row.signature), 4);
}

// Split a typed file number into the pull number and its check, forgiving common misreadings.
export function parseFileNumber(text) {
  const clean = String(text || '').toUpperCase().replace(/[^0-9A-Z-]/g, '').replace(/O/g, '0').replace(/[IL]/g, '1');
  const m = clean.match(/^([0-9A-HJKMNP-TV-Z]{1,10})-?([0-9A-HJKMNP-TV-Z]{4})$/);
  if (!m) return null;
  let id = 0;
  for (const ch of m[1]) id = id * 32 + ALPHA.indexOf(ch);
  return { id, check: m[2] };
}

// A player's file number: eight characters from their scrambled id.
export function playerFileNumber(id) {
  try { return bytesB32(unb64url(id), 8); } catch { return String(id).slice(0, 8).toUpperCase(); }
}
