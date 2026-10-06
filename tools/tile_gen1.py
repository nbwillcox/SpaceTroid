"""Zone 1 (Crash Site) tile authoring helpers: 16x16 hand-specified masonry, moss caps and edge overlays."""
import random
W = 16

def grid(fill='.'):
    return [[fill] * W for _ in range(W)]

def put(g, x, y, c):
    if 0 <= x < W and 0 <= y < W:
        g[y][x] = c

def block(g, x0, y0, w, h):
    """one ashlar block, w x h including a 1px mortar column/row on its right/bottom; x wraps so courses tile."""
    for yy in range(h):
        for xx in range(w):
            x = (x0 + xx) % W
            y = y0 + yy
            if y >= W:
                continue
            fw, fh = w - 1, h - 1
            if xx == fw or yy == fh:
                c = '1'
            elif yy == 0 and xx == 0:
                c = '5'
            elif yy == 0:
                c = '4'
            elif xx == 0:
                c = '4'
            elif yy == fh - 1 or xx == fw - 1:
                c = '2'
            else:
                c = '3'
            g[y][x] = c

LAYOUTS = {
    0: [(0, 0, 10, 8), (10, 0, 6, 8), (5, 8, 8, 8), (13, 8, 8, 8)],
    1: [(0, 0, 6, 8), (6, 0, 10, 8), (3, 8, 8, 8), (11, 8, 8, 8)],
    2: [(0, 0, 16, 8), (8, 8, 8, 8), (0, 8, 8, 8)],
}
# hand-placed texture per variant: dark speckles, light speckles, cracks, damp stains (moss-coloured)
TEX = {
    0: dict(dk=[(3, 3), (7, 2), (13, 4), (2, 6), (8, 11), (14, 13), (4, 14), (11, 10)],
            lt=[(5, 2), (12, 2), (7, 5), (1, 10), (9, 9), (15, 12), (6, 13)],
            crack=[(11, 11), (11, 12), (12, 12), (12, 13), (13, 13), (13, 14)],
            stain=[(2, 7, 'B'), (3, 7, 'C'), (4, 7, 'B'), (3, 6, 'B'), (7, 14, 'B'), (8, 14, 'C')]),
    1: dict(dk=[(2, 4), (9, 3), (14, 2), (4, 6), (6, 10), (12, 12), (1, 13), (10, 14)],
            lt=[(3, 2), (8, 5), (13, 5), (5, 11), (9, 13), (14, 9)],
            crack=[(8, 1), (8, 2), (7, 2), (7, 3), (6, 3), (6, 4), (6, 5)],
            stain=[(12, 7, 'B'), (13, 7, 'C'), (14, 7, 'B'), (13, 6, 'B'), (1, 15, 'B')]),
    2: dict(dk=[(4, 3), (11, 4), (2, 5), (14, 6), (5, 12), (10, 11), (13, 14)],
            lt=[(6, 2), (9, 6), (2, 10), (12, 10), (7, 14)],
            crack=[(10, 9), (10, 10), (11, 10), (11, 11), (11, 12), (12, 12)],
            stain=[(6, 7, 'B'), (7, 7, 'C'), (8, 7, 'B'), (7, 6, 'B'), (1, 14, 'B'), (2, 14, 'C')]),
}

def fill_tile(v):
    g = grid('1')
    for (x0, y0, w, h) in LAYOUTS[v]:
        block(g, x0, y0, w, h)
    t = TEX[v]
    for (x, y) in t['dk']:
        if g[y][x] == '3':
            g[y][x] = '2'
    for (x, y) in t['lt']:
        if g[y][x] in '23':
            g[y][x] = '4'
    for (x, y) in t['crack']:
        g[y][x] = '1'
    for (x, y, c) in t['stain']:
        put(g, x, y, c)
    return g
