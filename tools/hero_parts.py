"""The hero is built from parts: 8 painted torsos (one per aim angle, cut under the belt, with the barrel kept when it points down over the legs)
and a set of drawn leg poses (idle, walk / run cycles, skid, jump, fall, landing, crouch). The game puts any torso on any leg pose, so the head, arms and
cannon stay in one consistent place whatever the legs do. Used by tools/hero_img.py."""
import math
import numpy as np
from PIL import Image, ImageDraw
import hero_img as H

AIMS = ['90', '70', '45', '20', '0', 'm20', 'm45', 'm90']
GD = 20                                  # hip height above the ground when standing

def _belt(a, al):
    Hh, W = al.shape
    r, g, b = a[..., 0].astype(int), a[..., 1].astype(int), a[..., 2].astype(int)
    tan = al & (r > 150) & (g > 100) & (b < 150) & (r > b + 40)
    lo, hi = int(Hh * 0.35), int(Hh * 0.66); cnt = tan[lo:hi, int(W * 0.12):int(W * 0.7)].sum(axis=1)
    return lo + int(cnt.argmax()) if cnt.max() > 1 else int(Hh * 0.52)

def _gun(a, al):
    r, g, b = a[..., 0].astype(int), a[..., 1].astype(int), a[..., 2].astype(int)
    mn = np.minimum(np.minimum(r, g), b); mx = np.maximum(np.maximum(r, g), b)
    return al & (((mn >= 120) & (mx - mn <= 70)) | ((g > 190) & (b > 205) & (r < 190)))

def torso(img, name):
    """img = the standing aim frame at game scale (RGBA, quantised). Returns the torso image, the hip point inside it and the muzzle relative to the hip."""
    a = np.asarray(img); Hh, W = a.shape[:2]; al = a[..., 3] > 0
    belt = _belt(a, al); cut = belt + 2
    cols = np.nonzero(al[belt - 1:belt + 2].any(axis=0))[0]; hipx = float(cols.mean()) if len(cols) else W / 2.0
    keep = np.zeros_like(al); keep[:cut] = al[:cut]
    gm = _gun(a, al); gd = gm.copy(); gd[1:, :] |= gm[:-1, :]; gd[:-1, :] |= gm[1:, :]; gd[:, 1:] |= gm[:, :-1]; gd[:, :-1] |= gm[:, 1:]; gd &= al
    th = H.theta('aim_' + name); dx_, dy_ = math.cos(math.radians(th)), -math.sin(math.radians(th))
    cs = [c for c in H.components(gd & (np.arange(Hh)[:, None] < Hh)) if c['n'] >= 6]
    tip = None
    if cs:
        c = max(cs, key=lambda c: c['n'])
        for (py, px) in c['pts']:
            if py >= cut: keep[py, px] = True                                  # the barrel stays in the torso even where it hangs below the belt
        pts = np.array([(px, py) for (py, px) in c['pts'] if gm[py, px]], float)
        if len(pts) < 3: pts = np.array([(px, py) for (py, px) in c['pts']], float)
        mu = pts.mean(axis=0); u, sv, vt = np.linalg.svd(pts - mu, full_matrices=False); ax_ = vt[0]
        if ax_[0] * dx_ + ax_[1] * dy_ < 0: ax_ = -ax_
        k = int(((pts - mu) @ ax_).argmax()); tip = (float(pts[k][0]), float(pts[k][1]))
    ys, xs = np.nonzero(keep); x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    rgba = a.copy(); rgba[..., 3] = np.where(keep, 255, 0)
    out = Image.fromarray(rgba[y0:y1 + 1, x0:x1 + 1], 'RGBA')
    hx, hy = float(hipx - x0), float((belt + 1) - y0)
    return out, hx, hy, ((float(tip[0] - hipx), float(tip[1] - (belt + 1))) if tip else (0.0, 0.0))

