"""Cuts the supplied hero artwork sheet (_boss_src/hero3.png: run cycles at four aim angles, jump poses, standing aim, crouch, ball, spin) into game frames
and writes js/art/heroimg.js. Frames face right; anchor (ax, ay) = feet (x of the pelvis band, y of the lowest pixel; spin: body centre; ball: bottom centre);
tip (tx, ty) = the cannon muzzle relative to the anchor. Run: python tools/hero_img.py"""
import base64, io, json, math, os
import numpy as np
from PIL import Image, ImageDraw
from collections import deque

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', '_boss_src', 'hero3.png')
HERO_H = 43.0                      # standing forward-aim head-to-feet height in game pixels
CW, C2 = 132.25, 264.5             # cell widths (8 across / 4 across); the grid starts at x = 13
def row(names, y0, y1, x0=13.0, w=CW): return [(n, int(x0 + i * w) + 3, int(x0 + (i + 1) * w) - 2, y0, y1) for i, n in enumerate(names)]
CELLS = []
for pre, y0, y1 in (('run_f', 64, 181), ('run_u45', 234, 354), ('run_u90', 407, 543), ('run_d45', 597, 709)): CELLS += row([pre + str(i) for i in range(8)], y0, y1)
CELLS += row(['air_0', 'air_u45', 'air_u90', 'air_d45'], 792, 924, w=C2)
CELLS += row(['aim_90', 'aim_70', 'aim_45', 'aim_20', 'aim_0', 'aim_m20', 'aim_m45', 'aim_m90'], 992, 1132)
CELLS += row(['crouch_0', 'crouch_45', 'crouch_up', 'crouch_down'], 1195, 1270, w=C2)
CELLS += row(['ball0', 'ball1', 'ball2', 'ball3'], 1322, 1407, x0=14.0, w=98.5)
CELLS += row(['spin%d' % i for i in range(8)], 1322, 1407, x0=420.0, w=81.5)
def theta(n):
    if n.startswith(('spin', 'ball')): return None
    for k, v in (('u45', 45), ('u90', 90), ('d45', -45), ('_f', 0), ('m90', -90), ('m45', -45), ('m20', -20), ('_90', 90), ('_70', 70), ('_45', 45), ('_20', 20), ('_0', 0), ('crouch_up', 90), ('crouch_down', -45), ('crouch_45', 45)):
        if k in n: return v
    return 0

def components(mask):
    h, w = mask.shape; seen = np.zeros_like(mask, bool); comps = []
    for y in range(h):
        for x in np.nonzero(mask[y] & ~seen[y])[0]:
            if seen[y, x]: continue
            q = deque([(y, int(x))]); seen[y, x] = True; pts = []
            while q:
                cy, cx = q.popleft(); pts.append((cy, cx))
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not seen[ny, nx]: seen[ny, nx] = True; q.append((ny, nx))
            ys = [p[0] for p in pts]; xs = [p[1] for p in pts]
            comps.append(dict(pts=pts, x0=min(xs), x1=max(xs), y0=min(ys), y1=max(ys), n=len(pts)))
    return comps

def png64(img):
    buf = io.BytesIO(); img.save(buf, 'PNG', optimize=True)
    return 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()

def scale(img, s):
    w, h = max(1, round(img.width * s)), max(1, round(img.height * s))
    p = img.convert('RGBa').resize((w, h), Image.LANCZOS).convert('RGBA')
    a = np.asarray(p).copy(); a[..., 3] = np.where(a[..., 3] > 110, 255, 0)
    return Image.fromarray(a, 'RGBA')

def quant(img, n=64):
    a = np.asarray(img); alpha = a[..., 3] > 0
    rgb = Image.fromarray(a[..., :3], 'RGB').quantize(colors=n, method=Image.MEDIANCUT, dither=Image.NONE).convert('RGB')
    return Image.fromarray(np.dstack([np.asarray(rgb), (alpha * 255).astype(np.uint8)]), 'RGBA')

