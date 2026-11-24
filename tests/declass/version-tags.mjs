// Version tag check (24 Nov 2026, Brian's ask). Every page under site/ loads its own scripts and styles as
// /path/file.js?v=<tag>. The tag is the first 8 characters of the file's sha1, the way renderer/site_pages.py
// (asset_v) makes it; older Declass tags used md5, which is accepted too. Browsers keep these files for a long
// time, so a tag that matches neither means returning players may keep an old file. On 23 Nov 2026 a tag looked
// stale only because two chats used different hashes, which is why both count. Run after every pull or merge:
//   node tests/declass/version-tags.mjs        (exits 1 and lists any stale tag)
//   node tests/declass/version-tags.mjs --fix  (rewrites stale tags in place, as sha1)
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const site = path.join(root, 'site');
const fix = process.argv.includes('--fix');

function pages(dir) {
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap(e => {
    const p = path.join(dir, e.name);
    return e.isDirectory() ? pages(p) : e.name.endsWith('.html') ? [p] : [];
  });
}
const hash = (f, alg) => crypto.createHash(alg).update(fs.readFileSync(f)).digest('hex').slice(0, 8);

let checked = 0, stale = [];
for (const page of pages(site)) {
  let html = fs.readFileSync(page, 'utf8'), changed = false;
  html = html.replace(/((?:src|href)="(\/[^"?]+\.(?:js|css)))\?v=([0-9a-f]+)/g, (all, head, url, tag) => {
    const file = path.join(site, url);
    if (!fs.existsSync(file)) return all;
    checked++;
    const want = hash(file, 'sha1');
    if (tag === want || tag === hash(file, 'md5')) return all;
    stale.push(`${path.relative(root, page)}: ${url}?v=${tag} should be ?v=${want}`);
    if (!fix) return all;
    changed = true;
    return `${head}?v=${want}`;
  });
  if (changed) fs.writeFileSync(page, html);
}
if (stale.length) {
  console.log(stale.join('\n'));
  console.log(fix ? `${stale.length} stale tag(s) fixed, ${checked} checked` : `${stale.length} stale tag(s) of ${checked}; run with --fix`);
  if (!fix) process.exit(1);
} else console.log(`version tags: all ${checked} match their files`);