def legs_img(near, far, G):
    W, Hh, hx, hy = 48, 36, 24, 4
    big = Image.new('RGBA', (W * H.SS, Hh * H.SS), (0, 0, 0, 0)); dr = ImageDraw.Draw(big)
    for spec, f in ((far, 0.62), (near, 1.0)):                                   # the far leg (darker) first
        if spec[0] == 'ph': H._leg(dr, (hx, hy), spec[1], G, f, amp=spec[2])
        else: H._leg(dr, (hx, hy), 0, G, f, foot=spec[1:])
    im = big.resize((W, Hh), Image.BOX); la = np.asarray(im).copy(); la[..., 3] = np.where(la[..., 3] > 120, 255, 0)
    al = la[..., 3] > 0; ys, xs = np.nonzero(al); x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    return Image.fromarray(la[y0:y1 + 1, x0:x1 + 1], 'RGBA'), float(hx - x0), float(hy - y0)

def leg_poses():
    P = {'idle': (('ft', 4.5, 0, 0), ('ft', -5.5, 0, 0), GD),
         'skid': (('ft', 11, 0, -0.15), ('ft', -2, 0, 0), 19),
         'rise': (('ft', 4, 0.5, 0), ('ft', -3, 9.5, 0.6), GD),
         'apex': (('ft', 4, 1.5, 0), ('ft', -4, 5.5, 0.3), GD),
         'fall': (('ft', 6, 0, -0.1), ('ft', -6, 2.5, 0.2), GD),
         'land1': (('ft', 7, 0, 0), ('ft', -7, 0, 0), 17),
         'land2': (('ft', 9, 0, 0), ('ft', -8, 0, 0), 14),
         'crouch': (('ft', 10, 0, 0), ('ft', -8, 0, 0), 10)}
    AMPS = (('a', 0.5), ('b', 0.65), ('c', 0.8), ('d', 0.9), ('e', 1.0))       # stride lengths by speed: five steps, so the legs never jump between sizes when you speed up or slow down
    for tag, amp in AMPS:                                                      # the cycles share their phase, so the speed can change mid-stride
        for i in range(8):
            bob = round(0.9 * (1 - math.cos(4 * math.pi * i / 8)) / 2)
            P['%s%d' % (tag, i)] = (('ph', (i / 8.0) % 1.0, amp), ('ph', ((i / 8.0) + 0.5) % 1.0, amp), GD - bob)
    idle = P['idle']                                                           # stopping: from wherever the stride stopped, glide the feet to the idle stance in three steps
    for i in range(8):
        bob = round(0.9 * (1 - math.cos(4 * math.pi * i / 8)) / 2); n0, f0 = H.foot_at((i / 8.0) % 1.0, 0.5), H.foot_at(((i / 8.0) + 0.5) % 1.0, 0.5)
        for k in (1, 2, 3):
            t = k / 4.0; lerp = lambda a, b: tuple(x + (y - x) * t for x, y in zip(a, b))
            P['s%d_%d' % (k, i)] = (('ft',) + lerp(n0, idle[0][1:]), ('ft',) + lerp(f0, idle[1][1:]), round((GD - bob) + (GD - (GD - bob)) * t))
    return P

def make(raw, s):
    out = {}
    for n in AIMS:
        t, hx, hy, tip = torso(H.quant(H.scale(raw['aim_' + n], s)), n)
        t = H.quant(t); out['tor_' + n] = {'u': H.png64(t), 'w': t.width, 'h': t.height, 'hx': round(hx, 1), 'hy': round(hy, 1), 'tx': round(tip[0], 1), 'ty': round(tip[1], 1)}
    for name, (near, far, G) in leg_poses().items():
        im, hx, hy = legs_img(near, far, G); im = H.quant(im)
        out['leg_' + name] = {'u': H.png64(im), 'w': im.width, 'h': im.height, 'hx': round(hx, 1), 'hy': round(hy, 1), 'g': G}
    return out
