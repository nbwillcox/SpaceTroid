"""Shared pixel-art toolkit for the boss art: a letter canvas with lit blobs, plated skin, spikes, teeth, glowing cracks and eyes.
Letters follow the game's key sets: 'o','1'-'4' = the sprite's armor ramp (dark -> light); gold s k y Y w; visor q x v V W; energy d g e E h; metal z M m l L;
under b U u n N; moss A B C D F. '.' is transparent."""
import math, random

def hash2(x, y, seed=0):
    n = (x * 374761393 + y * 668265263 + seed * 2147483647) & 0xffffffff
    n = (n ^ (n >> 13)) * 1274126177 & 0xffffffff
    return ((n ^ (n >> 16)) & 0xffff) / 65535.0

class Cv:
    def __init__(s, w, h):
        s.w, s.h = w, h
        s.g = [['.'] * w for _ in range(h)]
    def put(s, x, y, c):
        x, y = int(round(x)), int(round(y))
        if 0 <= x < s.w and 0 <= y < s.h: s.g[y][x] = c
    def get(s, x, y): return s.g[y][x] if 0 <= x < s.w and 0 <= y < s.h else '.'
    def rect(s, x0, y0, x1, y1, c):
        for y in range(int(y0), int(y1) + 1):
            for x in range(int(x0), int(x1) + 1): s.put(x, y, c)
    def line(s, x0, y0, x1, y1, c, th=1):
        n = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(int(n) + 1):
            x = round(x0 + (x1 - x0) * i / n); y = round(y0 + (y1 - y0) * i / n)
            for dx in range(th):
                for dy in range(th): s.put(x + dx - th // 2, y + dy - th // 2, c)
    def rows(s): return [''.join(r) for r in s.g]
    def mask(s, inside):
        return [[bool(inside(x + 0.5, y + 0.5)) for x in range(s.w)] for y in range(s.h)]
    def shape(s, inside, ramp='1234', outline='o', bevel=True, light=None, cells=None):
        """paint a lit shape: ramp = 4 letters dark -> light. light(x, y) may return 0..1 brightness for smooth ellipsoid-style shading; otherwise a bevel is used.
        cells = (size, seed) adds plated skin: a jittered grid whose cell borders darken and whose cells vary a step."""
        m = s.mask(inside)
        at = lambda x, y: 0 <= x < s.w and 0 <= y < s.h and m[y][x]
        xs = [x for y in range(s.h) for x in range(s.w) if m[y][x]]
        if not xs: return m
        x0, x1 = min(xs), max(xs)
        for y in range(s.h):
            for x in range(s.w):
                if not m[y][x]: continue
                if light is not None:
                    l = light(x + 0.5, y + 0.5)
                    i = 3 if l > 0.78 else 2 if l > 0.5 else 1 if l > 0.26 else 0
                else:
                    up, lf, dn, rt = at(x, y - 1), at(x - 1, y), at(x, y + 1), at(x + 1, y)
                    if not bevel: i = 2
                    elif not dn and not rt: i = 0
                    elif not up or not lf: i = 3
                    elif not dn or not rt: i = 1
                    else:
                        t = (x - x0) / max(1, x1 - x0); i = 3 if t < 0.28 else 1 if t > 0.74 else 2
                if cells:
                    sz, sd = cells
                    cx, cy = x // sz, y // sz; best = 9; second = 9
                    for ox in (-1, 0, 1):
                        for oy in (-1, 0, 1):
                            px = (cx + ox + hash2(cx + ox, cy + oy, sd)) * sz; py = (cy + oy + hash2(cx + ox + 7, cy + oy + 3, sd)) * sz
                            d = math.hypot(x + 0.5 - px, y + 0.5 - py)
                            if d < best: second = best; best = d
                            elif d < second: second = d
                    if second - best < 0.9 and i > 0: i -= 1
                    elif i < 3 and hash2(cx, cy, sd + 5) > 0.7: i += 1 if hash2(x // sz, y // sz, sd + 9) > 0.5 else 0
                s.put(x, y, ramp[i])
        if outline:
            for y in range(-1, s.h + 1):
                for x in range(-1, s.w + 1):
                    if not at(x, y) and (at(x + 1, y) or at(x - 1, y) or at(x, y + 1) or at(x, y - 1)): s.put(x, y, outline)
        return m
    def crack(s, pts, hot='Y', mid='y', dark='k', th=1):
        """a glowing seam along the points: dark rim, hot centre"""
        for (a, b) in zip(pts, pts[1:]):
            s.line(a[0], a[1], b[0], b[1], dark, th + 2)
        for (a, b) in zip(pts, pts[1:]):
            s.line(a[0], a[1], b[0], b[1], mid, th + 1)
        for (a, b) in zip(pts, pts[1:]):
            s.line(a[0], a[1], b[0], b[1], hot, th)
    def eye(s, cx, cy, rx, ry, iris='Yw', pupil='q', glow='yk', slit=True):
        s.shape(ell(cx, cy, rx + 1.3, ry + 1.3), glow + glow, 'o', bevel=False)
        s.shape(ell(cx, cy, rx, ry), iris[0] * 2 + iris[-1] * 2, None, bevel=False)
        if slit: s.rect(round(cx), round(cy - ry + 0.5), round(cx), round(cy + ry - 0.5), pupil)
        s.put(round(cx - rx * 0.4), round(cy - ry * 0.45), 'w')

def ell(cx, cy, rx, ry): return lambda x, y: ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0
def box(x0, y0, x1, y1): return lambda x, y: x0 <= x <= x1 and y0 <= y <= y1
def poly(pts):
    def f(x, y):
        inside = False; n = len(pts)
        for i in range(n):
            (ax, ay), (bx, by) = pts[i], pts[(i + 1) % n]
            if (ay > y) != (by > y) and x < (bx - ax) * (y - ay) / (by - ay) + ax: inside = not inside
        return inside
    return f
def union(*fs): return lambda x, y: any(f(x, y) for f in fs)
def minus(a, b): return lambda x, y: a(x, y) and not b(x, y)
def both(a, b): return lambda x, y: a(x, y) and b(x, y)
def ring(cx, cy, r0, r1): return lambda x, y: r0 * r0 <= (x - cx) ** 2 + (y - cy) ** 2 <= r1 * r1
def lit(cx, cy, rx, ry, lx=-0.5, ly=-0.55):
    """ellipsoid lighting: 0..1 brightness for a point of a lit ellipsoid centred at cx,cy"""
    def f(x, y):
        nx, ny = (x - cx) / rx, (y - cy) / ry
        z = math.sqrt(max(0.0, 1 - nx * nx - ny * ny))
        return max(0.0, min(1.0, 0.18 + 0.5 * (lx * nx + ly * ny) / 0.74 + 0.5 * z))
    return f
def tube(pts, w0, w1):
    """a tapered limb along pts (list of (x, y)): inside test for the union of discs"""
    segs = []
    n = len(pts) - 1
    for i in range(n):
        (ax, ay), (bx, by) = pts[i], pts[i + 1]
        segs.append((ax, ay, bx, by, w0 + (w1 - w0) * i / max(1, n), w0 + (w1 - w0) * (i + 1) / max(1, n)))
    def f(x, y):
        for (ax, ay, bx, by, wa, wb) in segs:
            dx, dy = bx - ax, by - ay; L = dx * dx + dy * dy
            t = 0 if L == 0 else max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / L))
            px, py = ax + dx * t, ay + dy * t
            if math.hypot(x - px, y - py) <= wa + (wb - wa) * t: return True
        return False
    return f
def flip(rows): return [r[::-1] for r in rows]
