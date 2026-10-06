"""Moss caps, edge overlays and autotile composition (mask bits N=1 E=2 S=4 W=8 = side exposed to air)."""
from tile_gen1 import W, grid, put, fill_tile

# moss cap: first row of moss and depth per column (0 start = blade row), hand-set per variant
CAP = {
    0: dict(s=[0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0], d=[4, 5, 5, 4, 3, 4, 6, 7, 5, 4, 3, 4, 5, 6, 5, 4]),
    1: dict(s=[0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0], d=[5, 4, 3, 4, 6, 7, 5, 4, 4, 5, 6, 5, 3, 4, 5, 6]),
    2: dict(s=[0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0], d=[3, 4, 5, 5, 6, 4, 3, 4, 5, 7, 6, 4, 4, 5, 4, 3]),
}

def moss_cap(g, v):
    c = CAP[v]
    for x in range(W):
        s, d = c['s'][x], c['d'][x]
        for y in range(s, d):
            if y == s:
                col = 'F' if x % 4 == 1 else 'E'
            elif y == s + 1:
                col = 'D'
            elif y == d - 1:
                col = 'B'
            else:
                col = 'C' if (x + y) % 2 else 'D'
            g[y][x] = col
        if s:
            g[0][x] = '.'
        if d < W and g[d][x] in '1234':
            g[d][x] = '1'
        # warm rim-light on the left-facing slope of each tuft
        if x > 0 and c['d'][x - 1] < d and d > 4:
            put(g, x, s + 1, 'E')

def edge_bottom(g, v):
    for x in range(W):
        g[15][x] = '0'
        if g[14][x] not in 'BC':
            g[14][x] = '1'
    for x in ([2, 9, 13] if v == 0 else [4, 11] if v == 1 else [1, 7, 14]):
        put(g, x, 14, 'B'); put(g, x, 15, 'B')

def edge_left(g, y0):
    for y in range(y0, W):
        if g[y][0] != '.':
            g[y][0] = '2'
        if g[y][1] in '3':
            g[y][1] = '4'

def edge_right(g, y0):
    for y in range(y0, W):
        if g[y][15] != '.':
            g[y][15] = '0'
        if g[y][14] in '234':
            g[y][14] = '1'

def tile(v, mask, diag=0):
    g = fill_tile(v)
    N, E, S, Wd = mask & 1, mask & 2, mask & 4, mask & 8
    if N:
        moss_cap(g, v)
    depth = CAP[v]['d']
    if S:
        edge_bottom(g, v)
    if Wd:
        edge_left(g, depth[0] if N else 0)
    if E:
        edge_right(g, depth[15] if N else 0)
    if N and Wd:
        g[0][0] = '.'
        put(g, 0, 1, '2' if g[1][0] != '.' else '.')
    if N and E:
        g[0][15] = '.'
    if S and Wd:
        g[15][0] = '.'; put(g, 1, 15, '0')
    if S and E:
        g[15][15] = '.'; put(g, 14, 15, '0')
    if not mask:  # inner corner chips where only a diagonal neighbour is open
        if diag & 1: put(g, 0, 0, '0'); put(g, 1, 0, '1'); put(g, 0, 1, '1')
        if diag & 2: put(g, 15, 0, '0'); put(g, 14, 0, '1'); put(g, 15, 1, '1')
        if diag & 4: put(g, 15, 15, '0'); put(g, 14, 15, '1'); put(g, 15, 14, '1')
        if diag & 8: put(g, 0, 15, '0'); put(g, 1, 15, '1'); put(g, 0, 14, '1')
    return [''.join(r) for r in g]
