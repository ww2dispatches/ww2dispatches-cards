// GET /api/file?n=...: check a file number from a share picture. Says which card, finish, serial,
// and date it stands for if it is genuine. Nothing about the player is ever shown.
import { json, fail } from '../_lib/util.js';
import { now, findCard, summary } from '../_lib/catalog.js';
import { fileNumber, parseFileNumber } from '../_lib/fileno.js';

export async function onRequestGet({ request, env }) {
  const t = now(env, request);
  const n = parseFileNumber(new URL(request.url).searchParams.get('n'));
  if (!n) return fail(404, 'no such file');
  const row = await env.DB.prepare('SELECT * FROM pulls WHERE id = ?').bind(n.id).first();
  if (!row || !row.signature || fileNumber(row).split('-')[1] !== n.check) return fail(404, 'no such file');
  const card = findCard(row.card_id, t);
  if (!card) return fail(404, 'no such file');
  return json({
    file: fileNumber(row), card: summary(card, t), variant: row.variant, finish: row.finish,
    serial: row.serial ?? null, at: row.pulled_at,
  });
}
