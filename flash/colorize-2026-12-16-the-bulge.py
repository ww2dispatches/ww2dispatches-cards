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

# masks (original pixel coordinates)
man = poly([(1130, 1300), (1250, 1230), (1550, 1230), (1680, 1400), (1700, 1660), (2150, 1630), (2520, 1450),
            (2700, 1460), (2660, 1620), (2250, 1850), (1780, 2080), (1720, 2700), (1720, 3500), (1760, 4450),
            (440, 4480), (520, 3600), (780, 2600), (860, 1950), (1050, 1750), (1120, 1600)], 10)
man_face = ell(1430, 1600, 185, 185, 18)
man_hand = ell(2570, 1530, 150, 125, 10)
helmet1 = ell(1390, 1360, 260, 165, 14)
sold = poly([(3400, 2120), (3900, 2100), (4284, 2550), (4284, 4300), (3600, 4800), (2700, 5000),
             (2450, 4300), (2560, 3650), (2700, 3150), (3100, 2850), (3420, 2700)], 10)
sold_face = ell(3720, 2530, 165, 165, 18)
helmet2 = ell(3640, 2280, 300, 200)
sky = blur(sm(0.70, 0.88, L) * smooth * (1 - sm(1300, 1900, yy)), 18) * (1 - man) * (1 - sold)
ground = sm(4250, 4600, yy) * (1 - man) * (1 - sold) + sm(4300, 4500, yy) * sm(3600, 3900, xx) * (1 - sold_face)
ground = np.clip(ground, 0, 1)
running = poly([(1700, 2700), (3100, 2700), (3000, 4200), (1750, 4300)], 40) * (1 - man) * (1 - sold)

man, sold, man_hand, helmet1, helmet2 = gf(man), gf(sold), gf(man_hand, 20), gf(helmet1, 24), gf(helmet2, 24)
man_face, sold_face = gf(man_face, 20), gf(sold_face, 20)
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
mix(np.maximum(man_face, sold_face) * sm(0.18, 0.35, L), skin, 0.95)
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
