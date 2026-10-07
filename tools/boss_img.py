"""Cuts the supplied boss artwork sheets (tools/../_boss_src/<boss>.png) into game frames, scales them to boss size, keys out the background and writes js/art/bossimg.js
(base64 PNGs plus anchors). Run: python tools/boss_img.py"""
import base64, io, json, os, sys
import numpy as np
from PIL import Image, ImageEnhance, ImageOps
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from boss_seg import segment, GRID

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', '_boss_src')

def frame_rgba(im, lab, cell):
    """RGBA crop of one frame: the main body plus its nearby pieces (sparks, dust), everything else keyed out"""
    mx0, my0, mx1, my1 = cell['main']; pad = 80
    ids = cell['ids']
    x0, y0, x1, y1 = cell['full']
    # keep only pieces within `pad` of the main body so strays from neighbouring cells are dropped
    sel = np.isin(lab, list(ids))
    sub = sel[y0:y1 + 1, x0:x1 + 1]
    rgb = np.asarray(im)[y0:y1 + 1, x0:x1 + 1]
    # grow the mask by 1px so anti-aliased rims are kept
    m = sub.copy(); m[1:, :] |= sub[:-1, :]; m[:-1, :] |= sub[1:, :]; m[:, 1:] |= sub[:, :-1]; m[:, :-1] |= sub[:, 1:]
    out = np.dstack([rgb, (m * 255).astype(np.uint8)])
    return Image.fromarray(out, 'RGBA'), (mx0 - x0, my0 - y0, mx1 - x0, my1 - y0)

def scale(img, s):
    w, h = max(1, round(img.width * s)), max(1, round(img.height * s))
    p = img.convert('RGBa').resize((w, h), Image.LANCZOS).convert('RGBA')
    a = np.asarray(p).copy()
    a[..., 3] = np.where(a[..., 3] > 120, 255, 0)
    return Image.fromarray(a, 'RGBA')

def quant(img, n=56):
    a = np.asarray(img); alpha = a[..., 3] > 0
    rgb = Image.fromarray(a[..., :3], 'RGB').quantize(colors=n, method=Image.MEDIANCUT, dither=Image.NONE).convert('RGB')
    out = np.dstack([np.asarray(rgb), (alpha * 255).astype(np.uint8)])
    return Image.fromarray(out, 'RGBA')

def centroid(img, test):
    a = np.asarray(img).astype(int); r, g, b, al = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
    m = test(r, g, b) & (al > 0)
    ys, xs = np.nonzero(m)
    return (float(xs.mean()), float(ys.mean())) if len(xs) > 8 else None

def png64(img):
    buf = io.BytesIO(); img.save(buf, 'PNG', optimize=True)
    return 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()

def spec(img, ax, ay):
    return {'u': png64(img), 'w': img.width, 'h': img.height, 'ax': int(round(ax)), 'ay': int(round(ay))}

def tint(img, f=1.25, add=(0, 0, 0)):
    a = np.asarray(img).astype(float); a[..., :3] = np.clip(a[..., :3] * f + np.array(add), 0, 255)
    return Image.fromarray(a.astype(np.uint8), 'RGBA')

