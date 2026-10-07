"""Item art -> js/art/items.js: ability icons (20x20, drawn as the object itself), tank pickups (energy E-tank, missile, super), enemy drop icons, and the shrine statues
(big for ability unlocks, small for upgrades). Everything is rasterised from simple shapes with automatic bevel shading and outlines, then written as palette-letter grids.
Letters: 'o','1'-'4' = the icon's armor ramp (dark -> light); metal z M m l L; gold s k y Y w; visor q x v V W; energy d g e E h; world stone digits 0-5 for statues."""
import json, math, os

class Cv:
    def __init__(s, w, h):
        s.w, s.h = w, h
        s.g = [['.'] * w for _ in range(h)]
    def put(s, x, y, c):
        if 0 <= x < s.w and 0 <= y < s.h: s.g[y][x] = c
    def rect(s, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1): s.put(x, y, c)
    def line(s, x0, y0, x1, y1, c, th=1):
        n = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(n + 1):
            x = round(x0 + (x1 - x0) * i / n); y = round(y0 + (y1 - y0) * i / n)
            for dx in range(th):
                for dy in range(th): s.put(x + dx, y + dy, c)
    def shape(s, inside, ramp='1234', outline='o', bevel=True):
        """paint every pixel whose centre is inside (a function of float x, y), bevel-shaded with the 4-letter ramp (dark -> light), then outline it"""
        m = [[inside(x + 0.5, y + 0.5) for x in range(s.w)] for y in range(s.h)]
        at = lambda x, y: 0 <= x < s.w and 0 <= y < s.h and m[y][x]
        xs = [x for y in range(s.h) for x in range(s.w) if m[y][x]]
        if not xs: return
        x0, x1 = min(xs), max(xs)
        for y in range(s.h):
            for x in range(s.w):
                if not m[y][x]: continue
                up, lf, dn, rt = at(x, y - 1), at(x - 1, y), at(x, y + 1), at(x + 1, y)
                if not bevel: c = ramp[2]
                elif not dn and not rt: c = ramp[0]
                elif not up or not lf: c = ramp[3]
                elif not dn or not rt: c = ramp[1]
                else:
                    t = (x - x0) / max(1, x1 - x0)
                    c = ramp[3] if t < 0.28 else ramp[1] if t > 0.74 else ramp[2]
                s.put(x, y, c)
        if outline:
            for y in range(-1, s.h + 1):
                for x in range(-1, s.w + 1):
                    if not at(x, y) and (at(x + 1, y) or at(x - 1, y) or at(x, y + 1) or at(x, y - 1)): s.put(x, y, outline)
    def rows(s): return [''.join(r) for r in s.g]

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
def ring(cx, cy, r0, r1): return lambda x, y: r0 * r0 <= (x - cx) ** 2 + (y - cy) ** 2 <= r1 * r1

FONT = {'E': ['11111', '10000', '10000', '11110', '10000', '10000', '11111'], 'S': ['01111', '10000', '10000', '01110', '00001', '00001', '11110'],
        'M': ['10001', '11011', '10101', '10101', '10001', '10001', '10001']}
def glyph(cv, ch, x0, y0, c):
    for j, r in enumerate(FONT[ch]):
        for i, b in enumerate(r):
            if b == '1': cv.put(x0 + i, y0 + j, c)

# ---------------------------------------------------------------- 20x20 ability icons
def missile(big=False, nose='1234'):
    cv = Cv(20, 20)
    cv.shape(poly([(5.5, 13), (5.5, 18), (2, 19.5), (2, 15)]), nose, 'z'); cv.shape(poly([(14.5, 13), (14.5, 18), (18, 19.5), (18, 15)]), nose, 'z')
    cv.shape(box(6.5, 6, 13.5, 17), 'MmlL', 'z')
    cv.shape(poly([(6.5, 6.5), (13.5, 6.5), (10, 0.5)]), nose, 'z')
    cv.rect(7, 10, 12, 11, 'y'); cv.rect(7, 12, 12, 12, 'k')
    if big: cv.rect(7, 14, 12, 15, 'Y'); cv.rect(9, 2, 10, 4, 'w')
    cv.rect(8, 17, 11, 18, 'z'); cv.put(9, 19, 'Y'); cv.put(10, 19, 'y')
    return cv.rows()

