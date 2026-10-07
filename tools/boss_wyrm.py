"""Zone 3 boss, the Cinder Wyrm: a lava serpent. Head 72 x 52 facing right (anchor 30,26), neck segment 32 x 18, lava splash 40 x 18. Ramp = crimson; glow uses gold."""
import math
from art_kit import *

def head(openmouth=False, glow=0):
    W, H = 72, 52
    cv = Cv(W, H)
    j = 14 if openmouth else 0                       # how far the lower jaw drops
    # neck stub and dorsal frill behind the skull
    cv.shape(ell(26, 44, 15, 9), 'o123', 'o', light=lit(26, 44, 15, 9, -0.5, -0.6), cells=(5, 2))
    for (bx, by, tx, ty) in [(14, 20, -2, 4), (12, 26, -3, 14), (12, 32, -3, 24), (14, 15, 4, -1), (18, 12, 12, -2)]:
        cv.shape(poly([(bx + 4, by - 3), (max(0, tx), max(0, ty)), (bx + 6, by + 5)]), 'oo12', 'o', bevel=False)
    # lower jaw first (it sits behind the upper jaw's teeth)
    lower = poly([(10, 32 + j * 0.3), (40, 30 + j * 0.7), (62, 29 + j), (71, 30 + j), (69, 35 + j), (52, 41 + j), (30, 45 + j * 0.5), (14, 43)])
    if openmouth:
        cv.shape(poly([(14, 31), (62, 27), (70, 28), (70, 30 + j), (40, 31 + j * 0.7), (12, 34)]), 'oobk', 'o', bevel=False)            # glowing throat
        cv.shape(ell(40, 34 + j * 0.45, 17, 3.5 + j * 0.22), 'kyYY', None, bevel=False)
        for x in range(32, 60, 5): cv.put(x, 42, 'Y'); cv.put(x + 2, 44, 'y')                                                     # molten drool
    cv.shape(lower, 'o123', 'o', light=lit(38, 36 + j * 0.6, 34, 12, -0.4, -0.7), cells=(5, 4))
    cv.shape(poly([(12, 40 + j * 0.3), (44, 38 + j * 0.8), (66, 34 + j), (62, 40 + j), (40, 44 + j * 0.7), (16, 44)]), 'oo11', None, bevel=False)    # shadowed throat plates
    for k in range(5):
        cv.line(18 + k * 9, 40 + int(j * 0.4), 22 + k * 9, 44 + int(j * 0.5), 'o', 1)
    cv.shape(poly([(34, 44 + j * 0.6), (40, 51), (47, 43 + j * 0.7)]), 'o123', 'o', bevel=False)                                    # chin spike
    # lower fangs
    for (x, h) in [(48, 6), (56, 7), (63, 6)]:
        cv.shape(poly([(x - 2, 31 + j), (x, 31 + j - h), (x + 2, 31 + j)]), 'wwww', 'o', bevel=False)
    # upper skull
    skull = poly([(6, 24), (9, 13), (20, 5), (37, 6), (52, 11), (62, 17), (71, 21), (72, 26), (63, 29), (40, 31), (20, 33), (8, 33)])
    cv.shape(skull, 'o123', 'o', light=lit(38, 20, 38, 17, -0.5, -0.7), cells=(5, 7))
    cv.shape(poly([(16, 14), (22, 9), (34, 10), (46, 14), (60, 20), (46, 18), (30, 17)]), 'oo1o', None, bevel=False)               # heavy brow shadow
    # twin horns swept back from the brow
    for (bx, by, tx, ty, w) in [(24, 10, 4, 1, 6), (32, 9, 18, -1, 5)]:
        cv.shape(poly([(bx + w, by + 1), (tx, ty + 2), (tx + 4, ty + 6), (bx - 2, by + 4)]), 'o234', 'o')
    # armoured nose ridge
    for x in (46, 52, 58, 64):
        cv.shape(poly([(x - 3, 18 + (x - 46) * 0.25), (x, 12 + (x - 46) * 0.25), (x + 3, 17 + (x - 46) * 0.25)]), 'o234', 'o', bevel=False)
    # eye: a slanted slit that burns white-yellow, with a nostril glow
    cv.shape(poly([(31, 16), (45, 13), (46, 18), (34, 21)]), 'kkYY', 'o', bevel=False)
    cv.rect(37, 15, 40, 19, 'w' if glow else 'Y'); cv.rect(38, 15, 38, 19, 'q')
    cv.put(66, 22, 'Y'); cv.put(67, 22, 'y'); cv.put(66, 23, 'y')
    # lava cracks across the cheek and snout
    cv.crack([(14, 23), (22, 27), (30, 25), (38, 29)], 'Y', 'y', 'k', 1)
    cv.crack([(52, 22), (58, 25), (63, 24)], 'Y', 'y', 'k', 1)
    # upper fangs (the long canines come down over the lower jaw)
    for (x, h) in [(42, 5), (49, 9), (57, 11), (64, 8)]:
        cv.shape(poly([(x - 2, 29), (x, 29 + h), (x + 2, 29)]), 'wwww', 'o', bevel=False)
    return cv.rows()

def neck():
    cv = Cv(32, 18)
    cv.shape(ell(17, 9, 14, 8), 'o123', 'o', light=lit(17, 9, 14, 8, -0.5, -0.7), cells=(4, 5))
    cv.shape(poly([(21, 2), (30, 5), (30, 13), (21, 16), (25, 9)]), 'oo12', None, bevel=False)                                   # paler belly plates
    for y in (5, 9, 13): cv.line(24, y, 29, y, 'o', 1)
    cv.shape(poly([(9, 3), (0, 9), (9, 15)]), 'o234', 'o', bevel=False)                                                           # dorsal spike
    cv.crack([(10, 6), (14, 9), (19, 8)], 'Y', 'y', 'k', 1)
    cv.put(11, 12, 'y'); cv.put(16, 4, 'y')
    return cv.rows()

def splash(f):
    cv = Cv(40, 18)
    cv.rect(0, 14, 39, 17, 'k'); cv.rect(0, 15, 39, 17, 'y'); cv.rect(2, 16, 37, 17, 'Y')
    random_h = [(5, 9, 5), (10, 13, 3), (16, 7, 6), (21, 11, 4), (27, 9, 7), (33, 12, 3), (36, 8, 5)]
    for i, (x, hh, w) in enumerate(random_h):
        h = hh + (3 if (i + f) % 3 == 0 else 0) - (2 if (i + f) % 3 == 1 else 0)
        cv.shape(poly([(x - 1, 15), (x + 1, 15 - h), (x + 3, 15)]), 'kyYw', None, bevel=False)
        cv.put(x + 1, 15 - h - 2 - (f % 2), 'Y'); cv.put(x - 2 + f, 15 - h // 2, 'y')
    return cv.rows()

def build():
    return {'head': [head(False), head(True, 1)], 'neck': neck(), 'splash': [splash(i) for i in range(3)]}

if __name__ == '__main__':
    for r in head(True): print(r)
