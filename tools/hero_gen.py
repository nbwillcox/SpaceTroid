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
def body(): return part(27, HEAD + BACKPACK + TORSO + PAULDRON + ARM)

LEGS_IDLE = [
    (0, 9, "o43322111o"),
    (1, 8, "o211o"), (1, 11, "o4321o"),
    (2, 8, "o211o"), (2, 11, "o4321o"),
    (3, 8, "o211o"), (3, 11, "o3221o"),
    (4, 8, "okko"), (4, 11, "o3yYko"),
    (5, 8, "o1ko"), (5, 11, "o2kyo"),
    (6, 8, "o211o"), (6, 11, "o4321o"),
    (7, 8, "o211o"), (7, 11, "o4321o"),
    (8, 8, "o211o"), (8, 11, "o3221o"),
    (9, 8, "okko"), (9, 11, "oyYyko"),
    (10, 8, "o211o"), (10, 11, "o3221o"),
    (11, 8, "o2211o"), (11, 11, "o43221o"),
    (12, 8, "o22111o"), (12, 11, "o432211o"),
    (13, 8, "o3221111o"), (13, 11, "o43221111o"),
    (14, 8, "o43221111o"), (14, 11, "oyYy221111o"),
    (15, 8, "oLLl1111oo"), (15, 11, "oLLLl1111oo"),
    (16, 8, "oooooooooooo"),
]
if __name__ == '__main__':
    out = {'body': body(), 'legsIdle': part(18, LEGS_IDLE)}
    full = body() + part(18, LEGS_IDLE)
    out['idle'] = full
    for k, v in out.items():
        for i, r in enumerate(v):
            if len(r) != W: print('BAD', k, i, len(r))
    open(__import__('os').path.join(__import__('os').path.dirname(__file__), '..', 'js', 'art', 'hero.js'), 'w').write("/* generated from _hero_gen.py (hand-authored parts) */\n(function (G) { 'use strict'; G.art = G.art || {}; G.art.heroParts = " + json.dumps({'idle': out['idle']}) + "; })((window.SGS = window.SGS || {}));\n")
    print('ok')
