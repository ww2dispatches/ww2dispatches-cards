// Public settings the page needs before sign in. The client ID is not a secret.
import { json, fail } from '../_lib/util.js';
import { testerKeyOk } from '../_lib/gate.js';

export async function onRequestGet({ request, env }) {
  return json({
    googleClientId: env.GOOGLE_CLIENT_ID,
    open: testerKeyOk(env, request), // false means show "Coming soon"
  });
}
