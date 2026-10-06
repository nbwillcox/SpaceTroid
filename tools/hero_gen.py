# Hand-authored hero sprite parts, drawn with row spans: R(y, x, "letters"); '.' stays transparent. Light comes from the upper left.
import json
W = 28
def blank(h): return [['.'] * W for _ in range(h)]
def put(g, y, x, s):
    for i, c in enumerate(s):
        if c != '.' and 0 <= y < len(g) and 0 <= x + i < W: g[y][x + i] = c
def fin(g): return [''.join(r) for r in g]
def part(h, rows):
    g = blank(h)
    for (y, x, s) in rows: put(g, y, x, s)
    return fin(g)

HEAD = [
    (0, 10, "oooooo"),
    (1, 9, "o34444422o"),
    (2, 8, "o444444332oo"),
    (3, 7, "o44444333221o"),
    (4, 6, "o444443332oooooo"),
    (5, 6, "o44443332ovWWVxo".replace('ovWWVxo', 'oVWWvxo')),
    (6, 6, "o44433322ovVVvxo"),
    (7, 7, "o3332221ooxxxo"),
    (8, 8, "o22211111yyo"),
    (9, 9, "oo1111yyyo"),
    (10, 11, "ooUUUoo"),
]
BACKPACK = [
    (12, 5, "oooo"), (13, 4, "o3332o"), (14, 4, "o4432o"), (15, 4, "o3kyyo"), (16, 4, "o2kyYo"), (17, 4, "o21YYo"), (18, 4, "o2111o"), (19, 5, "oooo"),
]
TORSO = [
    (11, 8, "oooooooooo"),
    (12, 7, "o444433332221o"),
    (13, 7, "o44433322211oo"),
    (14, 7, "o4433322211o"),
    (15, 7, "o433222111oo"),
    (16, 8, "o3322211110o"),
    (17, 8, "o2221111oo"),
    (18, 9, "o2221111o"),
    (19, 9, "o2211kk1o"),
    (20, 9, "o1211kyko"),
    (21, 9, "o11111111o"),
    (22, 8, "ooooooooooo"),
    (23, 8, "oyYwYyYkyyo"),
    (24, 8, "ooooooooooo"),
    (25, 8, "o3221111Uo"),
    (26, 9, "o22111Uo"),
]
PAULDRON = [
    (10, 9, "ooooooo"), (11, 8, "o44444333o"), (12, 8, "o4443332221o"), (13, 8, "o443322211o"), (14, 9, "o32221111o"), (15, 10, "o2211kko"), (16, 11, "oo11oo"),
]
ARM = [
    (15, 14, "oooooooo"), (16, 14, "o4333222o"), (17, 13, "oo3322111oooooooo"), (18, 13, "o1211kkymmlllLLLo"), (19, 13, "o11kyYMmlLLLLLLo"), (20, 14, "ooooMmmllllllo"), (21, 20, "ooooooooo"),
    (18, 24, "oEh"), (19, 24, "oEh"),
]
def body(): return part(25, HEAD + BACKPACK + TORSO + PAULDRON + ARM)


# ---- legs: hand-posed limbs. Each limb is a thigh + shin (thick lines between keypoints) with a gold knee pad and a hand-drawn boot stamp; an outline pass closes them. ----
def line_pts(p0, p1):
    (x0, y0), (x1, y1) = p0, p1; n = max(abs(x1 - x0), abs(y1 - y0), 1)
    return [(round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n)) for i in range(n + 1)]
BOOT_F = [".....", "....."]  # placeholder (boot is drawn by boot())
def limb(g, hip, knee, ankle, front):
    ramp = ('4', '3', '2', '1') if front else ('3', '2', '1', '1')
    def thick(p0, p1, w):
        for (x, y) in line_pts(p0, p1):
            for k in range(w):
                xx = x - w // 2 + k
                c = ramp[0] if k == 0 else ramp[1] if k == 1 else ramp[2] if k < w - 1 else ramp[3]
                if 0 <= y < len(g) and 0 <= xx < W: g[y][xx] = c
    thick(hip, knee, 5); thick(knee, ankle, 4)
    kx, ky = knee
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if 0 <= ky + dy < len(g) and 0 <= kx + dx < W: g[ky + dy][kx + dx] = 'y' if (dx + dy) < 1 else 'k'
    g[ky][kx] = 'Y'
    # boot: heel at ankle, toe forward (right)
    ax, ay = ankle
    boot = ["33221", "3222111", "yY222111", "LLl11111"] if front else ["2211", "221111", "yy211111", "ml111111"]
    for j, row in enumerate(boot):
        for i, c in enumerate(row):
            xx, yy = ax - 2 + i, ay - 1 + j
            if 0 <= yy < len(g) and 0 <= xx < W: g[yy][xx] = c
def outline(g):
    h = len(g); out = [r[:] for r in g]
    for y in range(h):
        for x in range(W):
            if g[y][x] == '.':
                for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
                    xx, yy = x + dx, y + dy
                    if 0 <= xx < W and 0 <= yy < h and g[yy][xx] not in '.o': out[y][x] = 'o'; break
    return out
HIP = [(8, 0, "o43322111o")]
def legs(pose):
    g = blank(20)
    (bk, ft) = pose
    sh = lambda p: (p[0], p[1] + 2)
    limb(g, (11, 4), sh(bk[0]), sh(bk[1]), False); limb(g, (13, 4), sh(ft[0]), sh(ft[1]), True)
    g = outline(g)
    put(g, 0, 8, "o4332221111o"); put(g, 1, 8, "o3222111111o"); put(g, 2, 9, "o22111111o")
    return fin(g)
RUN = [
    (((8, 9), (5, 14)), ((15, 8), (17, 15))),    # contact
    (((9, 10), (7, 12)), ((15, 9), (14, 15))),   # down
    (((14, 8), (11, 11)), ((13, 9), (12, 15))),  # passing
    (((16, 8), (16, 12)), ((11, 9), (9, 15))),   # up
]
IDLE_LEGS = (((10, 9), (9, 15)), ((13, 9), (13, 15)))
JUMP_LEGS = (((14, 8), (11, 13)), ((16, 7), (17, 12)))
FALL_LEGS = (((11, 9), (9, 15)), ((14, 9), (15, 15)))
def swap(pose): return (pose[1], pose[0])
def compose(top, lg, dy=0):
    g = [list(r) for r in (['.' * W] * 25 + lg)]
    for y, r in enumerate(top):
        yy = y + dy
        if 0 <= yy < len(g):
            for x, c in enumerate(r):
                if c != '.': g[yy][x] = c
    return [''.join(r) for r in g]
if __name__ == '__main__':
    top = body()
    frames = {'idle': compose(top, legs(IDLE_LEGS)), 'jump': compose(top, legs(JUMP_LEGS), -1), 'fall': compose(top, legs(FALL_LEGS))}
    bob = [0, 1, 0, -1]
    for i in range(4): frames['run%d' % i] = compose(top, legs(RUN[i]), bob[i])
    for i in range(4): frames['run%d' % (i + 4)] = compose(top, legs(swap(RUN[i])), bob[i])
    for k, v in frames.items():
        for i, r in enumerate(v):
            if len(r) != W: print('BAD', k, i, len(r))
    import os
    open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'js', 'art', 'hero.js'), 'w').write("/* generated from tools/hero_gen.py (hand-authored parts) */\n(function (G) { 'use strict'; G.art = G.art || {}; G.art.heroParts = " + json.dumps(frames) + "; })((window.SGS = window.SGS || {}));\n")
    print('ok', len(frames))