def bomb():
    cv = Cv(20, 20)
    cv.shape(ell(9.5, 12, 7.6, 7.6), 'zMml', 'z')
    cv.shape(box(7.5, 3.5, 11.5, 6.5), 'kyYw', 'z')
    cv.line(10, 3, 12, 1, 'y'); cv.line(12, 1, 15, 1, 'y'); cv.rect(15, 0, 16, 1, 'W')
    cv.put(17, 0, 'w'); cv.put(16, 2, 'Y'); cv.put(14, 0, 'Y')
    cv.rect(6, 9, 7, 10, 'L')
    return cv.rows()

def morph():
    cv = Cv(20, 20)
    cv.shape(ell(9.5, 10, 8.3, 8.3), '1234', 'o')
    cv.rect(2, 9, 17, 11, 'y'); cv.rect(3, 9, 16, 9, 'Y'); cv.rect(3, 11, 16, 11, 'k')
    cv.rect(5, 5, 7, 6, 'w'); cv.put(4, 7, 'w')
    return cv.rows()

def charge():
    cv = Cv(20, 20)
    cv.shape(ell(9.5, 10, 8.4, 8.4), '1234', 'o')
    cv.shape(ell(9.5, 10, 5.2, 5.2), 'gehE', None, bevel=False)
    for (a, b, c, d) in [(11, 4, 7, 10), (7, 10, 12, 10), (12, 10, 8, 16)]: cv.line(a, b, c, d, 'h', 2)
    cv.put(6, 6, 'w'); cv.put(7, 6, 'w')
    return cv.rows()

def ice():
    cv = Cv(20, 20)
    for (a, b, c, d) in [(9.5, 1, 9.5, 18), (2, 5.5, 17, 14), (2, 14, 17, 5.5)]: cv.line(round(a), round(b), round(c), round(d), '3', 2)
    for (cx, cy) in [(9, 1), (9, 18), (2, 5), (16, 14), (2, 14), (16, 5)]: cv.shape(poly([(cx, cy - 2.2), (cx + 2.2, cy), (cx, cy + 2.2), (cx - 2.2, cy)]), '1234', 'o')
    cv.shape(ell(10, 10, 3, 3), '1234', 'o'); cv.put(9, 9, 'h')
    return cv.rows()

def flame(ramp='1234', core='yYw'):
    cv = Cv(20, 20)
    cv.shape(poly([(10, 0.5), (14, 6), (17, 11), (15, 16), (10, 19.5), (5, 16), (3, 11), (6, 8), (8, 4)]), ramp, 'o')
    cv.shape(poly([(10, 8), (13, 12), (12, 16), (10, 18), (8, 16), (7, 12)]), core[0] + core[1] + core[1] + core[2], None)
    cv.shape(poly([(10, 12), (11.5, 14.5), (10, 17), (8.5, 14.5)]), core[2] * 4, None, bevel=False)
    return cv.rows()

def space():
    cv = Cv(20, 20)
    cv.shape(ring(9.5, 10, 6.4, 8.8), '1234', 'o')
    for dy in (0, 5):
        cv.shape(poly([(4, 9 + dy), (9.5, 3.5 + dy), (15, 9 + dy), (15, 12 + dy), (9.5, 7 + dy), (4, 12 + dy)]), 'kyYw', 'o')
    return cv.rows()

def dash():
    cv = Cv(20, 20)
    cv.shape(poly([(7, 3), (13, 3), (13, 11), (18, 13), (19, 17), (7, 17)]), '1234', 'o')
    cv.rect(7, 15, 18, 17, 'M'); cv.rect(7, 17, 18, 17, 'z'); cv.rect(8, 6, 12, 7, 'Y'); cv.rect(8, 9, 12, 9, 'y')
    for (y, l) in [(5, 5), (9, 4), (13, 5)]: cv.rect(6 - l, y, 5, y, 'W' if y == 9 else 'x')
    return cv.rows()

def wave():
    cv = Cv(20, 20)
    cv.shape(ell(9.5, 10, 8.6, 8.6), 'qxvV', 'o')
    pts = [(2 + i, 10 + round(4.5 * math.sin(i / 15.0 * 2 * math.pi * 1.5))) for i in range(0, 16)]
    for (x, y) in pts: cv.rect(x, y - 1, x + 1, y + 1, 'W'); cv.put(x, y, 'V')
    return cv.rows()

def aqua():
    cv = Cv(20, 20)
    cv.shape(union(poly([(10, 0.5), (15.5, 11), (4.5, 11)]), ell(10, 12.5, 6.4, 6.4)), '1234', 'o')
    cv.rect(7, 9, 8, 13, 'h'); cv.put(7, 8, 'h')
    return cv.rows()

