"""Zone 4 boss, the Abyssal Jelly: a deep-sea horror, bell 112 x 78 (drawn at x-56, y-44; the tentacles are drawn in code). Ramp = teal (o,1-4); the eye uses visor letters; glow uses energy letters."""
import math
from art_kit import *

W, H = 112, 78
CX = 56.0

def bell(openm=False, pulse=0):
    cv = Cv(W, H)
    flare = 6 if openm else 0
    # crown of curved spikes
    for (x, h, lean) in [(24, 12, -5), (36, 15, -3), (48, 17, -1), (64, 17, 1), (76, 15, 3), (88, 12, 5)]:
        y = 34 - 33 * math.sqrt(max(0.0, 1 - ((x - CX) / 52.0) ** 2)) + 3
        cv.shape(poly([(x - 4, y + 4), (x + lean, y - h), (x + 4, y + 3)]), 'o234', 'o')
    # the dome: a lit ellipsoid, ribbed, with a scalloped skirt
    dome = lambda x, y: ((x - CX) / 52.0) ** 2 + ((y - 36.0 - 0) / 33.0) ** 2 <= 1 and y <= 40 + flare * 0.5
    skirt_pts = [(4 - flare, 38)]
    n = 10
    for i in range(n + 1):
        x = 4 - flare + (104 + 2 * flare) * i / n
        skirt_pts.append((x, 60 + flare + (4 if i % 2 == 0 else 0) * (0.6 + 0.4 * math.sin(i))))
        if i < n: skirt_pts.append((x + (104 + 2 * flare) / n / 2, 54 + flare))
    skirt_pts.append((108 + flare, 38))
    cv.shape(union(dome, poly(skirt_pts)), '1234', 'o', light=lit(CX, 36, 54, 36, -0.45, -0.7), cells=(7, 6))
    # radial canals glowing under the skin
    for k in range(11):
        a = math.pi * (0.1 + 0.8 * k / 10.0)
        pts = []
        for t in (0.3, 0.5, 0.7, 0.9):
            pts.append((CX + math.cos(a) * 50 * t, 46 - math.sin(a) * 38 * t + (12 if t > 0.6 else 6)))
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]): cv.line(round(x0), round(y0), round(x1), round(y1), 'g' if k % 2 else 'd', 1)
        cv.put(pts[-1][0], pts[-1][1], 'h')
    # bioluminescent warts along the rim
    for i in range(14):
        x = 10 + i * 7 + (i % 2) * 2; y = 52 + (i % 3) * 2
        cv.shape(ell(x, y, 2, 2), 'dgeh', None, bevel=False)
    # inner organs: lobes around the central eye
    for (lx, ly, rx, ry) in [(30, 44, 11, 8), (82, 44, 11, 8), (40, 56, 9, 6), (72, 56, 9, 6)]:
        cv.shape(ell(lx, ly, rx, ry), 'oUnN' if not pulse else 'bUnN', 'o', light=lit(lx, ly, rx, ry, -0.4, -0.6))
        cv.put(lx - 2, ly - 2, 'h'); cv.put(lx + 1, ly + 1, 'e')
    cv.shape(ell(CX, 46, 20, 15), 'obUn', 'o', light=lit(CX, 46, 20, 15, -0.3, -0.6))              # stomach ring
    # the eye: a huge slit-pupilled orb (the weak point)
    ey = 46
    cv.shape(ell(CX, ey, 15 + pulse, 11 + pulse), 'oxvV', 'o', light=lit(CX, ey, 15, 11, -0.3, -0.6))
    cv.shape(ell(CX, ey, 8 + pulse * 0.5, 7 + pulse * 0.5), 'VWWW', 'x', bevel=False)
    cv.rect(CX - 1, ey - 8 - pulse, CX, ey + 8 + pulse, 'q')
    cv.put(CX - 6, ey - 5, 'w'); cv.put(CX - 5, ey - 5, 'w')
    # veins running out of the eye
    for (dx, dy) in [(-18, -6), (18, -6), (-14, 10), (14, 10)]:
        cv.line(round(CX + dx * 0.55), round(ey + dy * 0.55), round(CX + dx), round(ey + dy), 'x', 1)
    if openm:
        # the underside gapes: a wide ring of fangs around a dark maw
        cv.shape(ell(CX, 66, 30, 9), 'ooqq', 'o', bevel=False)
        cv.shape(ell(CX, 66, 22, 5.5), 'xvVV', None, bevel=False)
        for i in range(12):
            x = CX - 26 + i * 4.7
            cv.shape(poly([(x - 2.2, 60), (x, 68), (x + 2.2, 60)]), 'wwww', 'o', bevel=False)
            cv.shape(poly([(x - 2.2, 74), (x, 65), (x + 2.2, 74)]), 'wwww', 'o', bevel=False)
    return cv.rows()

def build():
    return {'bell': [bell(False, 0), bell(True, 1)]}

if __name__ == '__main__':
    for r in bell(False): print(r)