def fill_holes(g):
    hh, ww = g.shape; out = np.zeros_like(g); q = deque()
    for xx in range(ww):
        for yy in (0, hh - 1):
            if not g[yy, xx] and not out[yy, xx]: out[yy, xx] = True; q.append((yy, xx))
    for yy in range(hh):
        for xx in (0, ww - 1):
            if not g[yy, xx] and not out[yy, xx]: out[yy, xx] = True; q.append((yy, xx))
    while q:
        cy, cx = q.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = cy + dy, cx + dx
            if 0 <= ny < hh and 0 <= nx < ww and not g[ny, nx] and not out[ny, nx]: out[ny, nx] = True; q.append((ny, nx))
    return ~out

SS = 8                                                   # supersampling for the drawn legs
LEG = dict(out=(10, 14, 40), dark=(22, 40, 104), mid=(44, 86, 178), lite=(112, 164, 232), tan=(214, 156, 92))
def _shade(c, f): return tuple(int(v * f) for v in c)
def _seg(dr, p0, p1, w0, w1, col):
    (x0, y0), (x1, y1) = p0, p1; dx, dy = x1 - x0, y1 - y0; d = math.hypot(dx, dy) or 1.0; nx, ny = -dy / d, dx / d
    pts = [(x0 + nx * w0 / 2, y0 + ny * w0 / 2), (x1 + nx * w1 / 2, y1 + ny * w1 / 2), (x1 - nx * w1 / 2, y1 - ny * w1 / 2), (x0 - nx * w0 / 2, y0 - ny * w0 / 2)]
    dr.polygon([(x * SS, y * SS) for x, y in pts], fill=col)
    for (cx, cy, r) in ((x0, y0, w0 / 2), (x1, y1, w1 / 2)): dr.ellipse([(cx - r) * SS, (cy - r) * SS, (cx + r) * SS, (cy + r) * SS], fill=col)
def _band(dr, P, Q, t, w, col):
    x, y = P[0] + (Q[0] - P[0]) * t, P[1] + (Q[1] - P[1]) * t; dx, dy = Q[0] - P[0], Q[1] - P[1]; d = math.hypot(dx, dy) or 1.0; nx, ny = -dy / d * w / 2, dx / d * w / 2
    _seg(dr, (x - nx, y - ny), (x + nx, y + ny), 1.4, 1.4, col)
