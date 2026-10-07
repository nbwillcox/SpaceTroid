"""Cuts the supplied hero artwork sheet (_boss_src/hero.png) into game frames and writes js/art/heroimg.js.
Frames face right; anchor (ax, ay) = feet centre (spin: body centre; ball: bottom centre); tip (tx, ty) = the cannon muzzle relative to the anchor. Run: python tools/hero_img.py"""
import base64, io, json, os, sys
import numpy as np
from PIL import Image
from collections import deque

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', '_boss_src', 'hero.png')

# (band y0, y1, frame names)
BANDS = [
    (49, 221, ['aim_90', 'aim_70', 'aim_45', 'aim_20', 'aim_0', 'aim_m20', 'aim_m45', 'aim_m75']),
    (303, 457, ['run0', 'run1', 'run2', 'run3', 'run4', 'run5', 'run6', 'run7']),
    (530, 726, ['jump', 'fall', 'skid', 'land', 'itemget', 'front']),
    (813, 932, ['crouch_0', 'crouch_up', 'crouch_45', 'crouch_down']),
    (1018, 1150, ['spin0', 'spin1', 'spin2', 'spin3', 'spin4', 'spin5', 'spin6', 'spin7']),
    (1232, 1383, ['ball0', 'ball1', 'ball2', 'ball3', 'suit_cobalt', 'suit_crimson', 'suit_teal']),
]
import math
HERO_H = 43.0
THETA = {'aim_90': 90, 'aim_70': 70, 'aim_45': 45, 'aim_20': 20, 'aim_0': 0, 'aim_m20': -20, 'aim_m45': -45, 'aim_m75': -75, 'jump': 60, 'fall': -10, 'skid': 180, 'land': 180, 'itemget': 90,
         'crouch_0': 0, 'crouch_up': 90, 'crouch_45': 45, 'crouch_down': -30}          # aim_0 head-to-feet height in game pixels

def components(mask, y0, y1):
    h, w = mask.shape; seen = np.zeros_like(mask, bool); comps = []
    for y in range(y0, y1 + 1):
        for x in np.nonzero(mask[y] & ~seen[y])[0]:
            if seen[y, x]: continue
            q = deque([(y, x)]); seen[y, x] = True; pts = []
            while q:
                cy, cx = q.popleft(); pts.append((cy, cx))
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        ny, nx = cy + dy, cx + dx
                        if y0 <= ny <= y1 and 0 <= nx < w and mask[ny, nx] and not seen[ny, nx]:
                            seen[ny, nx] = True; q.append((ny, nx))
            ys = [p[0] for p in pts]; xs = [p[1] for p in pts]
            comps.append(dict(pts=pts, x0=min(xs), x1=max(xs), y0=min(ys), y1=max(ys), n=len(pts)))
    return comps

def group(comps, n):
    comps = sorted([c for c in comps if c['n'] >= 6], key=lambda c: c['x0'])
    gaps = []; runmax = comps[0]['x1']
    for i in range(1, len(comps)):
        gaps.append((comps[i]['x0'] - runmax, i)); runmax = max(runmax, comps[i]['x1'])
    cuts = sorted(i for _, i in sorted(gaps, reverse=True)[:n - 1])
    groups = []; prev = 0
    for c in cuts + [len(comps)]:
        groups.append(comps[prev:c]); prev = c
    return groups

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

