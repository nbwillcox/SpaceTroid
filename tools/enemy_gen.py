"""Zone 1 enemies -> js/art/zone1foes.js. Grids are authored short and padded to a fixed width; armor letters o,1-4 take the creature's colour ramp (crimson / teal) at compile time."""
import json, os

def pad(rows, w):
    out = []
    for r in rows:
        assert len(r) <= w, (r, len(r), w)
        out.append(r + '.' * (w - len(r)))
    return out

# --- shell crawler: armoured beetle, faces right, 16 x 13 -------------------------------------------------
SHELL = [
    "",
    "",
    "....ooooo",
    "..oo444433oo",
    ".o4443333322o",
    "o444333322221o...oo",
    "o4433332222211oooo4o",
    "o3333222221111o44oYo",
    ".o3322221111o.o44oo",
    "..o22221111o..ooo",
    "...oooooooo",
]
SHELL = pad(SHELL, 20)
def crawler(phase):
    rows = [list(r) for r in SHELL]
    # armour plate seams (dark groove with a lit lip on its left), then a bigger eye
    for x in (6, 10):
        for y in range(3, 10):
            if rows[y][x] not in 'o.':
                rows[y][x] = '1'
                if rows[y][x - 1] in '234': rows[y][x - 1] = '4' if rows[y][x - 1] != '4' else '4'
    rows[7][18] = 'W'; rows[6][18] = 'Y'; rows[6][17] = 'o'
    rows[8][17] = 'w'; rows[9][16] = 'w'
    rows += [list('.' * 20) for _ in range(4)]
    sh = [(-1, 0, 1), (0, 0, 0), (1, 0, -1), (0, 0, 0)][phase]
    lift = [(0, 1, 0), (0, 0, 0), (1, 0, 0), (0, 0, 0)][phase]
    for n, x in enumerate((4, 8, 13)):
        up = lift[n]
        rows[11][x] = 'o'; rows[11][x + 1] = 'o'
        rows[12 - up][x + sh[n]] = 'o'; rows[12 - up][x + sh[n] + 1] = '1'
        rows[13 - up][x + sh[n] - 1] = '1'; rows[13 - up][x + sh[n]] = '1'
    return [''.join(r) for r in rows]

# --- glow-moth: hovering flyer, 20 x 16, wings flap through 4 frames --------------------------------------
MOTH_BODY = [
    "........o44o",
    ".......o4332o",
    ".......o3322o",
    "......oo3221oo",
    "......o322 11o".replace(' ', ''),
    ".......o2211o",
    ".......oo11oo",
    "........oYYo",
    ".........oo",
]
WING = {  # (row, x0, x1) for the left wing, mirrored to the right; rows count from the top of the sprite
    'up':   [(0, 1, 2), (1, 1, 4), (2, 2, 6), (3, 3, 7), (4, 4, 8), (5, 5, 8)],
    'mid':  [(3, 0, 3), (4, 0, 7), (5, 1, 8), (6, 2, 8), (7, 4, 8)],
    'down': [(6, 0, 1), (7, 0, 3), (8, 1, 5), (9, 2, 7), (10, 3, 8), (5, 6, 8)],
}
def moth(kind):
    W, H = 20, 14
    g = [['.'] * W for _ in range(H)]
    by = 2 if kind != 'down' else 1
    for i, r in enumerate(pad(MOTH_BODY, W)):
        for x, c in enumerate(r):
            if c != '.' and 0 <= by + i < H: g[by + i][x] = c
    for (y, x0, x1) in WING[kind]:
        for x in range(x0, x1 + 1):
            c = 'h' if x == x0 else 'e' if x < x1 - 1 else 'E'
            if y == min(r for r, _, _ in WING[kind]): c = 'h'
            for xx in (x, W - 1 - x):
                if g[y][xx] == '.': g[y][xx] = c
    return [''.join(r) for r in g]
MOTH_FRAMES = ['up', 'mid', 'down', 'mid']

# --- spore pod: rooted turret, 16 x 24, closed / open mouth ---------------------------------------------
def pod(opened):
    rows = [
        "......ooo.......",
        ".....o444o......",
        "....o44332o.....",
        "...o4433322o....",
        "...o4333222o....",
        "...o3322211o....",
        "....o22211o.....",
        ".....o111o......",
        "......ooo.......",
    ]
    if opened:
        rows[2] = "....o4Yw32o....."; rows[3] = "...o4YYw322o...."
        rows[4] = "...o4wwY2222o..."; rows[5] = "...o3YYY2211o..."
    rows = rows + [
        "......DCB.......",
        "......DCB.......",
        ".....DDCB.......",
        "..F.FDCCBF.F....",
        "..DFDDCCBDFD....",
        "...DDCCCBBD.....",
        "..B.CDCBBC.B....",
        ".BBBBCCBBBBBB...",
        "BCDBBBBBBBBDCB..",
        "11BCB1BB1BCB11..",
    ]
    return pad(rows, 16)