def _leg(dr, hip, p, G, f, L=11.2):
    """one leg of the run cycle: stance (foot slides back along the ground) then swing (foot lifts and carries forward)"""
    beta = 0.0
    if p < 0.5: fx = 9.0 - 19.0 * (p / 0.5); lift = 0.0
    else: u = (p - 0.5) / 0.5; beta = (1.1 * math.sin(math.pi * u) if u < 0.5 else -0.35 * math.sin(math.pi * u)); sm = u * u * (3 - 2 * u); fx = -10.0 + 19.0 * sm; lift = 8.0 * math.sin(math.pi * u) ** 0.8
    fy = G - 2.4 - lift; n0 = math.hypot(fx, fy); d = min(n0, 2 * L - 0.4); ux, uy = fx / n0, fy / n0
    h = math.sqrt(max(0.1, L * L - (d / 2) ** 2)); H = hip; K = (hip[0] + ux * d / 2 + uy * h, hip[1] + uy * d / 2 - ux * h); A = (hip[0] + ux * d, hip[1] + uy * d)
    o, m, l, dk, tan = [_shade(LEG[k], f) for k in ('out', 'mid', 'lite', 'dark', 'tan')]
    boot = [(A[0] - 3.4, A[1] - 2.2), (A[0] + 1.8, A[1] - 2.2), (A[0] + 5.6, A[1] + 0.6), (A[0] + 5.6, A[1] + 2.4), (A[0] - 3.4, A[1] + 2.4)]
    def rot(pts): c, sn = math.cos(beta), math.sin(beta); return [(A[0] + (x - A[0]) * c - (y - A[1]) * sn, A[1] + (x - A[0]) * sn + (y - A[1]) * c) for x, y in pts]
    boot = rot(boot)
    big = [(A[0] - 4.4, A[1] - 3.2), (A[0] + 2.2, A[1] - 3.2), (A[0] + 6.6, A[1] + 0.2), (A[0] + 6.6, A[1] + 3.4), (A[0] - 4.4, A[1] + 3.4)]; big = rot(big)
    for grow, col in ((1.7, o), (0.0, m)):
        _seg(dr, H, K, 6.0 + grow, 4.8 + grow, col); _seg(dr, K, A, 4.8 + grow, 3.8 + grow, col)
        dr.polygon([(x * SS, y * SS) for x, y in (big if grow else boot)], fill=col)
    sh = (0.9, 0.6); _seg(dr, (H[0] + sh[0], H[1] + sh[1]), (K[0] + sh[0], K[1] + sh[1]), 2.4, 2.0, dk); _seg(dr, (K[0] + sh[0], K[1] + sh[1]), (A[0] + sh[0], A[1] + sh[1] - 1), 2.0, 1.6, dk)
    dr.polygon([(x * SS, y * SS) for x, y in rot([(A[0] - 3.4, A[1] + 0.2), (A[0] + 5.6, A[1] + 0.8), (A[0] + 5.6, A[1] + 2.4), (A[0] - 3.4, A[1] + 2.4)])], fill=dk)
    _seg(dr, (H[0] - 1.2, H[1] + 0.5), (K[0] - 1.2, K[1] - 0.4), 1.5, 1.3, l); _seg(dr, (K[0] - 1.0, K[1] + 0.3), (A[0] - 1.0, A[1] - 1.5), 1.3, 1.2, l)
    _band(dr, H, K, 0.45, 6.0, tan); _band(dr, K, A, 0.72, 5.0, tan)
    dr.ellipse([(K[0] + 0.5 - 1.9) * SS, (K[1] - 0.3 - 1.9) * SS, (K[0] + 0.5 + 1.9) * SS, (K[1] - 0.3 + 1.9) * SS], fill=tan); dr.ellipse([(K[0] - 0.2) * SS, (K[1] - 1.4) * SS, (K[0] + 1.0) * SS, (K[1] - 0.4) * SS], fill=l)
    dr.polygon([(x * SS, y * SS) for x, y in rot([(A[0] + 1.0, A[1] - 0.4), (A[0] + 3.4, A[1] - 0.4), (A[0] + 3.4, A[1] + 0.6), (A[0] + 1.0, A[1] + 0.6)])], fill=tan)

def run_legs(im2, i):
    """swap the painted legs of a run frame for drawn ones that really alternate: the painted torso stays (cut under the belt), two legs 180 degrees apart are drawn under it"""
    a = np.asarray(im2); H, W = a.shape[:2]; al = a[..., 3] > 0; old_ay = int(np.nonzero(al.any(axis=1))[0].max()) + 1
    r, g, b = a[..., 0].astype(int), a[..., 1].astype(int), a[..., 2].astype(int); tan = al & (r > 150) & (g > 100) & (b < 150) & (r > b + 40)
    lo, hi = int(H * 0.35), int(H * 0.66); cnt = tan[lo:hi, int(W * 0.12):int(W * 0.7)].sum(axis=1); belt = lo + int(cnt.argmax()) if cnt.max() > 1 else int(H * 0.52)
    cut = belt + 2; Gd = 20.5; oy = old_ay - (belt + 1 + int(Gd)); cols = np.nonzero(al[belt - 1:belt + 2].any(axis=0))[0]; ax = float(cols.mean()) if len(cols) else W / 2.0
    bob = (0, 1, 0, 1, 0, 1, 0, 1)[i] * 0 + round(0.9 * (1 - math.cos(4 * math.pi * i / 8)) / 2)
    can = Image.new('RGBA', (W, H + 4), (0, 0, 0, 0)); can.paste(im2.crop((0, 0, W, cut)), (0, oy + bob))
    big = Image.new('RGBA', (W * SS, (H + 4) * SS), (0, 0, 0, 0)); dr = ImageDraw.Draw(big)
    hip = (ax, oy + belt + 1 + bob); G = Gd - bob
    _leg(dr, hip, ((i / 8.0) + 0.5) % 1.0, G, 0.62)                                         # far leg (darker) first
    _leg(dr, hip, (i / 8.0) % 1.0, G, 1.0)                                                  # near leg
    legs = big.resize((W, H + 4), Image.BOX); la = np.asarray(legs).copy(); la[..., 3] = np.where(la[..., 3] > 120, 255, 0); legs = Image.fromarray(la, 'RGBA')
    can.alpha_composite(legs); can.alpha_composite(Image.new('RGBA', can.size, (0, 0, 0, 0)))
    # torso over the legs (the belt hides the hip joint)
    t = Image.new('RGBA', can.size, (0, 0, 0, 0)); t.paste(im2.crop((0, 0, W, cut)), (0, oy + bob)); can.alpha_composite(t)
    return can, ax