def grapple():
    cv = Cv(20, 20)
    cv.line(10, 1, 10, 13, 'L', 2); cv.rect(8, 1, 11, 2, 'y'); cv.rect(8, 15, 11, 16, 'z')
    cv.shape(minus(ring(10, 13.5, 4.5, 8), box(0, 0, 20, 13)), 'MmlL', 'z')
    cv.shape(poly([(1, 12.5), (4.5, 12.5), (3, 18)]), 'MmlL', 'z'); cv.shape(poly([(15.5, 12.5), (19, 12.5), (17, 18)]), 'MmlL', 'z')
    return cv.rows()

def scan():
    cv = Cv(20, 20)
    cv.shape(poly([(1, 10), (5, 5), (10, 3), (15, 5), (19, 10), (15, 15), (10, 17), (5, 15)]), '1234', 'o')
    cv.shape(ell(10, 10, 4.2, 4.2), 'qxvV', 'q')
    cv.rect(9, 9, 10, 10, 'W'); cv.put(8, 8, 'W')
    return cv.rows()

ICONS = {'morph': (morph, 'teal'), 'missile': (lambda: missile(False, '1234'), 'crimson'), 'bombs': (bomb, 'cobalt'), 'charge': (charge, 'cobalt'), 'iceBeam': (ice, 'cobalt'),
         'heatSuit': (lambda: flame('1234', 'yYw'), 'crimson'), 'spaceJump': (space, 'teal'), 'dashBoots': (dash, 'cobalt'), 'waveBeam': (wave, 'visor'), 'aquaSuit': (aqua, 'teal'),
         'grapple': (grapple, 'cobalt'), 'superMissile': (lambda: missile(True, '1234'), 'teal'), 'scanVisor': (scan, 'teal'), 'plasmaBeam': (lambda: flame('1234', 'YwW'), 'crimson')}

# ---------------------------------------------------------------- tank pickups (20x22, two glint frames)
def tank(kind, frame):
    cv = Cv(20, 22)
    body = {'energy': '1234', 'missile': '1234', 'super': '1234'}[kind]
    cv.shape(box(3.5, 3.5, 16.5, 19.5), body, 'o')                       # glass body
    cv.shape(box(5.5, 7.5, 14.5, 15.5), 'bUuN' if kind == 'energy' else 'bUuN', 'o', bevel=False)   # label plate
    cv.shape(box(3, 1, 17, 4), 'zMml', 'z'); cv.shape(box(3, 19, 17, 21), 'zMml', 'z')   # caps
    cv.rect(4, 2, 16, 2, 'L')
    if kind == 'energy': glyph(cv, 'E', 7, 8, 'W')
    elif kind == 'missile':
        cv.rect(9, 9, 10, 14, 'L'); cv.rect(8, 11, 11, 11, 'y'); cv.shape(poly([(8.5, 9.5), (11.5, 9.5), (10, 7.2)]), '1234', None, bevel=False); cv.put(7, 13, 'x'); cv.put(12, 13, 'x')
    else:
        cv.rect(9, 9, 10, 14, 'L'); cv.rect(8, 11, 11, 11, 'Y'); cv.shape(poly([(8.5, 9.5), (11.5, 9.5), (10, 7.2)]), 'dgeE', None, bevel=False); cv.put(7, 13, 'g'); cv.put(12, 13, 'g')
    if frame: cv.rect(5, 5, 6, 6, 'W'); cv.put(7, 4, 'W'); cv.rect(5, 17, 5, 17, 'w')
    else: cv.rect(13, 16, 14, 17, 'w')
    return cv.rows()

# ---------------------------------------------------------------- enemy drops (small, 2 frames)
def drop_energy(f):
    cv = Cv(10, 10)
    cv.shape(ell(4.8, 5, 4.2, 4.2), 'dgeE', 'd'); cv.put(3, 3, 'h'); cv.put(4, 3, 'h')
    if f: cv.put(4, 4, 'h'); cv.put(3, 4, 'h')
    return cv.rows()

def drop_missile(f, nose='1234', band='y'):
    cv = Cv(10, 12)
    cv.shape(box(3.5, 4, 6.5, 9.5), 'MmlL', 'z'); cv.shape(poly([(3.5, 4.5), (6.5, 4.5), (5, 0.5)]), nose, 'z')
    cv.shape(poly([(3.5, 8), (3.5, 11), (1, 11.5), (1, 9)]), nose, 'z'); cv.shape(poly([(6.5, 8), (6.5, 11), (9, 11.5), (9, 9)]), nose, 'z')
    cv.rect(4, 6, 5, 6, band)
    if f: cv.put(5, 2, 'w')
    return cv.rows()

