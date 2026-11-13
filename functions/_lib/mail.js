// Sends the sign in code (13 Nov 2026). One small module so the mail service can be swapped.
// Uses Resend's HTTP API when RESEND_API_KEY is set (Cloudflare, Pages, Settings, Variables and Secrets).
// MAIL_FROM is the sender, e.g. "Declass <files@ww2dispatches.com>"; the domain must be verified at Resend.
// On test copies only (ALLOW_FAKE_NOW=1, never set on the live site) no mail is sent and the code is
// handed back to the test instead.
const DEFAULT_FROM = 'Declass <files@ww2dispatches.com>';

export const mailMode = env => env.RESEND_API_KEY ? 'resend' : env.ALLOW_FAKE_NOW === '1' ? 'test' : 'off';

export function codeMail(code) {
  const spaced = code.slice(0, 3) + ' ' + code.slice(3);
  const text = `Your Declass code is ${spaced}\n\nType it into the game to save your dossier. It works for 10 minutes.\n\nIf you didn't ask for this, you can ignore this email. Nothing happens without the code.\n\nDeclass is a WW2 Dispatches game.\nhttps://ww2dispatches.com/declass`;
  const html = `<div style="font-family:Georgia,'Times New Roman',serif;max-width:440px;margin:0 auto;padding:24px;color:#1a1612">
<p style="font-size:13px;letter-spacing:.12em;text-transform:uppercase;color:#a34f44;margin:0 0 6px">WW2 Dispatches</p>
<h1 style="font-size:22px;margin:0 0 18px">Your Declass code</h1>
<p style="font-size:38px;font-weight:700;letter-spacing:.14em;margin:0 0 18px;font-family:'Courier New',monospace">${spaced}</p>
<p style="font-size:16px;line-height:1.5;margin:0 0 14px">Type it into the game to save your dossier. It works for 10 minutes.</p>
<p style="font-size:14px;line-height:1.5;color:#5e5647;margin:0 0 14px">If you didn't ask for this, you can ignore this email. Nothing happens without the code.</p>
<p style="font-size:12px;color:#8a806c;margin:22px 0 0">Declass is a WW2 Dispatches game. <a href="https://ww2dispatches.com/declass" style="color:#8a806c">ww2dispatches.com/declass</a></p>
</div>`;
  return { subject: `${spaced} is your Declass code`, text, html };
}

// Returns {ok: true} when the mail service took it, {ok: true, test: code} on a test copy, {ok: false} otherwise.
export async function sendCode(env, to, code) {
  const mode = mailMode(env);
  if (mode === 'test') return { ok: true, test: code };
  if (mode !== 'resend') return { ok: false };
  const m = codeMail(code);
  try {
    const res = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: { authorization: 'Bearer ' + env.RESEND_API_KEY, 'content-type': 'application/json' },
      body: JSON.stringify({ from: env.MAIL_FROM || DEFAULT_FROM, to: [to], subject: m.subject, text: m.text, html: m.html }),
    });
    if (!res.ok) console.error('declass mail refused', res.status, (await res.text().catch(() => '')).slice(0, 200));
    return { ok: res.ok };
  } catch (err) {
    console.error('declass mail error', err && err.message);
    return { ok: false };
  }
}
