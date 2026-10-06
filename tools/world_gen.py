"""Doors, item orbs and tanks, save pad, map terminal and the crashed-ship decor -> js/art/world1.js"""
import json, math, os

def grid(w, h, c='.'): return [[c] * w for _ in range(h)]
def fin(g): return [''.join(r) for r in g]
def put(g, x, y, c):
    if 0 <= y < len(g) and 0 <= x < len(g[0]): g[y][x] = c
def rect(g, x0, y0, x1, y1, c):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1): put(g, x, y, c)

# ---- doors: 16 x 48. Shield letters o,1-4 take the ramp of the compile-time key set (cobalt / crimson / teal / gold); frame letters are metal ----
def door(frame):
    g = grid(16, 48)
    open_px = [0, 9, 18, 27, 36][frame]
    for y in range(48):
        for x in (0, 1, 2, 13, 14, 15):
            c = {0: 'z', 1: 'M', 2: 'm', 13: 'm', 14: 'M', 15: 'z'}[x]
            if x in (1, 14) and y % 8 == 3: c = 'l'
            g[y][x] = c
    rect(g, 0, 0, 15, 3, 'M'); rect(g, 0, 0, 15, 0, 'z'); rect(g, 1, 1, 14, 1, 'l'); rect(g, 1, 2, 14, 2, 'm')
    rect(g, 0, 44, 15, 47, 'M'); rect(g, 0, 47, 15, 47, 'z'); rect(g, 1, 44, 14, 44, 'l'); rect(g, 1, 45, 14, 45, 'm')
    for x in (4, 11): put(g, x, 1, 'y'); put(g, x, 46, 'y')
    if 4 <= 43 - open_px:
        rect(g, 3, 4, 12, 43 - open_px, 'o')
        rect(g, 4, 5, 11, 42 - open_px, '2')
        for y in range(5, 43 - open_px):
            for x in range(4, 12):
                if int((x - 4) + (y - 5) * 0.5) % 9 < 1: g[y][x] = '3'
                if x == 4: g[y][x] = '4' if y % 6 else '3'
                if x == 11: g[y][x] = '1'
        if open_px == 0:   # central emblem: a diamond with stems
            for (dx, dy, c) in [(0, 0, '4'), (-1, 1, '4'), (1, 1, '4'), (-2, 2, '3'), (2, 2, '3'), (-1, 3, '3'), (1, 3, '3'), (0, 4, '4')]:
                put(g, 7 + dx, 19 + dy, c); put(g, 8 + dx, 19 + dy, c)
            for y in (10, 11, 12, 27, 28, 29): put(g, 7, y, '4'); put(g, 8, y, '4')
    return fin(g)

# ---- collectible orb: 16 x 16 sphere, three shine phases (ramp via key set) ----
def orb(phase):
    g = grid(16, 16)
    for y in range(16):
        for x in range(16):
            dx, dy = (x + 0.5 - 8) / 7.6, (y + 0.5 - 8) / 7.6; d2 = dx * dx + dy * dy
            if d2 > 1: continue
            if d2 > 0.78: g[y][x] = 'o'; continue
            dz = math.sqrt(1 - d2); lam = -0.55 * dx - 0.6 * dy + 0.6 * dz
            g[y][x] = '4' if lam > 0.8 else '3' if lam > 0.52 else '2' if lam > 0.2 else '1'
    sx, sy = [(4, 4), (5, 4), (5, 5)][phase]
    put(g, sx, sy, 'h'); put(g, sx + 1, sy, 'h'); put(g, sx, sy + 1, 'h')
    for (x, y) in [(7, 7), (8, 7), (7, 8), (8, 8)]: g[y][x] = 'h' if phase != 1 else 'E'
    return fin(g)

def tank(kind, lit):
    g = grid(14, 14)
    rect(g, 0, 0, 13, 13, 'z'); rect(g, 1, 1, 12, 12, 'm'); rect(g, 1, 1, 12, 1, 'L'); rect(g, 1, 1, 1, 12, 'l'); rect(g, 12, 2, 12, 12, 'M'); rect(g, 2, 12, 12, 12, 'M')
    rect(g, 3, 3, 10, 10, 'z')
    if kind == 'energy':
        rect(g, 4, 4, 9, 9, 'g'); rect(g, 4, 4, 9, 6, 'E' if lit else 'e'); rect(g, 4, 4, 9, 4, 'h'); rect(g, 5, 6, 8, 7, 'h' if lit else 'E')
    elif kind == 'missile':
        for (x, y, c) in [(6, 4, 'w'), (7, 4, 'w'), (5, 5, 'Y'), (6, 5, 'Y'), (7, 5, 'Y'), (8, 5, 'Y')]: put(g, x, y, c)
        rect(g, 5, 6, 8, 9, 'Y' if lit else 'y'); rect(g, 5, 6, 5, 9, 'w'); rect(g, 8, 6, 8, 9, 'k'); rect(g, 5, 9, 8, 9, 'k')
    else:
        rect(g, 4, 4, 9, 9, 'k'); rect(g, 5, 5, 8, 8, 'Y' if lit else 'y'); rect(g, 5, 5, 6, 6, 'w')
    return fin(g)

