# Colorize NARA 208-AA-202B-4 (German photo, captured, U.S. National Archives) for the Bulge Flash card, 16 Dec 2026.
# Method A: region masks plus luminance color ramps, Kodachrome grade, then the ORIGINAL luminance is restored in Lab
# (only a gentle global S curve is applied to it), so no detail is added, removed or moved.
# Usage: python3 colorize-2026-12-16-the-bulge.py <original.jpg> <out_prefix> [warm|quiet]
import sys, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter

src, out, grade = sys.argv[1], sys.argv[2], (sys.argv[3] if len(sys.argv) > 3 else "warm")
im = Image.open(src).convert("L"); W, H = im.size          # 4284 x 5370
L = np.asarray(im).astype(np.float32) / 255
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)

def sm(a, b, x): t = np.clip((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t)
def blur(m, r): return np.asarray(Image.fromarray((np.clip(m, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r))).astype(np.float32) / 255
def poly(pts, r=18):
    m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).polygon(pts, fill=255)
    return np.asarray(m.filter(ImageFilter.GaussianBlur(r))).astype(np.float32) / 255
def ell(cx, cy, rx, ry, r=25):
    m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=255)
    return np.asarray(m.filter(ImageFilter.GaussianBlur(r))).astype(np.float32) / 255
def gf(m, r=24, eps=5e-4):
    # guided filter: snaps a rough mask to the photo's own edges (He et al.), so color stops where the object stops
    I = L; b = lambda x: cv2.boxFilter(x, -1, (2 * r + 1, 2 * r + 1))
    mI, mp = b(I), b(m); a = (b(I * m) - mI * mp) / (b(I * I) - mI * mI + eps); c = mp - a * mI
    return np.clip(b(a) * I + b(c), 0, 1)
def hx(h): return tuple(int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))
def ramp(st):
    o = np.zeros((H, W, 3), np.float32)
    for c in range(3): o[..., c] = np.interp(L, [s[0] for s in st], [hx(s[1])[c] for s in st])
    return o

# local smoothness tells flat sky from textured metal and cloth
Lb = blur(L, 3); var = blur((L - Lb) ** 2, 14) * 400; smooth = 1 - sm(0.02, 0.12, var)

# masks (original pixel coordinates). Every figure mask is a traced outline, and the edge snapped version
# is clamped to that outline, so no color can pass the drawn edge onto the halftrack.
MAN = [(1112, 1692), (1050, 1780), (1000, 1850), (960, 1900), (900, 1960), (862, 2000), (832, 2200), (802, 2400),
       (780, 2500), (752, 2545), (706, 2700), (684, 2800), (640, 2900), (616, 3000), (594, 3100), (554, 3170),
       (531, 3200), (530, 3300), (507, 3400), (482, 3500), (470, 3600), (455, 3700), (442, 3800), (433, 3900),
       (425, 4000), (417, 4100), (409, 4200), (400, 4300), (404, 4400), (424, 4480),
       (1700, 4470), (1702, 3655), (1747, 3625), (1746, 3480), (1718, 3380), (1702, 3300), (1702, 2900), (1727, 2800),
       (1744, 2760), (1740, 2580), (1717, 2500), (1702, 2450), (1702, 2088), (1780, 1985), (1850, 1925), (2060, 1870),
       (2200, 1805), (2410, 1712), (2606, 1665), (2690, 1560), (2745, 1490), (2750, 1430), (2620, 1378), (2480, 1428),
       (2400, 1485), (2130, 1625), (1710, 1745), (1650, 1720), (1668, 1650), (1648, 1560), (1613, 1470), (1588, 1380),
       (1548, 1288), (1482, 1228), (1400, 1202), (1300, 1207), (1208, 1238), (1148, 1305), (1134, 1400), (1124, 1480),
       (1100, 1560), (1094, 1650)]
HELMET1 = [(1094, 1650), (1100, 1560), (1124, 1480), (1134, 1400), (1148, 1305), (1208, 1238), (1300, 1207), (1400, 1202), (1482, 1228),
           (1548, 1288), (1588, 1380), (1613, 1470), (1648, 1560), (1668, 1650), (1652, 1722), (1600, 1700), (1572, 1560),
           (1540, 1452), (1400, 1422), (1250, 1432), (1190, 1482), (1150, 1580), (1120, 1662)]
GLOVE = [(2125, 1628), (2400, 1485), (2480, 1428), (2620, 1378), (2750, 1430), (2745, 1490), (2690, 1560), (2606, 1665),
         (2410, 1712), (2200, 1805), (2128, 1836)]
SOLD = [(3359, 2497), (3375, 2350), (3395, 2227), (3436, 2162), (3517, 2115), (3620, 2091), (3702, 2091), (3776, 2116),
        (3838, 2173), (3878, 2233), (3922, 2281), (3907, 2400), (3880, 2452), (3862, 2495), (3862, 2545), (3842, 2612),
        (3850, 2690), (3900, 2645), (4010, 2620), (4284, 2700), (4284, 4300), (3600, 4800), (2700, 5000), (2450, 4300),
        (2560, 3650), (2700, 3150), (3100, 2850), (3200, 2850), (3270, 2780), (3345, 2700), (3350, 2560)]
HELMET2 = [(3359, 2497), (3375, 2350), (3395, 2227), (3436, 2162), (3517, 2115), (3620, 2091), (3702, 2091), (3776, 2116),
           (3838, 2173), (3878, 2233), (3922, 2281), (3907, 2400), (3880, 2452), (3848, 2400), (3842, 2296), (3650, 2296),
           (3560, 2400), (3470, 2460), (3385, 2502)]
FACE2 = [(3688, 2296), (3843, 2288), (3842, 2400), (3872, 2452), (3858, 2492), (3860, 2545), (3842, 2598), (3815, 2610),
         (3780, 2575), (3745, 2510), (3712, 2440), (3692, 2370)]
