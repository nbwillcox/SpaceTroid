"""Zone 3 enemy + boss art -> js/art/zone3foes.js: magmite (lava leaper), Cinder Wyrm head (closed / open), neck segment and lava splash. Compile with 'crimson' (digits) + gold letters Y y w k."""
import json, math, os

def blank(w, h): return [['.'] * w for _ in range(h)]
def put(g, x, y, c):
    if 0 <= y < len(g) and 0 <= x < len(g[0]): g[y][x] = c
def line(g, x0, y0, x1, y1, c, t=1):
    n = max(abs(x1 - x0), abs(y1 - y0), 1)
    for i in range(n + 1):
        x = round(x0 + (x1 - x0) * i / n); y = round(y0 + (y1 - y0) * i / n)
        for dx in range(t):
            for dy in range(t): put(g, x + dx, y + dy, c)
def shade(x, y, cx, cy, rx, ry, bias=0.62):
    nx, ny = (x - cx) / rx, (y - cy) / ry
    z = math.sqrt(max(0.0, 1 - nx * nx - ny * ny)); l = -0.5 * nx - 0.55 * ny + bias * z
    return '4' if l > 1.0 else '3' if l > 0.7 else '2' if l > 0.36 else '1'
def outline(g):
    h, w = len(g), len(g[0]); out = [r[:] for r in g]
    for y in range(h):
        for x in range(w):
            if g[y][x] == '.':
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    xx, yy = x + dx, y + dy
                    if 0 <= xx < w and 0 <= yy < h and g[yy][xx] != '.': out[y][x] = 'o'; break
    return [''.join(r) for r in out]

def magmite(f):
    """magmite 16 x 22: a molten blob with a flame tail; f 0 calm, 1 stretched mid-leap"""
    W, H = 16, 22; g = blank(W, H); cy = 14.0 if f == 0 else 11.0; ry = 6.5 if f == 0 else 8.5; cx, rx = 8.0, 6.5 if f == 0 else 5.5
    for y in range(H):
        for x in range(W):
            nx, ny = (x - cx) / rx, (y - cy) / ry
            if nx * nx + ny * ny <= 1: g[y][x] = shade(x, y, cx, cy, rx, ry)
    for k in range(6 if f else 3):
        put(g, 8 + (k % 2) - 1, int(cy + ry) + k, 'Y' if k < 2 else 'y' if k < 4 else 'k')
        put(g, 8 + (k % 2), int(cy + ry) + k, 'y' if k < 3 else 'k')
    for dx in (-2, 2): put(g, 8 + dx, int(cy) - 2, 'w'); put(g, 8 + dx, int(cy) - 1, 'Y')
    for dx in range(-3, 4): put(g, 8 + dx, int(cy) + 2, '1')
    for (x, y) in ((4, int(cy) - ry - 1), (8, int(cy) - ry - 2), (12, int(cy) - ry - 1)): put(g, int(x), int(y), 'Y')
    return outline(g)

def wyrm_head(open_):
    """Cinder Wyrm head, 72 x 52, facing right: skull, horns, long jaw; open_ shows the glowing maw"""
    W, H = 72, 52; g = blank(W, H)
    cx, cy, rx, ry = 30.0, 26.0, 24.0, 19.0
    for y in range(H):
        for x in range(W):
            nx, ny = (x - cx) / rx, (y - cy) / ry
            if nx * nx + ny * ny <= 1: g[y][x] = shade(x, y, cx, cy, rx, ry)
    for y in range(H):                      # snout wedge
        for x in range(46, 70):
            t = (x - 46) / 24.0; top = 20 + t * 8; bot = 36 - t * 3
            if top <= y <= bot and not (open_ and y > 30 + t * 2 and t > 0.15): g[y][x] = shade(x, y, 40, 28, 30, 16)
    if open_:                               # lower jaw drops, maw glows
        for y in range(34, 46):
            for x in range(40, 70):
                t = (x - 40) / 30.0
                if 34 + t * 8 <= y <= 38 + t * 8: g[y][x] = '2' if y < 38 + t * 8 - 1 else '1'
        for y in range(28, 40):
            for x in range(44, 68):
                t = (x - 44) / 24.0
                if 29 + t * 3 <= y <= 36 + t * 7 and g[y][x] != '.': g[y][x] = 'Y' if abs(y - (33 + t * 5)) < 2 else 'y'
        for k in range(5): put(g, 50 + k * 4, 30 + k // 2, 'w'); put(g, 52 + k * 4, 38 + k // 2, 'w')
    for k in range(4):                      # horns sweeping back
        line(g, 20 + k * 5, 12, 10 + k * 3, 2 - k, '3', 3); line(g, 21 + k * 5, 12, 11 + k * 3, 3 - k, '4', 1)
    for (x, y) in ((38, 18), (39, 18), (40, 18), (41, 19), (42, 19), (38, 19), (39, 19)): put(g, x, y, 'Y' if (x + y) % 2 else 'w')
    for k in range(10): put(g, 34 + k, 15 + k // 4, 'o')
    for k in range(6): put(g, 62 + k // 2, 24 + k // 3, 'k')       # nostril smoulder
    return outline(g)

def neck_segment():
    """one ring of the wyrm's neck, 32 x 18: banded plate with lit left and glowing seams"""
    W, H = 32, 18; g = blank(W, H)
    for y in range(H):
        for x in range(W):
            nx, ny = (x - 15.5) / 15.5, (y - 8.5) / 9.0
            if nx * nx * 0.7 + ny * ny <= 1: g[y][x] = shade(x, y, 15.5, 6.0, 16.0, 14.0, 0.7)
    for y in range(H):
        for x in range(W):
            if g[y][x] != '.' and (y == 0 or y == H - 1 or abs(y - 9) == 8): g[y][x] = 'k'
    for x in range(4, 28, 4):
        for y in range(3, 15): 
            if g[y][x] != '.': g[y][x] = '1'
    for x in range(6, 26, 8): put(g, x, 8, 'Y'); put(g, x + 1, 8, 'y')
    return outline(g)

def splash(f):
    W, H = 40, 18; g = blank(W, H)
    for k in range(12):
        x = 4 + k * 3 + (k * 7 + f * 5) % 3; h = 3 + (k * 5 + f * 3) % 8
        for y in range(h): put(g, x, H - 1 - y, 'Y' if y > h - 3 else 'y'); put(g, x + 1, H - 1 - y, 'k' if y < h - 2 else 'y')
    return [''.join(r) for r in g]

if __name__ == '__main__':
    out = {'magmite': [magmite(0), magmite(1)], 'head': [wyrm_head(False), wyrm_head(True)], 'neck': neck_segment(), 'splash': [splash(0), splash(1), splash(2)]}
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'js', 'art', 'zone3foes.js')
    src = "/* GENERATED by tools/enemy_gen3.py: zone 3 magmite and Cinder Wyrm art. */\n(function (G) {\n  G.art = G.art || {};\n  G.art.zone3foes = " + json.dumps(out, separators=(',', ':')) + ";\n})((window.SGS = window.SGS || {}));\n"
    open(path, 'w', encoding='utf-8').write(src)
    print('wrote', len(src))
