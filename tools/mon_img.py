"""Cuts the supplied monster artwork sheets (_monsterart/1..12.png) into game frames and writes js/art/monimg.js (PNG data URIs per enemy type).
Upgraded art for the existing enemies is fitted into the old sprite box (so hitboxes and anchors stay), new enemies get their own sizes. Run: python tools/mon_img.py"""
import base64, io, json, os
import numpy as np
from PIL import Image
from collections import deque

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', '_monsterart')
OLD = json.load(open(os.path.join(HERE, '..', '_boss_preview', 'foes_old.json')))

# (type, image, region x0,y0,x1,y1, frames, exclude rects, threshold, mode, extra)
# mode: 'ground' = feet on the bottom row, 'center' = body centred. extra: ref = frames that set the scale; fit = (w, h) content box for new enemies
U = 'up'
SPECS = [
    # --- upgraded art for the existing enemies (fitted to the old sprite box)
    ('crawler', 1, (24, 100, 806, 228), 4, [], 46, 'ground', {'old': 'crawler'}),
    ('moth', 1, (836, 100, 1354, 220), 4, [], 46, 'center', {'old': 'moth'}),
    ('pod', 1, (1384, 100, 1678, 228), 2, [], 46, 'ground', {'old': 'pod'}),
    ('frostling', 1, (24, 346, 614, 499), 3, [], 46, 'ground', {'old': 'frostling'}),
    ('wisp', 1, (648, 346, 1077, 496), 3, [], 46, 'center', {'old': 'wisp'}),
    ('turret', 1, (1111, 346, 1433, 512), 2, [], 46, 'ground', {'old': 'turret'}),
    ('icicle', 1, (1467, 346, 1730, 494), 1, [], 46, 'ground', {'old': 'icicle'}),
    ('hopper', 1, (24, 622, 610, 768), 3, [], 46, 'ground', {'old': 'hopper'}),
    ('ember', 1, (640, 622, 895, 786), 2, [], 46, 'ground', {'old': 'ember'}),
    ('magmite', 1, (926, 622, 1167, 754), 2, [], 46, 'ground', {'old': 'magmite'}),
    ('cinder', 1, (1197, 622, 1923, 762), 4, [], 46, 'ground', {'old': 'cinder'}),
    ('drone', 2, (24, 120, 821, 314), 4, [], 26, 'ground', {'old': 'drone', 'bg': (500, 290)}),
    ('jelly', 2, (853, 120, 1269, 363), 3, [], 46, 'center', {'old': 'jelly'}),
    ('rturret', 2, (1300, 120, 1585, 372), 2, [], 46, 'ground', {'old': 'rturret'}),
    ('guard', 2, (24, 541, 797, 727), 4, [], 46, 'ground', {'old': 'guard'}),
    ('hmoth', 2, (829, 541, 1276, 682), 4, [], 46, 'center', {'old': 'hmoth'}),
    ('hpod', 2, (1308, 541, 1581, 729), 2, [], 46, 'ground', {'old': 'hpod'}),
    ('egg', 2, (1612, 541, 1923, 751), 2, [], 46, 'ground', {'old': 'egg'}),
    # --- new enemies
    ('thorn', 3, (40, 470, 1410, 730), 4, [], 46, 'ground', {'fit': (38, 28)}),
    ('shardbat', 4, (50, 450, 1400, 795), 4, [], 46, 'center', {'fit': (30, 24)}),
    ('glacipede', 5, (30, 490, 1420, 735), 4, [], 46, 'ground', {'fit': (46, 26)}),
    ('mine', 6, (40, 435, 1410, 780), 4, [], 90, 'center', {'ref': [0, 1, 2], 'fit': (22, 22)}),
    ('leaper', 7, (40, 450, 1410, 760), 4, [], 46, 'ground', {'ref': [0, 3], 'fit': (34, 22)}),
    ('scarab', 8, (40, 495, 1420, 765), 4, [], 46, 'ground', {'fit': (38, 28)}),
    ('skimmer', 9, (30, 480, 1425, 750), 4, [], 46, 'center', {'fit': (46, 22)}),
    ('eel', 10, (30, 340, 1415, 795), 4, [(0, 0, 430, 410)], 80, 'ground', {'ref': [0], 'fit': (22, 18)}),
    ('stinger', 11, (30, 420, 1415, 785), 4, [(0, 0, 440, 450)], 46, 'center', {'fit': (30, 30)}),
    ('bloom', 12, (30, 395, 1415, 775), 4, [(0, 0, 340, 405)], 70, 'ground', {'ref': [0], 'fit': (22, 26)}),
]

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