man0 = poly(MAN, 5)
man_face = ell(1430, 1600, 185, 185, 18)
man_hand0 = poly(GLOVE, 5)
helmet1_0 = poly(HELMET1, 5)
sold0 = poly(SOLD, 8)
sold_face0 = poly(FACE2, 7)
helmet2_0 = poly(HELMET2, 5)
man, sold = man0, sold0
sky = blur(sm(0.70, 0.88, L) * smooth * (1 - sm(1300, 1900, yy)), 18) * (1 - man) * (1 - sold)
ground = sm(4250, 4600, yy) * (1 - man) * (1 - sold) + sm(4300, 4500, yy) * sm(3600, 3900, xx) * (1 - sold_face0)
ground = np.clip(ground, 0, 1)
running = poly([(1700, 2700), (3100, 2700), (3000, 4200), (1750, 4300)], 40) * (1 - man) * (1 - sold)

clamp = lambda m0, r=24: np.minimum(gf(m0, r), m0)
man, sold, man_hand = clamp(man0), clamp(sold0), clamp(man_hand0, 20)
helmet1, helmet2 = clamp(helmet1_0), clamp(helmet2_0)
man_face, sold_face = np.minimum(gf(man_face, 20), man0), clamp(sold_face0, 20)
warm = grade == "warm"
# base: the halftrack. 1944 German vehicles: Dunkelgelb base with olive green and red brown patches.
# The darker mottles take the olive brown end of the ramp, the light ground the dark yellow.
veh = ramp([(0, "#120f0b"), (0.22, "#3a3324"), (0.42, "#6a5c3c" if warm else "#635a43"), (0.62, "#a28d5e" if warm else "#968a6a"),
            (0.82, "#cdbb8f" if warm else "#c2b597"), (1, "#f2ead7")])
out_rgb = veh
def mix(mask, col, k=1.0):
    global out_rgb
    m = np.clip(mask * k, 0, 1)[..., None]; out_rgb = out_rgb * (1 - m) + col * m
mix(running, ramp([(0, "#0e0d0b"), (0.4, "#3b352d"), (0.8, "#7d7465"), (1, "#d8d1c2")]), 0.75)    # tracks, wheels, mud
mix(sky, ramp([(0, "#5a6168"), (0.7, "#b9bfc4"), (0.9, "#e3e6e8"), (1, "#f6f7f7")]), 0.95)        # overcast December sky
mix(ground, ramp([(0, "#0f0d0a"), (0.35, "#3d3122"), (0.65, "#7a6446"), (1, "#cdbb98")]), 0.9)    # dead winter grass, mud
mix(man, ramp([(0, "#0e0f0d"), (0.3, "#363a32"), (0.6, "#6e7365"), (0.85, "#acb0a4"), (1, "#eceee8")]), 0.95)  # grey green rubberized Kradmantel
mix(sold, ramp([(0, "#0f0d0a"), (0.3, "#3a3426"), (0.55, "#6b6142"), (0.8, "#a29776"), (1, "#e6e0cc")]), 0.9)  # camouflage smock, muted brown green
mix(np.maximum(helmet1, helmet2), ramp([(0, "#0e0f0f"), (0.4, "#3f4542"), (0.75, "#858c86"), (1, "#dfe2de")]), 0.9)  # field grey helmets
skin = ramp([(0, "#24160f"), (0.35, "#6e4a38"), (0.6, "#ad8a70"), (0.8, "#d4b59c"), (1, "#f6e9de")])
mix(np.maximum(man_face, sold_face) * sm(0.08, 0.25, L), skin, 0.95)
mix(man_hand, ramp([(0, "#141310"), (0.5, "#5d5a4c"), (1, "#c8c3b0")]), 0.85)                    # wool glove

# Kodachrome grade: richer saturation, slight warm shift, faint grain
g = out_rgb.mean(2, keepdims=True)
sat = 1.22 if warm else 1.12
out_rgb = np.clip(g + (out_rgb - g) * sat, 0, 1) * np.array([1.03, 1.0, 0.96] if warm else [1.015, 1.0, 0.985], np.float32)
out_rgb = np.clip(out_rgb, 0, 1)

# restore the archival luminance (with a gentle S curve) in Lab: structure is the original photo
lab = cv2.cvtColor((out_rgb * 255).astype(np.uint8), cv2.COLOR_RGB2LAB).astype(np.float32)
Ls = np.clip((L - 0.5) * 1.08 + 0.5, 0, 1)
lab[..., 0] = Ls * 255
ab = lab[..., 1:].copy()
for c in range(2): ab[..., c] = cv2.GaussianBlur(ab[..., c], (0, 0), 2.0)   # smooth chroma only
lab[..., 1:] = ab
rgb = cv2.cvtColor(np.clip(lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2RGB).astype(np.float32) / 255
rgb = np.clip(rgb + np.random.default_rng(16).normal(0, 0.012, rgb.shape).astype(np.float32), 0, 1)
Image.fromarray((rgb * 255).astype(np.uint8)).save(out + ".jpg", quality=95, subsampling=0)

# fidelity check: colorized luminance against the original
from skimage.metrics import structural_similarity as ssim
Lc = cv2.cvtColor((rgb * 255).astype(np.uint8), cv2.COLOR_RGB2LAB)[..., 0].astype(np.float32) / 255
mad = float(np.abs(Lc - Ls).mean()); s1 = float(ssim(Lc, Ls, data_range=1.0)); s0 = float(ssim(Lc, L, data_range=1.0))
print(f"{out}: luminance MAD vs curved original {mad:.4f}, SSIM vs curved original {s1:.4f}, SSIM vs raw original {s0:.4f}")