def build():
    out = {}
    seg = {}
    for nm in GRID:
        im, lab, cells = segment(nm, SRC)
        seg[nm] = {c['label']: frame_rgba(im, lab, c) for c in cells}
    # ---------------- beetle: scale so the walking body is 132 px wide; anchor = body centre x, feet y
    S = seg['beetle']; s = 132.0 / (S['walk'][1][2] - S['walk'][1][0] + 1)
    def bf(label, bob=0, post=None):
        img, main = S[label]; im2 = scale(img, s)
        if post: im2 = post(im2)
        im2 = quant(im2)
        mx0, my0, mx1, my1 = [v * s for v in main]
        return spec(im2, (mx0 + mx1) / 2.0, my1 + bob)
    walk = [bf('walk', b) for b in (0, -1, -2, -1)]
    # core: centre of the glowing hole on the stunned frame, measured from the body centre / feet
    st = scale(S['stun0'][0], s); c = centroid(st, lambda r, g, b: (b > 200) & (g > 170) & (r < 200))
    m = [v * s for v in S['stun0'][1]]; core = {'dx': round((m[0] + m[2]) / 2 - c[0]), 'dy': round(m[3] - c[1])} if c else {'dx': 30, 'dy': 52}
    out['beetle'] = {'walk': walk, 'rear': bf('roar'), 'tele': [bf('tele'), bf('tele', 0, lambda i: tint(i, 1.12, (22, 10, 0)))], 'charge': [bf('charge'), bf('charge', -1)],
                     'stun': [bf('stun0'), bf('stun1')], 'core': core}
    # ---------------- moth: body width 140, anchor on the chest gem (the game's weak point sits 6px below the anchor)
    S = seg['moth']; s = 140.0 / (S['fly'][1][2] - S['fly'][1][0] + 1)
    def mf(label, post=None, gem=True):
        img, main = S[label]; im2 = scale(img, s)
        if post: im2 = post(im2)
        g = centroid(im2, lambda r, g_, b: (b > 190) & (r < 150) & (g_ > 120) & (g_ < 235)) if gem else None
        mx0, my0, mx1, my1 = [v * s for v in main]
        ax, ay = (g[0], g[1] - 6) if g else ((mx0 + mx1) / 2.0, (my0 + my1) / 2.0)
        return spec(quant(im2), ax, ay)
    out['moth'] = {'fly': [mf('fly'), mf('down'), mf('fly'), mf('down')], 'shoot': [mf('shoot', None, False), mf('shoot', lambda i: tint(i, 1.15), False)], 'dive': mf('dive', None, False),
                   'stun': [mf('stun'), mf('stun', lambda i: tint(i, 1.2, (0, 12, 20)))], 'dead': mf('dead', None, False)}
    # ---------------- wyrm: head 76 px wide anchored at the cranium; neck 32 x 17; lava splash 44 wide
    S = seg['wyrm']; s = 76.0 / (S['head'][1][2] - S['head'][1][0] + 1)
    def wf(label, post=None):
        img, main = S[label]; im2 = scale(img, s)
        if post: im2 = post(im2)
        mx0, my0, mx1, my1 = [v * s for v in main]
        return spec(quant(im2), mx0 + (mx1 - mx0) * 0.44, (my0 + my1) / 2.0)
    img, main = S['neck']; sn = 32.0 / (main[2] - main[0] + 1); neck = quant(scale(img.crop((main[0], main[1], main[2] + 1, main[3] + 1)), sn))
    img, main = S['splash']; ss = 44.0 / (S['splash'][1][2] - S['splash'][1][0] + 1); sp = quant(scale(img, ss))
    out['wyrm'] = {'head': [wf('head'), wf('head_open')], 'neck': spec(neck, neck.width / 2.0, neck.height / 2.0),
                   'splash': [spec(sp, sp.width / 2.0, sp.height), spec(ImageOps.mirror(sp), sp.width / 2.0, sp.height), spec(tint(sp, 1.15), sp.width / 2.0, sp.height)]}
    # ---------------- jelly: bell 116 px wide, anchored on the big eye (the game's weak point sits 2px below the anchor)
    S = seg['jelly']; s = 116.0 / (S['bell'][1][2] - S['bell'][1][0] + 1)
    def jf(label):
        img, main = S[label]; im2 = scale(img, s)
        g = centroid(im2, lambda r, g_, b: (r > 190) & (g_ < 150) & (b > 110))
        mx0, my0, mx1, my1 = [v * s for v in main]
        return spec(quant(im2), g[0] if g else (mx0 + mx1) / 2.0, (g[1] if g else (my0 + my1) / 2.0) - 2)
    out['jelly'] = {'bell': [jf('bell'), jf('bell_open')]}
    # ---------------- heart: body 124 px wide anchored at the eye; nodes 34 px
    S = seg['heart']; s = 124.0 / (S['closed'][1][2] - S['closed'][1][0] + 1)
    ey = None
    def hf(label):
        nonlocal ey
        img, main = S[label]; im2 = scale(img, s)
        mx0, my0, mx1, my1 = [v * s for v in main]
        g = centroid(im2, lambda r, g_, b: (r > 200) & (g_ > 130) & (b < 90))
        if label == 'open' and g: ey = (g[1] - my0) / max(1.0, my1 - my0)
        return im2, (mx0, my0, mx1, my1)
    fr = {l: hf(l) for l in ('open', 'closed', 'wide')}
    body = []
    for l in ('closed', 'open', 'wide'):
        im2, (mx0, my0, mx1, my1) = fr[l]
        body.append(spec(quant(im2), (mx0 + mx1) / 2.0, my0 + (my1 - my0) * (ey if ey else 0.55)))
    img, main = S['node']; sn = 34.0 / (main[2] - main[0] + 1); nd = quant(scale(img, sn))
    mx0, my0, mx1, my1 = [v * sn for v in main]
    out['heart'] = {'heart': body, 'node': [spec(nd, (mx0 + mx1) / 2.0, (my0 + my1) / 2.0), spec(tint(nd, 1.6, (30, 30, 30)), (mx0 + mx1) / 2.0, (my0 + my1) / 2.0)]}
    return out

if __name__ == '__main__':
    d = build()
    path = os.path.join(HERE, '..', 'js', 'art', 'bossimg.js')
    src = "/* GENERATED by tools/boss_img.py from the supplied boss artwork: frames as PNG data URIs with anchors (ax, ay = the point that sits at the boss's position). */\n(function (G) {\n  G.art = G.art || {};\n  G.art.bossimg = " + json.dumps(d, separators=(',', ':')) + ";\n})((window.SGS = window.SGS || {}));\n"
    open(path, 'w', encoding='utf-8').write(src)
    print('wrote', len(src))
    for k, v in d.items():
        print(k, {kk: (vv['w'], vv['h'], vv['ax'], vv['ay']) if isinstance(vv, dict) and 'w' in vv else ([(x['w'], x['h'], x['ax'], x['ay']) for x in vv] if isinstance(vv, list) else vv) for kk, vv in v.items()})