def group(comps, n):
    comps = sorted(comps, key=lambda c: c['x0'])
    if n == 1: return [comps]
    gaps = []; run = comps[0]['x1']
    for i in range(1, len(comps)):
        gaps.append((comps[i]['x0'] - run, i)); run = max(run, comps[i]['x1'])
    cuts = sorted(i for _, i in sorted(gaps, reverse=True)[:n - 1]); out = []; prev = 0
    for c in cuts + [len(comps)]: out.append(comps[prev:c]); prev = c
    return out

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

_img = {}
def sheet(i):
    if i not in _img:
        a = np.asarray(Image.open(os.path.join(SRC, '%d.png' % i)).convert('RGB')).astype(int)
        bg = np.median(a[5:25, 5:25].reshape(-1, 3), axis=0); _img[i] = (a, bg)
    return _img[i]

def cut(spec):
    """-> list of (RGBA PIL image, (left, bottom) position in sheet coordinates)"""
    name, i, (x0, y0, x1, y1), n, excl, thr, mode, ex = spec
    a, bg = sheet(i)
    if 'bg' in ex: bx, by = ex['bg']; bg = np.median(a[by:by + 6, bx:bx + 6].reshape(-1, 3), axis=0)         # a sprite sitting on its panel's own (slightly lighter) background
    d = np.abs(a - bg).sum(2) > thr
    sub = np.zeros_like(d); sub[y0:y1, x0:x1] = d[y0:y1, x0:x1]
    for (ex0, ey0, ex1, ey1) in excl: sub[ey0:ey1, ex0:ex1] = False
    comps = [c for c in components(sub) if c['n'] >= 6 and not (c['y1'] - c['y0'] < 4 and c['x1'] - c['x0'] > 40) and not (c['x1'] - c['x0'] < 4 and c['y1'] - c['y0'] > 40)]
    big = max(c['n'] for c in comps); comps = [c for c in comps if c['n'] >= 0.01 * big]
    out = []
    groups = group(comps, n) if len(comps) >= n else None
    if groups is None or len(groups) < n:                                     # frames that touch: split the blob at the quietest columns
        allp = [p for c in comps for p in c['pts']]; cols = np.zeros(sub.shape[1] + 2, int)
        for (py, px) in allp: cols[px] += 1
        xmin, xmax = min(p[1] for p in allp), max(p[1] for p in allp); span = xmax - xmin; cuts = []
        for k in range(1, n):
            mid = xmin + span * k / n; lo, hi = int(mid - span * 0.1 / n * 2), int(mid + span * 0.1 / n * 2)
            cuts.append(min(range(lo, hi + 1), key=lambda x: cols[x]))
        groups = []; prev = xmin
        for cx in cuts + [xmax + 1]:
            sel = []
            for c in comps:
                pts = [(py, px) for (py, px) in c['pts'] if prev <= px < cx]
                if pts:
                    ys = [q[0] for q in pts]; xs = [q[1] for q in pts]; sel.append(dict(pts=pts, x0=min(xs), x1=max(xs), y0=min(ys), y1=max(ys), n=len(pts)))
            groups.append(sel); prev = cx
    for grp in groups:
        m = np.zeros(sub.shape, bool)
        for c in grp:
            for (py, px) in c['pts']: m[py, px] = True
        ys, xs = np.nonzero(m); bx0, bx1, by0, by1 = xs.min(), xs.max(), ys.min(), ys.max()
        g = m[by0:by1 + 1, bx0:bx1 + 1]; g2 = g.copy(); g2[1:, :] |= g[:-1, :]; g2[:-1, :] |= g[1:, :]; g2[:, 1:] |= g[:, :-1]; g2[:, :-1] |= g[:, 1:]
        hole = fill_holes(g2) & ~g2; lab = components(hole); keep = np.zeros_like(g2)
        for c in lab:
            if c['n'] <= 80:
                for (py, px) in c['pts']: keep[py, px] = True
        g2 |= keep
        rgb = a[by0:by1 + 1, bx0:bx1 + 1].astype(np.uint8)
        out.append((Image.fromarray(np.dstack([rgb, (g2 * 255).astype(np.uint8)]), 'RGBA'), (int(bx0), int(by1))))
    return out