def build():
    im = Image.open(SRC).convert('RGB'); a = np.asarray(im).astype(int)
    bg = np.median(a[100:105, 0:6].reshape(-1, 3), axis=0); mask = np.abs(a - bg).sum(2) > 48
    raw = {}
    for name, x0, x1, y0, y1 in CELLS:
        sub = mask[y0:y1 + 1, x0:x1 + 1] if not name.startswith('ball') else (np.abs(a - bg).sum(2) > 130)[y0:y1 + 1, x0:x1 + 1]; comps = components(sub)
        comps = [c for c in comps if not (c['y1'] - c['y0'] < 4 and c['x1'] - c['x0'] > 12) and not (c['x1'] - c['x0'] < 4 and c['y1'] - c['y0'] > 12)]          # drop stray cell-border rules (horizontal and vertical)
        big = max(c['n'] for c in comps); body = [c for c in comps if c['n'] >= 0.03 * big]
        if not name.startswith(('spin', 'ball')):                                                       # the painted floor line under the feet: clear any long run in the bottom rows
            yb = max(c['y1'] for c in body); sub = sub.copy()
            for yy in range(max(0, yb - 14), yb + 1):
                best = cur = 0
                for v in sub[yy]: cur = cur + 1 if v else 0; best = max(best, cur)
                if best >= 45: sub[yy] = False
            comps = components(sub); big = max(c['n'] for c in comps); body = [c for c in comps if c['n'] >= 0.03 * big]
        bx0 = min(c['x0'] for c in body); bx1 = max(c['x1'] for c in body); by0 = min(c['y0'] for c in body); by1 = max(c['y1'] for c in body)
        m = np.zeros(sub.shape, bool)
        for c in body:
            for (py, px) in c['pts']: m[py, px] = True
        m = m[by0:by1 + 1, bx0:bx1 + 1]
        g = m.copy(); g[1:, :] |= m[:-1, :]; g[:-1, :] |= m[1:, :]; g[:, 1:] |= m[:, :-1]; g[:, :-1] |= m[:, 1:]
        hole = fill_holes(g) & ~g                                                                        # fill only small gaps (between arm and body); the space between the legs stays open
        lab = components(hole); keep = np.zeros_like(g)
        for c in lab:
            if c['n'] <= 40:
                for (py, px) in c['pts']: keep[py, px] = True
        g = g | keep
        rgb = a[y0 + by0:y0 + by1 + 1, x0 + bx0:x0 + bx1 + 1].astype(np.uint8)
        raw[name] = Image.fromarray(np.dstack([rgb, (g * 255).astype(np.uint8)]), 'RGBA')
    ref = raw['aim_0']; s = HERO_H / ref.height
    frames = {}
    for name, img in raw.items():
        sc = 16.0 / max(img.width, img.height) if name.startswith('ball') else s
        im2 = scale(img, sc); axo = None
        if name.startswith('run_'): im2, axo = run_legs(im2, int(name[-1]))
        im2 = quant(im2); arr = np.asarray(im2); al = arr[..., 3] > 0
        ys, xs = np.nonzero(al); my0, my1, mx0, mx1 = ys.min(), ys.max(), xs.min(), xs.max()
        if name.startswith('spin'): ax, ay = (mx0 + mx1) / 2.0, (my0 + my1) / 2.0
        elif name.startswith('ball'): ax, ay = im2.width / 2.0, im2.height
        else:
            ay = my1 + 1; bh = my1 - my0 + 1
            band = al[int(max(0, my1 - 0.52 * bh)):int(my1 - 0.36 * bh) + 1]; cols = np.nonzero(band.any(axis=0))[0]          # pelvis band: a stable horizontal anchor whatever the legs and arms do
            ax = float(cols.mean()) if len(cols) else (mx0 + mx1) / 2.0
            if axo is not None: ax = axo
        tip = None; th = theta(name)
        if th is not None:
            dx_, dy_ = math.cos(math.radians(th)), -math.sin(math.radians(th)); sh = (ax - 2, ay - 0.62 * bh)
            keep = ys < ay - (0.10 if th < -60 else 0.28) * bh
            rr, gg, bb = arr[..., 0].astype(int)[ys, xs], arr[..., 1].astype(int)[ys, xs], arr[..., 2].astype(int)[ys, xs]
            gun = ((np.minimum(np.minimum(rr, gg), bb) >= 120) & (np.maximum(np.maximum(rr, gg), bb) - np.minimum(np.minimum(rr, gg), bb) <= 70)) | ((gg > 190) & (bb > 205) & (rr < 190))   # the barrel is silver / white with a cyan muzzle: legs and armour are saturated blue or tan
            gm = np.zeros(al.shape, bool); gm[ys[keep & gun], xs[keep & gun]] = True
            gd = gm.copy(); gd[1:, :] |= gm[:-1, :]; gd[:-1, :] |= gm[1:, :]; gd[:, 1:] |= gm[:, :-1]; gd[:, :-1] |= gm[:, 1:]; gd &= al          # bridge the barrel's highlights
            cs = [c for c in components(gd) if c['n'] >= 6]
            if cs:
                c = max(cs, key=lambda c: c['n']); pts = np.array([(px, py) for (py, px) in c['pts'] if gm[py, px]], float)
                if len(pts) < 3: pts = np.array([(px, py) for (py, px) in c['pts']], float)
                mu = pts.mean(axis=0); u, sv, vt = np.linalg.svd(pts - mu, full_matrices=False); ax_ = vt[0]
                if ax_[0] * dx_ + ax_[1] * dy_ < 0: ax_ = -ax_
                k = int(((pts - mu) @ ax_).argmax()); tip = (float(pts[k][0]) - ax, float(pts[k][1]) - ay)
            elif keep.any():
                kx, ky = xs[keep], ys[keep]; k = int(((kx - sh[0]) * dx_ + (ky - sh[1]) * dy_).argmax()); tip = (float(kx[k]) - ax, float(ky[k]) - ay)
        fr = {'u': png64(im2), 'w': im2.width, 'h': im2.height, 'ax': round(ax), 'ay': round(ay)}
        if tip: fr['tx'] = round(tip[0]); fr['ty'] = round(tip[1])
        frames[name] = fr
    old = json.load(open(os.path.join(HERE, 'hero_old_frames.json')))
    frames['front'] = old['front']                                   # the sheet has no camera-facing pose: the save animation keeps the earlier one
    return frames

if __name__ == '__main__':
    fr = build()
    path = os.path.join(HERE, '..', 'js', 'art', 'heroimg.js')
    src = "/* GENERATED by tools/hero_img.py from the supplied hero artwork: PNG data URIs with anchors (feet) and cannon-tip offsets. */\n(function (G) {\n  G.art = G.art || {};\n  G.art.heroimg = " + json.dumps(fr, separators=(',', ':')) + ";\n})((window.SGS = window.SGS || {}));\n"
    open(path, 'w', encoding='utf-8').write(src)
    print('wrote', len(src))
    for k, v in fr.items(): print(k, v['w'], v['h'], 'anchor', v['ax'], v['ay'], 'tip', v.get('tx'), v.get('ty'))
