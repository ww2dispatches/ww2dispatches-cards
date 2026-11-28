"""Draw the Day by Day tab and strips for one day's Map Room clip with ov.html in headless Chrome.
Writes tab.png, stripA.png (the day's subtitle), stripB.png (the closing line), openov.png (tab and strip over the
opening still), openbg.png and opener.png (the still alone and with its overlay) into <out dir>.
Usage: ov_shoot.py <day.json> <out dir> [opening photo]   Env: MAPROOM_STAMP (e.g. TEST).
The tab and strip sit inside the template's safe area (tab_top, strip_lift)."""
import json, os, subprocess, sys, tempfile, urllib.parse
import numpy as np, cv2
HERE = os.path.dirname(os.path.abspath(__file__))
TPL = json.load(open(os.path.join(HERE, 'template.json')))
REC = json.load(open(sys.argv[1])); OV = sys.argv[2]; os.makedirs(OV, exist_ok=True)
DAY = dict(REC['mapRoom']); DAY['subtitle'] = REC['subtitle']; DAY.setdefault('tonight', 'The line tonight. It moves again tomorrow.')
NAME, N, OF = REC.get('seriesName', 'The Bulge'), REC.get('day', 1), REC.get('days', 30)
PHOTO = sys.argv[3] if len(sys.argv) > 3 else None
STAMP = os.environ.get('MAPROOM_STAMP', '')
CHROME = os.environ.get('CHROME', 'google-chrome')
POS = dict(ty=TPL['tab_top'], lift=TPL['strip_lift'])

def shoot(out, **q):
    if STAMP: q['stamp'] = STAMP
    q.update(POS)
    url = 'file://' + os.path.join(HERE, 'ov.html') + '?' + urllib.parse.urlencode(q)
    with tempfile.TemporaryDirectory() as prof:
        subprocess.run([CHROME, '--headless=new', '--no-sandbox', '--disable-gpu', '--hide-scrollbars', f'--user-data-dir={prof}',
                        '--allow-file-access-from-files', '--default-background-color=00000000', '--force-device-scale-factor=1',
                        '--window-size=1080,1920', '--virtual-time-budget=4000', f'--screenshot={out}', url],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    px = cv2.imread(out, cv2.IMREAD_UNCHANGED)[0, 0]              # ov.html paints the frame magenta when a strip won't fit
    if len(px) >= 3 and tuple(int(v) for v in px[:3]) == (255, 0, 255):
        os.remove(out); raise SystemExit(f'{out}: the strip text is wider than the frame at 40 px; shorten it: "{q.get("sub")}"')
    print('wrote', out)

tab = dict(cap='CAMPAIGN SERIES · THE MAP ROOM', name=NAME.upper(), day=f'DAY {N} OF {OF}')
shoot(os.path.join(OV, 'tab.png'), **tab)
shoot(os.path.join(OV, 'stripA.png'), tab='0', sub=DAY['subtitle'], bl=DAY['asOf'])
shoot(os.path.join(OV, 'stripB.png'), tab='0', sub=DAY['tonight'], bl=DAY['asOf'])
shoot(os.path.join(OV, 'openov.png'), sub=DAY['subtitle'], bl=DAY['asOf'], **tab)
if PHOTO:   # the day's archival photo, in grayscale like the Day by Day still
    g = os.path.join(OV, 'photo-gray.png'); cv2.imwrite(g, cv2.cvtColor(cv2.imread(PHOTO), cv2.COLOR_BGR2GRAY))
    shoot(os.path.join(OV, 'openbg.png'), tab='0', photo='file://' + os.path.abspath(g))
else:  # placeholder: plain dark ground until the day's real still exists
    cv2.imwrite(os.path.join(OV, 'openbg.png'), np.full((1920, 1080, 4), (27, 27, 27, 255), np.uint8))
bg = cv2.imread(os.path.join(OV, 'openbg.png'), cv2.IMREAD_UNCHANGED).astype(np.float32)
ov = cv2.imread(os.path.join(OV, 'openov.png'), cv2.IMREAD_UNCHANGED).astype(np.float32)
a = ov[..., 3:4] / 255; comp = bg.copy(); comp[..., :3] = bg[..., :3] * (1 - a) + ov[..., :3] * a; comp[..., 3] = 255
cv2.imwrite(os.path.join(OV, 'opener.png'), comp.astype(np.uint8)); print('wrote opener.png')