def scale(img, s):
    w, h = max(1, round(img.width * s)), max(1, round(img.height * s))
    p = img.convert('RGBa').resize((w, h), Image.LANCZOS).convert('RGBA')
    a = np.asarray(p).copy(); a[..., 3] = np.where(a[..., 3] > 110, 255, 0)
    return Image.fromarray(a, 'RGBA')

def quant(img, n=64):
    a = np.asarray(img); alpha = a[..., 3] > 0
    rgb = Image.fromarray(a[..., :3], 'RGB').quantize(colors=n, method=Image.MEDIANCUT, dither=Image.NONE).convert('RGB')
    return Image.fromarray(np.dstack([np.asarray(rgb), (alpha * 255).astype(np.uint8)]), 'RGBA')

def png64(img):
    buf = io.BytesIO(); img.save(buf, 'PNG', optimize=True)
    return 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()

def old_box(name):
    """union bounding box of the old sprite's frames and the old frame size"""
    fr = OLD[name]; W, H = fr[0]['w'], fr[0]['h']; x0 = y0 = 10 ** 6; x1 = y1 = -1
    for f in fr:
        a = np.frombuffer(base64.b64decode(f['rgba']), np.uint8).reshape(f['h'], f['w'], 4)[..., 3] > 0
        ys, xs = np.nonzero(a); x0 = min(x0, xs.min()); x1 = max(x1, xs.max()); y0 = min(y0, ys.min()); y1 = max(y1, ys.max())
    return W, H, (int(x0), int(y0), int(x1), int(y1))

def build():
    out = {}
    for spec in SPECS:
        name, i, region, n, excl, thr, mode, ex = spec
        frs = cut(spec); assert len(frs) == n, (name, len(frs), n)
        ref = ex.get('ref', list(range(n)))
        # uniform scale from the reference frames
        rw = max(frs[k][0].width for k in ref); rh = max(frs[k][0].height for k in ref)
        if 'old' in ex:
            W, H, (ox0, oy0, ox1, oy1) = old_box(ex['old']); fw, fh = ox1 - ox0 + 1, oy1 - oy0 + 1
        else:
            fw, fh = ex['fit']
        s = min(fw / rw, fh / rh)
        sc = [scale(im, s) for im, _ in frs]
        base = max(pos[1] for _, pos in frs)                                   # common baseline in the sheet (the lowest bottom edge)
        tops = [(pos[1] - base) * s for _, pos in frs]                          # each frame's bottom relative to it (<= 0)
        cx = max(im.width for im in sc) // 2 + 1
        if mode == 'ground': Hc = int(max(im.height - t for im, t in zip(sc, tops))) + 1; yb = [Hc - 1 + t for t in tops]
        else: Hc = int(max(im.height for im in sc)) + 2; yb = [(Hc + im.height) / 2 for im in sc]                    # centred flyers keep their own heights
        Wc = cx * 2 + 1; ucx = cx
        if 'old' in ex:                                                         # keep the old box: same canvas, same anchor
            Wc, Hc = W, H
            ucx = (ox0 + ox1) / 2.0
            if mode == 'ground': yb = [oy1 + 1 + t for t in tops]
            else: yb = [(oy0 + oy1) / 2.0 + im.height / 2.0 for im in sc]
        frames = []
        for im, bot in zip(sc, yb):
            can = Image.new('RGBA', (Wc, Hc), (0, 0, 0, 0)); px = int(round((ucx if 'old' in ex else cx) - im.width / 2.0)); py = int(round(bot - im.height)); can.paste(im, (px, py), im)
            q = quant(can); frames.append({'u': png64(q), 'w': Wc, 'h': Hc})
        ent = {'frames': frames}
        if 'old' not in ex: ent['ax'] = cx; ent['ay'] = Hc - 1 if mode == 'ground' else Hc // 2
        out[name] = ent
        print(name, n, 'canvas', Wc, Hc, 'scale %.3f' % s)
    return out

if __name__ == '__main__':
    d = build()
    path = os.path.join(HERE, '..', 'js', 'art', 'monimg.js')
    src = "/* GENERATED by tools/mon_img.py from the supplied monster artwork: PNG data URIs per enemy type (upgrades fit the old sprite boxes; new enemies carry their anchor). */\n(function (G) {\n  G.art = G.art || {};\n  G.art.monimg = " + json.dumps(d, separators=(',', ':')) + ";\n})((window.SGS = window.SGS || {}));\n"
    open(path, 'w', encoding='utf-8').write(src); print('wrote', len(src))
