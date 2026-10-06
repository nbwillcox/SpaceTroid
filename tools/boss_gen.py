"""Zone 1 boss, the Mossback Warden: giant plated beetle, 124 x 80, facing right -> js/art/boss1.js"""
import json, math, os
Wd, Hd = 124, 80

def blank(): return [['.'] * Wd for _ in range(Hd)]
def put(g, x, y, c):
    if 0 <= x < Wd and 0 <= y < Hd: g[y][x] = c
def line(g, x0, y0, x1, y1, c, t=3):
    n = max(abs(x1 - x0), abs(y1 - y0), 1)
    for i in range(n + 1):
        x = round(x0 + (x1 - x0) * i / n); y = round(y0 + (y1 - y0) * i / n)
        for dx in range(t):
            for dy in range(t): put(g, x + dx - t // 2, y + dy - t // 2, c)

def shade(x, y, cx, cy, rx, ry):
    nx, ny = (x - cx) / rx, (y - cy) / ry
    z = math.sqrt(max(0.0, 1 - nx * nx - ny * ny))
    l = -0.5 * nx - 0.55 * ny + 0.62 * z
    return '4' if l > 1.0 else '3' if l > 0.7 else '2' if l > 0.36 else '1'

def shell(open_core, flick):
    g = blank(); shape = [[False] * Wd for _ in range(Hd)]
    cx, cy, rx, ry = 50.0, 56.0, 48.0, 46.0
    cut = lambda x, y: open_core and ((x - 30) / 17.0) ** 2 + ((y - 26) / 10.0) ** 2 <= 1
    for y in range(8, 58):
        for x in range(Wd):
            nx, ny = (x - cx) / rx, (y - cy) / ry
            if nx * nx + ny * ny <= 1 and y <= 57:
                shape[y][x] = True
                g[y][x] = shade(x, y, cx, cy, rx, ry)
    for sx in (18, 32, 46, 60, 74):   # plate seams curving with the dome
        for y in range(10, 57):
            for x in range(Wd):
                if shape[y][x] and abs(x - (sx - 0.22 * (cy - y) + 0.0)) < 0.6:
                    g[y][x] = '1'
                    if x > 0 and g[y][x - 1] in '23': g[y][x - 1] = '4' if g[y][x - 1] == '3' else '3'
    for y in range(8, 40):            # moss on the lit crown
        for x in range(Wd):
            if shape[y][x] and y < 8 + 20 * (1 - abs((x - 44) / 44.0)) and math.sin(x * 0.55) + math.cos(y * 0.8) > 0.95:
                g[y][x] = 'F' if (x + y) % 7 == 0 else 'D' if (x * y) % 3 else 'C'
    for y in range(57, 62):           # belly shadow band
        for x in range(10, 90):
            if abs(x - 50) <= 42 - (y - 57) * 3: g[y][x] = '1'; shape[y][x] = True
    if open_core:
        for y in range(Hd):
            for x in range(Wd):
                if cut(x, y) and shape[y][x]:
                    d = ((x - 30) / 17.0) ** 2 + ((y - 26) / 10.0) ** 2
                    g[y][x] = ('h' if flick else 'E') if d < 0.16 else 'E' if d < 0.38 else 'e' if d < 0.62 else 'g' if d < 0.86 else 'o'
        for k in range(-8, 9, 4):      # raised plate teeth around the opening
            for t in range(5):
                put(g, 30 + k * 2 - t // 2, 14 - t, '4' if t < 3 else '3'); put(g, 31 + k * 2 + t // 2, 14 - t, '2'); shape[14 - t][30 + k * 2] = True
    for k in range(7):                 # crown spines along the shell's top edge
        sx = 22 + k * 10; top = 8 + int(14 * (abs(sx - 50) / 48.0) ** 2) - 3
        for t in range(7):
            for dx in (0, 1):
                put(g, sx + dx, top - t + 4, '4' if dx == 0 else '2'); shape[max(0, top - t + 4)][sx + dx] = True
    return g, shape

def head(g, shape, glow, dip):
    hx, hy = 98.0, 54.0 + dip
    for y in range(Hd):
        for x in range(Wd):
            nx, ny = (x - hx) / 18.0, (y - hy) / 14.0
            if nx * nx + ny * ny <= 1 and x > 84:
                g[y][x] = shade(x, y, hx, hy, 18.0, 14.0); shape[y][x] = True
    ey = int(hy) - 6
    for k in range(13):                # long glowing eye slit, slanting down toward the snout
        x = 96 + k; y = ey + k // 3
        for (dy, c) in ((0, 'Y'), (1, 'w' if glow else 'y'), (2, 'o')):
            put(g, x, y + dy, c)
    for k in range(16):                # heavy brow ridge
        put(g, 92 + k, ey - 2 + k // 4, 'o'); put(g, 92 + k, ey - 3 + k // 4, '1')
    for (bx, by, sgn) in ((104, int(hy) + 8, 1), (106, int(hy) + 12, -1)):   # curved pincers
        for k in range(18):
            ang = k / 17.0
            x = int(bx + 4 + 14 * ang); y = int(by + sgn * (-3 + 14 * ang * ang)) if sgn > 0 else int(by + 14 * ang - 3 * ang * 6 + 0)
            for t in range(3): put(g, x, y + t, 'y' if t == 0 else 'k' if t == 1 else 'o'); 
            shape[min(Hd - 1, max(0, y))][min(Wd - 1, x)] = True
    for k in range(4):                 # cheek spikes
        for t in range(4 - k): put(g, 90 + k, int(hy) + 6 + t + k * 2, '4'); 
    line(g, 100, int(hy) - 14, 108, int(hy) - 28 + dip, 'o', 2); line(g, 108, int(hy) - 28 + dip, 116, int(hy) - 30 + dip, 'o', 2)

def legs(g, phase, front_slam=False):
    sw = [(-6, 0, 6, 0), (0, 0, 0, 0), (6, 0, -6, 0), (0, 0, 0, 0)][phase]
    lift = [(0, 4, 0, 0), (0, 0, 0, 0), (4, 0, 0, 4), (0, 0, 0, 0)][phase]
    for n, hx in enumerate((24, 44, 66, 84)):
        fx = hx + 7 + sw[n]; fy = 77 - lift[n]
        kx, ky = hx + 14, 68 - lift[n] // 2
        line(g, hx, 58, kx, ky, 'o', 6); line(g, kx, ky, fx, fy, 'o', 5)
        line(g, hx, 58, kx, ky - 1, '2', 3); line(g, kx - 1, ky, fx, fy - 1, '2', 2)
        line(g, hx - 1, 57, kx - 1, ky - 2, '3', 1)
        for k in range(-4, 5): put(g, fx + k + 3, min(Hd - 1, fy + 2), 'o'); put(g, fx + k + 3, min(Hd - 1, fy + 1), '1')
        put(g, kx, ky - 3, '4'); put(g, kx + 1, ky - 4, '4')

def outline(g, shape):
    out = [r[:] for r in g]
    for y in range(Hd):
        for x in range(Wd):
            if shape[y][x] and g[y][x] not in 'owyYkE' :
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    xx, yy = x + dx, y + dy
                    if not (0 <= xx < Wd and 0 <= yy < Hd) or not (shape[yy][xx] or g[yy][xx] != '.'):
                        out[y][x] = 'o'; break
    return out

def frame(phase=1, open_core=False, flick=False, glow=False, dip=0, rear=0):
    g, shape = shell(open_core, flick)
    lg = blank(); legs(lg, phase)
    for y in range(Hd):
        for x in range(Wd):
            if lg[y][x] != '.' and g[y][x] == '.': g[y][x] = lg[y][x]
    head(g, shape, glow, dip)
    g = outline(g, shape)
    if rear:   # rear up: the whole sprite shifts up / tilts back by moving rows
        g = [['.'] * Wd for _ in range(rear)] + g[:Hd - rear]
    return [''.join(r) for r in g]

if __name__ == '__main__':
    out = {'walk': [frame(p) for p in range(4)], 'rear': frame(1, rear=6, dip=-4), 'tele': [frame(1, glow=True, dip=4), frame(1, glow=False, dip=4)], 'charge': [frame(0, glow=True, dip=6), frame(2, glow=True, dip=6)], 'stun': [frame(1, True, False), frame(1, True, True)]}
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'js', 'art', 'boss1.js')
    src = "/* GENERATED by tools/boss_gen.py: the Mossback Warden, zone 1 boss (124x80 frames, facing right). */\n(function (G) {\n  G.art = G.art || {};\n  G.art.boss1 = " + json.dumps(out, separators=(',', ':')) + ";\n})((window.SGS = window.SGS || {}));\n"
    open(path, 'w', encoding='utf-8').write(src)
    print('wrote', len(src))