# --- big shell crawler (replaces the small one): 36 x 28, shaded dome, plated, six-legged -----------------
import math
def _line(g, x0, y0, x1, y1, c, t=2):
    n = max(abs(x1 - x0), abs(y1 - y0), 1)
    for i in range(n + 1):
        x = round(x0 + (x1 - x0) * i / n); y = round(y0 + (y1 - y0) * i / n)
        for k in range(t):
            if 0 <= y < len(g) and 0 <= x + k < len(g[0]): g[y][x + k] = c

def crawler_big(phase):
    Wd, Hd = 36, 28
    g = [['.'] * Wd for _ in range(Hd)]
    # legs behind the body: hip, knee, foot per leg; phase swings the feet
    swing = [(-3, 0, 3), (0, 0, 0), (3, 0, -3), (0, 0, 0)][phase]
    lift = [(0, 2, 0), (0, 0, 0), (2, 0, 0), (0, 0, 0)][phase]
    for n, hx in enumerate((7, 15, 23)):
        fx = hx + 3 + swing[n]; fy = 27 - lift[n]
        _line(g, hx, 19, hx + 5, 22, 'o'); _line(g, hx + 5, 22, fx, fy, 'o')
        _line(g, hx + 1, 19, hx + 5, 21, '1', 1)
        for k in range(3): 
            if fy < 28: g[fy][min(Wd - 1, fx + k - 1)] = 'o'
    shape = [[False] * Wd for _ in range(Hd)]
    cx, cy, rx, ry = 15.5, 18.5, 14.5, 14.5
    def shade(x, y, ccx, ccy, rrx, rry):
        nx, ny = (x - ccx) / rrx, (y - ccy) / rry
        z = math.sqrt(max(0.0, 1 - nx * nx - ny * ny))
        l = -0.5 * nx - 0.55 * ny + 0.75 * z
        return '4' if l > 1.0 else '3' if l > 0.72 else '2' if l > 0.4 else '1'
    for y in range(0, 19):
        for x in range(Wd):
            nx, ny = (x - cx) / rx, (y - cy) / ry
            if nx * nx + ny * ny <= 1 and y >= 4:
                g[y][x] = shade(x, y, cx, cy, rx, ry); shape[y][x] = True
    for y in (19, 20):  # belly shadow band
        for x in range(Wd):
            if abs(x - cx) <= 14 - (y - 19) * 2:
                g[y][x] = '1'; shape[y][x] = True
    for sx in (9.5, 19.5):  # plate seams that follow the dome's curve
        for y in range(5, 19):
            for x in range(Wd):
                if shape[y][x] and abs(x - (sx - 0.18 * (cy - y))) < 0.55:
                    g[y][x] = '1'
                    if x > 0 and g[y][x - 1] in '23': g[y][x - 1] = '4' if g[y][x - 1] == '3' else '3'
    # head
    hx, hy, hr = 30.0, 17.0, 5.6
    for y in range(Hd):
        for x in range(Wd):
            if (x - hx) ** 2 + (y - hy) ** 2 <= hr * hr:
                g[y][x] = shade(x, y, hx, hy, hr, hr); shape[y][x] = True
    for (x, y, c) in [(31, 15, 'Y'), (32, 15, 'w'), (31, 16, 'y'), (30, 14, 'o'), (31, 14, 'o'), (32, 14, 'o'), (33, 15, 'o')]:
        g[y][x] = c
    for (x, y) in [(33, 21), (34, 22), (35, 22), (35, 21), (33, 20)]:
        g[y][x] = 'w' if (x + y) % 2 else 'y'; shape[y][x] = True
    _line(g, 31, 12, 33, 7, 'o', 1); _line(g, 33, 7, 35, 6, 'o', 1)
    # outline pass on the body shapes
    out = [r[:] for r in g]
    for y in range(Hd):
        for x in range(Wd):
            if shape[y][x] and g[y][x] not in 'owyY':
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    xx, yy = x + dx, y + dy
                    if not (0 <= xx < Wd and 0 <= yy < Hd) or not shape[yy][xx]:
                        out[y][x] = 'o'; break
    return [''.join(r) for r in out]

if __name__ == '__main__':
    out = {'crawler': [crawler_big(i) for i in range(4)], 'moth': [moth(k) for k in MOTH_FRAMES], 'pod': [pod(0), pod(1)]}
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'js', 'art', 'zone1foes.js')
    src = "/* GENERATED by tools/enemy_gen.py: zone 1 enemy frame grids (armor letters recolour per creature). */\n(function (G) {\n  G.art = G.art || {};\n  G.art.zone1foes = " + json.dumps(out, separators=(',', ':')) + ";\n})((window.SGS = window.SGS || {}));\n"
    open(path, 'w', encoding='utf-8').write(src)
    print('wrote', len(src))