def drop_bomb(f):
    cv = Cv(10, 12)
    cv.shape(ell(4.8, 7.4, 3.9, 3.9), 'zMml', 'z'); cv.rect(4, 2, 5, 3, 'y'); cv.put(6, 1, 'y'); cv.put(7, 0, 'W' if f else 'Y'); cv.put(8, 0, 'w')
    cv.put(3, 6, 'L')
    return cv.rows()

DROPS = {'en': ('cobalt', [drop_energy(0), drop_energy(1)]), 'missile': ('crimson', [drop_missile(0), drop_missile(1)]),
         'super': ('teal', [drop_missile(0, '1234', 'Y'), drop_missile(1, '1234', 'Y')]), 'sbomb': ('cobalt', [drop_bomb(0), drop_bomb(1)])}

# ---------------------------------------------------------------- statues (front view, zone stone via 'world' keys: digits 0-5 are the zone's stone ramp)
def statue(W, H, small=False):
    cv = Cv(W, H); k = W / 48.0; sx = lambda v: v * k; sy = lambda v: v * (H / 72.0)
    cx = W / 2.0
    S = '2345' if not small else '2345'; O = '0'
    E = lambda a, b, c, d: ell(sx(a), sy(b), sx(c), sy(d))
    B = lambda a, b, c, d: box(sx(a), sy(b), sx(c), sy(d))
    P = lambda pts: poly([(sx(a), sy(b)) for (a, b) in pts])
    cv.shape(ring(sx(24), sy(17), sx(14.5), sx(17.5)), 'kyYw', O)                                         # halo behind the head
    cv.shape(P([(10, 52), (38, 52), (43, 67), (5, 67)]), '1234', O)                                         # robe
    cv.shape(P([(14, 30), (34, 30), (36, 52), (12, 52)]), S, O)                                             # torso
    cv.shape(E(24, 40, 3.2, 4.2), 'dgeE', 'd', bevel=False)                                                  # chest gem
    cv.shape(B(15, 46, 33, 48), 'kyYw', O)                                                                   # belt
    for (sg, ox) in ((-1, 0), (1, 0)):
        px = 24 + sg * 14
        cv.shape(E(px, 34, 6.5, 5.5), S, O); cv.shape(ring(sx(px), sy(34), sx(4.2), sx(6.2)), 'kyYw', None, bevel=False)         # pauldrons
        fx = 24 + sg * 11
        cv.shape(P([(24 + sg * 15, 38), (24 + sg * 19, 40), (24 + sg * 15, 52), (24 + sg * 11, 51)]), S, O)                      # upper arm
        cv.shape(P([(24 + sg * 17, 47), (24 + sg * 13, 55), (24 + sg * 8, 55), (24 + sg * 10, 48)]), S, O)                      # forearm reaching in
        cv.shape(E(24 + sg * 8, 55.5, 4.2, 2.6), 'kyYw', O)                                                                       # hands cupped under the item
    cv.shape(B(21, 27, 27, 31), S, O)                                                                        # neck
    cv.shape(E(24, 18, 8.2, 10), S, O)                                                                       # helmet
    cv.shape(B(18, 15.5, 30, 19), 'qxvV', 'q', bevel=False)                                                  # visor slit
    cv.rect(int(sx(20)), int(sy(17)), int(sx(22)), int(sy(17)), 'W')
    cv.shape(P([(24, 5), (26, 10), (22, 10)]), 'kyYw', O)                                                    # crest
    cv.shape(B(4, 65, 44, 68), '1234', O); cv.shape(B(1, 68, 47, 71.5), '1234', O)                          # plinth
    return cv.rows()

if __name__ == '__main__':
    out = {'icons': {}, 'ramps': {}, 'tanks': {}, 'drops': {}, 'dropRamps': {}, 'statue': {'big': statue(48, 72), 'small': statue(28, 42, True)}}
    for k, (fn, rp) in ICONS.items(): out['icons'][k] = fn(); out['ramps'][k] = rp
    for kd in ('energy', 'missile', 'super'): out['tanks'][kd] = [tank(kd, 0), tank(kd, 1)]
    for k, (rp, fr) in DROPS.items(): out['drops'][k] = fr; out['dropRamps'][k] = rp
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'js', 'art', 'items.js')
    src = "/* GENERATED by tools/item_gen.py: ability icons, tank pickups, enemy drop icons and the shrine statues. */\n(function (G) {\n  G.art = G.art || {};\n  G.art.items = " + json.dumps(out, separators=(',', ':')) + ";\n})((window.SGS = window.SGS || {}));\n"
    open(path, 'w', encoding='utf-8').write(src)
    print('wrote', len(src))
