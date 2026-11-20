"""Draw the Day by Day tab and strips for a Map Room clip with ov.html in headless Chrome.
Writes tab.png, stripA.png (day subtitle), stripB.png (closing line), openov.png (tab and strip over the opening still),
openbg.png and opener.png (the still alone and with its overlay) into <work>/ov.
Usage: ov_shoot.py <series name> <day> <of> [opening photo]   Env: MAPROOM_WORK, MAPROOM_DAY, MAPROOM_STAMP (e.g. TEST)."""
import json, os, subprocess, sys, tempfile, urllib.parse
import numpy as np, cv2
HERE = os.path.dirname(os.path.abspath(__file__))
D = os.environ.get('MAPROOM_WORK', '.'); OV = os.path.join(D, 'ov'); os.makedirs(OV, exist_ok=True)
DAY = json.load(open(os.environ.get('MAPROOM_DAY', os.path.join(D, 'day01.json'))))
NAME, N, OF = sys.argv[1], sys.argv[2], sys.argv[3]; PHOTO = sys.argv[4] if len(sys.argv) > 4 else None
STAMP = os.environ.get('MAPROOM_STAMP', '')
CHROME = os.environ.get('CHROME', 'google-chrome')

def shoot(out, **q):
    if STAMP: q['stamp'] = STAMP
    url = 'file://' + os.path.join(HERE, 'ov.html') + '?' + urllib.parse.urlencode(q)
    with tempfile.TemporaryDirectory() as prof:
        subprocess.run([CHROME, '--headless=new', '--no-sandbox', '--disable-gpu', '--hide-scrollbars', f'--user-data-dir={prof}',
                        '--allow-file-access-from-files', '--default-background-color=00000000', '--force-device-scale-factor=1',
                        '--window-size=1080,1920', '--virtual-time-budget=4000', f'--screenshot={out}', url],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print('wrote', out)

tab = dict(cap='CAMPAIGN SERIES · THE MAP ROOM', name=NAME.upper(), day=f'DAY {N} OF {OF}')
shoot(os.path.join(OV, 'tab.png'), **tab)
shoot(os.path.join(OV, 'stripA.png'), tab='0', sub=DAY['subtitle'], bl=DAY['asOf'])
shoot(os.path.join(OV, 'stripB.png'), tab='0', sub=DAY['tonight'], bl=DAY['asOf'])
shoot(os.path.join(OV, 'openov.png'), sub=DAY['subtitle'], bl=DAY['asOf'], **tab)
if PHOTO:
    shoot(os.path.join(OV, 'openbg.png'), tab='0', photo='file://' + os.path.abspath(PHOTO))
else:  # placeholder: plain dark ground until the day's real still exists
    cv2.imwrite(os.path.join(OV, 'openbg.png'), np.full((1920, 1080, 4), (27, 27, 27, 255), np.uint8))
bg = cv2.imread(os.path.join(OV, 'openbg.png'), cv2.IMREAD_UNCHANGED).astype(np.float32)
ov = cv2.imread(os.path.join(OV, 'openov.png'), cv2.IMREAD_UNCHANGED).astype(np.float32)
a = ov[..., 3:4] / 255; comp = bg.copy(); comp[..., :3] = bg[..., :3] * (1 - a) + ov[..., :3] * a; comp[..., 3] = 255
cv2.imwrite(os.path.join(OV, 'opener.png'), comp.astype(np.uint8)); print('wrote opener.png')