def pad(phase):
    """save pad: 32 x 26, two pylons and a glowing deck"""
    g = grid(32, 26)
    rect(g, 2, 22, 29, 25, 'M'); rect(g, 2, 22, 29, 22, 'L'); rect(g, 3, 23, 28, 23, 'l'); rect(g, 2, 25, 29, 25, 'z'); rect(g, 0, 24, 1, 25, 'M'); rect(g, 30, 24, 31, 25, 'M')
    for sx in (4, 24):
        rect(g, sx, 6, sx + 3, 21, 'm'); rect(g, sx, 6, sx, 21, 'l'); rect(g, sx + 3, 6, sx + 3, 21, 'M'); rect(g, sx, 4, sx + 3, 5, 'L')
        for y in range(8, 20, 3): rect(g, sx + 1, y, sx + 2, y + 1, 'E' if (y // 3 + phase) % 2 else 'e')
    rect(g, 8, 19, 23, 21, 'g'); rect(g, 9, 20, 22, 21, 'E' if phase else 'e'); rect(g, 8, 19, 23, 19, 'h')
    return fin(g)

def terminal(phase):
    """map terminal: 24 x 40 console with a glowing screen"""
    g = grid(24, 40)
    rect(g, 2, 34, 21, 39, 'M'); rect(g, 2, 34, 21, 34, 'L'); rect(g, 2, 39, 21, 39, 'z')
    rect(g, 5, 12, 18, 33, 'm'); rect(g, 5, 12, 5, 33, 'l'); rect(g, 18, 12, 18, 33, 'M'); rect(g, 4, 10, 19, 11, 'L')
    rect(g, 7, 14, 16, 27, 'z'); rect(g, 8, 15, 15, 26, 'g')
    for y in range(16, 26, 2):
        for x in range(9, 15):
            if (x * 5 + y * 3 + phase * 7) % 4 < 2: put(g, x, y, 'E')
    for (x, y) in [(10, 18), (11, 18), (11, 19), (12, 19), (12, 20), (13, 20)]: put(g, x, y, 'h')
    rect(g, 8, 29, 15, 31, 'M'); put(g, 9, 30, 'E' if phase else 'y'); put(g, 12, 30, 'y'); put(g, 14, 30, 'Y' if phase else 'k')
    return fin(g)

def wreck():
    """crashed ship hull section, 104 x 60: scorched plates, torn edge, gold stripe"""
    W, H = 104, 60
    g = grid(W, H)
    for y in range(H):
        for x in range(W):
            nx, ny = (x - 52) / 52.0, (y - 40) / 40.0
            torn = 0.05 * math.sin(x * 0.9) + 0.04 * math.sin(y * 1.3)
            if nx * nx + ny * ny <= 1 + torn and y <= 54 and x > 4 + int(5 * math.sin(y * 0.5)):
                lam = -0.5 * nx - 0.7 * ny + 0.5
                g[y][x] = 'l' if lam > 0.9 else 'm' if lam > 0.55 else 'M' if lam > 0.2 else 'z'
    for x in range(8, 100, 14):
        for y in range(6, 54):
            if g[y][x] != '.': g[y][x] = 'z'
    for y in (22, 38):
        for x in range(W):
            if g[y][x] != '.': g[y][x] = 'z'
    for y in range(30, 34):
        for x in range(W):
            if g[y][x] != '.': g[y][x] = 'Y' if y == 30 else 'y' if y < 33 else 'k'
    for (cx, cy, r) in [(30, 16, 9), (74, 12, 7), (60, 46, 8), (88, 36, 6)]:
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r and 0 <= y < H and 0 <= x < W and g[y][x] != '.':
                    g[y][x] = 'z' if (x + y) % 3 else 'M'
    for (x, y) in [(40, 8), (41, 8), (42, 9), (70, 50), (71, 50), (20, 44), (21, 45)]:
        put(g, x, y, '.')
    for y in range(12, 18):
        for x in range(82, 96):
            if g[y][x] != '.': g[y][x] = 'g' if (x + y) % 5 else 'e'
    out = [r[:] for r in g]
    for y in range(H):
        for x in range(W):
            if g[y][x] == '.':
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    xx, yy = x + dx, y + dy
                    if 0 <= xx < W and 0 <= yy < H and g[yy][xx] != '.': out[y][x] = 'z'; break
    return fin(out)

if __name__ == '__main__':
    out = {'door': [door(f) for f in range(5)], 'orb': [orb(i) for i in range(3)],
           'tankEnergy': [tank('energy', 0), tank('energy', 1)], 'tankMissile': [tank('missile', 0), tank('missile', 1)], 'tankSuper': [tank('super', 0), tank('super', 1)],
           'pad': [pad(0), pad(1)], 'terminal': [terminal(0), terminal(1)], 'wreck': wreck()}
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'js', 'art', 'world1.js')
    src = "/* GENERATED by tools/world_gen.py: doors, item orbs and tanks, save pad, map terminal, crashed-ship decor. */\n(function (G) {\n  G.art = G.art || {};\n  G.art.world1 = " + json.dumps(out, separators=(',', ':')) + ";\n})((window.SGS = window.SGS || {}));\n"
    open(path, 'w', encoding='utf-8').write(src)
    print('wrote', len(src))