def build():
    im = Image.open(SRC).convert('RGB'); a = np.asarray(im).astype(int)
    bg = np.median(a[:8, :].reshape(-1, 3), axis=0); mask = np.abs(a - bg).sum(2) > 34
    frames = {}
    raw = {}
    for (y0, y1, names) in BANDS:
        comps = components(mask, y0, y1)
        for name, grp in zip(names, group(comps, len(names))):
            big = max(c['n'] for c in grp); body = [c for c in grp if c['n'] >= 0.04 * big]
            x0 = min(c['x0'] for c in body); x1 = max(c['x1'] for c in body); yy0 = min(c['y0'] for c in body); yy1 = max(c['y1'] for c in body)
            bx0 = min(c['x0'] for c in body); bx1 = max(c['x1'] for c in body); by0 = min(c['y0'] for c in body); by1 = max(c['y1'] for c in body)
            m = np.zeros(mask.shape, bool)
            for c in body:
                for (py, px) in c['pts']: m[py, px] = True
            sub = m[yy0:yy1 + 1, x0:x1 + 1].copy()
            dd = np.abs(a[yy0:yy1 + 1, x0:x1 + 1] - bg).sum(2)
            while sub.shape[0] > 8 and not (sub[-1] & (dd[-1] > 110)).any():      # strip the dim ground-shadow rows under the feet
                sub = sub[:-1]; dd = dd[:-1]; yy1 -= 1; by1 = min(by1, yy1)
            if name.startswith('ball'): sub = sub[:min(sub.shape[0], sub.shape[1] + 1)]; yy1 = yy0 + sub.shape[0] - 1; by1 = min(by1, yy1)
            g = sub.copy(); g[1:, :] |= sub[:-1, :]; g[:-1, :] |= sub[1:, :]; g[:, 1:] |= sub[:, :-1]; g[:, :-1] |= sub[:, 1:]
            # fill holes: anything not reachable from the border without crossing the figure is inside it
            hh, ww = g.shape; outside = np.zeros_like(g); q = deque()
            for xx in range(ww):
                for yy in (0, hh - 1):
                    if not g[yy, xx] and not outside[yy, xx]: outside[yy, xx] = True; q.append((yy, xx))
            for yy in range(hh):
                for xx in (0, ww - 1):
                    if not g[yy, xx] and not outside[yy, xx]: outside[yy, xx] = True; q.append((yy, xx))
            while q:
                cy, cx = q.popleft()
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < hh and 0 <= nx < ww and not g[ny, nx] and not outside[ny, nx]: outside[ny, nx] = True; q.append((ny, nx))
            g = ~outside
            rgb = a[yy0:yy1 + 1, x0:x1 + 1].astype(np.uint8)
            img = Image.fromarray(np.dstack([rgb, (g * 255).astype(np.uint8)]), 'RGBA')
            raw[name] = (img, (bx0 - x0, by0 - yy0, bx1 - x0, by1 - yy0), (x0, yy0))
    # common scale from the forward-aiming standing frame
    ref = raw['aim_0'][1]; s = HERO_H / (ref[3] - ref[1] + 1)
    sb = 16.0 / (raw['ball0'][1][2] - raw['ball0'][1][0] + 1)
    for name, (img, main, _) in raw.items():
        if name.startswith('suit_'): continue
        sc = sb if name.startswith('ball') else s
        im2 = quant(scale(img, sc)); mx0, my0, mx1, my1 = [v * sc for v in main]
        arr = np.asarray(im2); al = arr[..., 3] > 0
        if name.startswith('spin'):
            ax, ay = (mx0 + mx1) / 2.0, (my0 + my1) / 2.0
        elif name.startswith('ball'):
            ax, ay = im2.width / 2.0, im2.height
        else:
            ay = my1 + 1
            rows = np.nonzero(al[int(max(0, my1 - (my1 - my0) * 0.12)):int(my1) + 1].any(axis=0))[0] if False else None
            bh = my1 - my0 + 1
            band = al[int(max(0, my1 - 0.52 * bh)):int(my1 - 0.36 * bh) + 1]; cols = np.nonzero(band.any(axis=0))[0]     # pelvis band: a stable horizontal anchor whatever the legs and arms do
            ax = float(cols.mean()) if len(cols) else (mx0 + mx1) / 2.0
        tip = None
        if not name.startswith(('spin', 'ball')):
            th = THETA.get(name, 0.0); dx_, dy_ = math.cos(math.radians(th)), -math.sin(math.radians(th))
            bh = my1 - my0 + 1; sh = (ax - 2, ay - 0.62 * bh)
            ys, xs = np.nonzero(al)
            keep = ys < ay - 0.28 * bh
            if keep.any():
                ys, xs = ys[keep], xs[keep]; k = int(((xs - sh[0]) * dx_ + (ys - sh[1]) * dy_).argmax()); tip = (float(xs[k]) - ax, float(ys[k]) - ay)
        fr = {'u': png64(im2), 'w': im2.width, 'h': im2.height, 'ax': round(ax), 'ay': round(ay)}
        if tip: fr['tx'] = round(tip[0]); fr['ty'] = round(tip[1])
        frames[name] = fr
    return frames

if __name__ == '__main__':
    fr = build()
    path = os.path.join(HERE, '..', 'js', 'art', 'heroimg.js')
    src = "/* GENERATED by tools/hero_img.py from the supplied hero artwork: PNG data URIs with anchors (feet centre) and cannon-tip offsets. */\n(function (G) {\n  G.art = G.art || {};\n  G.art.heroimg = " + json.dumps(fr, separators=(',', ':')) + ";\n})((window.SGS = window.SGS || {}));\n"
    open(path, 'w', encoding='utf-8').write(src)
    print('wrote', len(src))
    for k, v in fr.items(): print(k, v['w'], v['h'], 'anchor', v['ax'], v['ay'], 'tip', v.get('tx'), v.get('ty'))
