"""Zone 5 boss, the Hive Heart: a monstrous pulsing heart, body 128 x 128 (centre 64,64 is the weak point) and 34 x 34 eye-pod nodes. Ramp = visor (o,1-4: dark purple -> pink); glow uses gold."""
import math
from art_kit import *

W = 128

def heart(state=0):
    """state 0 = lids shut, 1 = open, 2 = wide open and blazing"""
    cv = Cv(W, W)
    # carapace spikes ringing the mass
    for k in range(12):
        a = k / 12.0 * 6.283 + 0.2
        bx, by = 64 + math.cos(a) * 52, 68 + math.sin(a) * 50
        tx, ty = 64 + math.cos(a) * 63, 68 + math.sin(a) * 61
        if ty < 4 or ty > 124 or tx < 2 or tx > 125: continue
        nx, ny = -math.sin(a), math.cos(a)
        cv.shape(poly([(bx + nx * 5, by + ny * 5), (tx, ty), (bx - nx * 5, by - ny * 5)]), 'o234', 'o')
    # great vessels rising from the top, ending in ragged open mouths
    for (x0, y0, x1, y1, w) in [(48, 38, 36, 8, 7), (64, 32, 64, 3, 8), (80, 38, 92, 8, 7)]:
        cv.shape(tube([(x0, y0 + 10), (x1, y1 + 5)], w, w - 1), 'o112', 'o', cells=(4, 3))
        cv.shape(ell(x1, y1 + 4, w, 3.5), 'oqbU', 'o', bevel=False)
        cv.crack([(x0, y0 + 8), ((x0 + x1) / 2, (y0 + y1) / 2 + 6), (x1, y1 + 8)], 'Y', 'y', 'k', 1)
    # the heart: two lobes tapering to an apex, fleshy and plated
    body = union(ell(46, 68, 34, 38), ell(82, 68, 34, 38), poly([(14, 84), (114, 84), (64, 124)]))
    cv.shape(body, 'o112', 'o', light=lit(64, 70, 54, 52, -0.5, -0.65), cells=(6, 11))
    # muscle ridges and a deep groove down the middle
    for r in (18, 30, 42):
        pts = [(64 - r * math.sin(t), 68 - r * 0.9 * math.cos(t) + 6) for t in [-1.2, -0.7, -0.2, 0.3, 0.8, 1.3]]
        for a, b in zip(pts, pts[1:]): cv.line(round(a[0]), round(a[1]), round(b[0]), round(b[1]), 'o', 1)
    cv.line(64, 36, 64, 118, 'o', 2)
    # veins: branching, with yellow pus pulsing along them
    rng = [(24, 50, 8, 30), (30, 70, 10, 78), (98, 52, 118, 32), (92, 76, 116, 82), (40, 92, 28, 112), (88, 94, 100, 112), (50, 52, 36, 36), (80, 54, 96, 38)]
    for (x0, y0, x1, y1) in rng:
        cv.line(x0, y0, x1, y1, 'x', 2); cv.line(x0, y0, x1, y1, 'V', 1)
        mx, my = (x0 + x1) // 2, (y0 + y1) // 2
        cv.put(mx, my, 'Y'); cv.put(mx + 1, my + 1, 'y')
        cv.line(mx, my, mx + (6 if x1 > x0 else -6), my + 7, 'x', 1)
    # the central eye-maw
    cx, cy = 64, 66
    lid = {0: 3, 1: 9, 2: 14}[state]
    rx = {0: 26, 1: 24, 2: 25}[state]
    cv.shape(ell(cx, cy, rx + 4, lid + 5), 'oqbU', 'o', bevel=False)                                  # raw socket
    cv.shape(ell(cx, cy, rx, lid), 'oqvV' if state == 0 else 'qxvV', 'q', bevel=False)
    if state:
        iris = lid - 3
        cv.shape(ell(cx, cy, 15 + state * 2, iris + 1), 'kyYw', 'k', light=lit(cx, cy, 15, iris, -0.3, -0.5))
        cv.rect(cx - 1, cy - iris, cx, cy + iris, 'q')                                                  # slit pupil
        cv.put(cx - 7, cy - iris // 2, 'w'); cv.put(cx - 6, cy - iris // 2, 'w')
    else:
        cv.line(cx - rx + 2, cy, cx + rx - 2, cy, 'q', 2)                                                # lids sewn shut with a row of stitches
    # fangs around the socket (they bare when it opens)
    n = 14
    for i in range(n):
        a = i / n * 6.283
        x = cx + math.cos(a) * (rx + 3); y = cy + math.sin(a) * (lid + 6)
        h = 3 + state * 3
        cv.shape(poly([(x - 2, y - 1 if math.sin(a) < 0 else y + 1), (x - math.cos(a) * (-h), y - math.sin(a) * (-h) * 0.7 + (-2 if math.sin(a) < 0 else 2)), (x + 2, y)]), 'wwww', 'o', bevel=False)
    # slime drooling from the apex and the lower lobes
    for (x, l) in [(40, 8), (56, 12), (74, 10), (88, 6), (64, 14)]:
        y0 = 108 + (6 if x == 64 else 0) - int(abs(x - 64) * 0.4)
        cv.line(x, y0, x, y0 + l, 'k', 2); cv.put(x, y0 + l + 1, 'Y'); cv.put(x, y0 + l - 3, 'y')
    return cv.rows()

def node(flash=False):
    cv = Cv(34, 34)
    for k in range(8):
        a = k / 8.0 * 6.283
        bx, by = 17 + math.cos(a) * 11, 17 + math.sin(a) * 11
        tx, ty = 17 + math.cos(a) * 16, 17 + math.sin(a) * 16
        nx, ny = -math.sin(a), math.cos(a)
        cv.shape(poly([(bx + nx * 3, by + ny * 3), (tx, ty), (bx - nx * 3, by - ny * 3)]), 'o234', 'o', bevel=False)
    cv.shape(ell(17, 17, 12, 12), 'oxvV' if not flash else 'wwww', 'o', light=lit(17, 17, 12, 12, -0.4, -0.6))
    cv.shape(ell(17, 17, 7, 7), 'kyYw' if not flash else 'wwwW', 'k', bevel=False)
    cv.rect(16, 11, 17, 23, 'q'); cv.put(13, 14, 'w')
    return cv.rows()

def build():
    return {'heart': [heart(0), heart(1), heart(2)], 'node': [node(False), node(True)]}

if __name__ == '__main__':
    for r in heart(2): print(r)
