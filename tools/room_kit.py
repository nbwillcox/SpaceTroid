r"""Shared room authoring kit: the Room grid class (tiles, platforms, ramps, doors, spawns, items) plus a terrain kit that carves organic caves from solid rock."""
BS = chr(92)

class Room:
    def __init__(s, rid, name, w, h, mx, my, wall_all=False, solid=False):
        s.id, s.name, s.w, s.h, s.mx, s.my = rid, name, w, h, mx, my
        s.g = [['.'] * w for _ in range(h)]
        s.doors, s.items, s.stations, s.decor = [], [], [], []
        s.zone = 1
        s.movers = []
        s.pressure = False
        s.fill(0, 0, w - 1, 1, '#'); s.fill(0, h - 2, w - 1, h - 1, '#'); s.fill(0, 0, 0, h - 1, '#'); s.fill(w - 1, 0, w - 1, h - 1, '#')
        s.wall_all = wall_all
        if solid: s.fill(0, 0, w - 1, h - 1, '#')
    def fill(s, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if 0 <= y < s.h and 0 <= x < s.w: s.g[y][x] = c
    def plat(s, x0, x1, y, c='='): s.fill(x0, y, x1, y, c)
    def ramp(s, x0, F, n, rising=True):
        for i in range(n):
            if rising:
                s.g[F - 1 - i][x0 + i] = '/'; s.fill(x0 + i, F - i, x0 + i, F - 1, '#')
            else:
                s.g[F - n + i][x0 + i] = BS; s.fill(x0 + i, F - n + i + 1, x0 + i, F - 1, '#')
    def door(s, did, side, ty, color, to, tdoor, h=3):
        x = 0 if side == 'L' else s.w - 1
        s.fill(x, ty, x, ty + h - 1, '.')
        s.doors.append({'id': did, 'side': side, 'ty': ty, 'color': color, 'to': to, 'door': tdoor, 'h': h})
    def spawn(s, ch, x, y): s.g[y][x] = ch
    def mover(s, axis, a, b, w, speed, fixed): s.movers.append({'axis': axis, 'a': a, 'b': b, 'w': w, 'speed': speed, 'x' if axis == 'y' else 'y': fixed})
    def wall(s, x0, y0, x1, y1, ragged=True):
        import math
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if ragged:   # crumbled, uneven edges so the back wall does not read as a rectangle
                    ex = 0 if x0 <= 1 or x1 >= s.w - 2 else 1
                    dl = int(2.4 * abs(math.sin(y * 1.3 + x0))) * (1 if x0 > 1 else 0); dr = int(2.4 * abs(math.sin(y * 0.9 + x1))) * (1 if x1 < s.w - 2 else 0)
                    dt = int(2.0 * abs(math.sin(x * 1.1 + y0))) * (1 if y0 > 2 else 0); db = int(2.0 * abs(math.sin(x * 0.7 + y1))) * (1 if y1 < s.h - 3 else 0)
                    if x < x0 + dl or x > x1 - dr or y < y0 + dt or y > y1 - db: continue
                if s.g[y][x] == '.': s.g[y][x] = 'w'
    def item(s, iid, typ, tx, ty): s.items.append({'id': iid, 'type': typ, 'tx': tx, 'ty': ty})
    def station(s, typ, tx, ty, to=None):
        d = {'type': typ, 'tx': tx, 'ty': ty}
        if to: d['to'] = to
        s.stations.append(d)
    def emit(s):
        s.check()
        if s.wall_all: s.wall(1, 2, s.w - 2, s.h - 3, ragged=False)
        rows = [''.join(r) for r in s.g]
        d = {'id': s.id, 'name': s.name, 'zone': s.zone, 'mx': s.mx, 'my': s.my, 'map': rows, 'doors': s.doors, 'items': s.items, 'stations': s.stations, 'decor': s.decor, 'movers': s.movers, 'pressure': s.pressure}
        return d
    # ---- terrain kit: carve organic caves from solid rock (floor and ceiling profiles) ----
    def cave(s, floor, ceil=None, surf='#', y0=0, y1=None):
        """floor / ceil: knot lists [(x, row)] or [(x, row, 's')] ('s' forces a vertical step). floor row = the surface cell row (hero stands on its top edge);
        ceil row = first open row. Level changes up to 3 rows get 45-degree ramps ending at the knot x. Call before placing platforms, doors, spawns.
        y0..y1 limits the carve to a band of rows (a second cave() below the first makes a two-level room); a floor row below y1 leaves the band open underneath."""
        w, h = s.w, s.h
        y1 = h - 1 if y1 is None else y1
        fr, fk = s._profile(floor, True)
        cl, _ = s._profile(ceil or [(0, y0 + 2)], False)
        s.fr, s.fk, s.cl = fr, fk, cl
        for x in range(w):
            for y in range(y0, y1 + 1):
                if y < cl[x]: s.g[y][x] = '#'
                elif y < fr[x]: s.g[y][x] = '.'
                elif y == fr[x]: s.g[y][x] = fk[x] if fk[x] != '#' else surf
                else: s.g[y][x] = '#'
        for y in range(y0, y1 + 1): s.g[y][0] = '#'; s.g[y][w - 1] = '#'
        return (fr, fk, cl)
    def use(s, b): s.fr, s.fk, s.cl = b
    def _profile(s, knots, ramps):
        w = s.w; ks = sorted(knots, key=lambda k: k[0]); lvl = [ks[0][1]] * w; kind = [None] * w
        for i in range(1, len(ks)):
            a, b = ks[i - 1], ks[i]; bx, d = b[0], b[1] - a[1]
            step = len(b) > 2 and b[2] == 's'
            n = abs(d)
            if ramps and not step and 0 < n <= 3 and bx - n > a[0]:
                for x in range(a[0], bx - n): lvl[x] = a[1]
                for j in range(n):
                    x = bx - n + j
                    if d < 0: lvl[x] = a[1] - 1 - j; kind[x] = '/'
                    else: lvl[x] = a[1] + j; kind[x] = BS
                for x in range(bx, w): lvl[x] = b[1]
            else:
                for x in range(a[0], bx): lvl[x] = a[1]
                for x in range(bx, w): lvl[x] = b[1]
        return lvl, [k or '#' for k in kind]
    def ground(s, x): return s.fr[x]
    def on(s, ch, x, dy=0): s.g[s.fr[x] - 1 + dy][x] = ch                      # spawn marker standing on the floor at column x
    def hang(s, x, n, wd=1):
        for xx in range(x, x + wd):
            for y in range(s.cl[xx], s.cl[xx] + n): s.g[y][xx] = '#'
    def block(s, x0, x1, top, c='#'):                                          # solid slab from row top down to the floor
        for x in range(x0, x1 + 1): s.fill(x, top, x, s.fr[x] - 1, c)
    def pool(s, x0, x1, c='L', depth=1):
        """sink the floor under x0..x1 by depth rows and fill that dip with hazard c (lava L / water W)"""
        for x in range(x0, x1 + 1):
            t = s.fr[x]
            for y in range(t, t + depth): s.g[y][x] = c
            s.fr[x] = t
    def back(s, mode='full', *a):
        if mode == 'full': s.wall(1, 2, s.w - 2, s.h - 3, ragged=False)
        elif mode == 'ragged': s.wall(*a)
    def check(s):
        for d in s.doors:
            x = 0 if d['side'] == 'L' else s.w - 1; xi = 1 if d['side'] == 'L' else s.w - 2
            for y in range(d['ty'], d['ty'] + d['h']):
                assert s.g[y][xi] in '.wSW', (s.id, d['id'], 'door vestibule blocked at', xi, y, s.g[y][xi])
            assert s.g[d['ty'] + d['h']][xi] in '#=ibBMD', (s.id, d['id'], 'no floor under door', s.g[d['ty'] + d['h']][xi])
    def show(s):
        print(s.id, s.w, 'x', s.h); print('\n'.join(''.join(r) for r in s.g))
    def surf(s, x0, x1, c='i'):
        """re-skin the floor surface cells (flat ones only) of x0..x1, e.g. 'i' for slippery ice"""
        for x in range(x0, x1 + 1):
            if s.fk[x] == '#' and s.g[s.fr[x]][x] == '#': s.g[s.fr[x]][x] = c
    def top(s, x, c, dy=1):                                                       # marker at the first open row under the ceiling (icicles etc.)
        s.g[s.cl[x] + dy - 1][x] = c
    def flood(s, x0, x1, top, c='W'):
        for x in range(x0, x1 + 1):
            for y in range(top, s.fr[x]):
                if s.g[y][x] in '.w': s.g[y][x] = c
    def stair(s, hx0, hx1, fr):
        """ledges that climb from a cavern floor (row fr) back up through a gap in the floor above at hx0..hx1"""
        for (x0, x1, y) in [(hx0 - 5, hx0 - 1, fr - 3), (hx0, hx0 + 4, fr - 6), (hx0 - 5, hx0 - 1, fr - 9), (hx0, hx0 + 4, fr - 12), (hx0, hx1, fr - 14)]: s.plat(x0, x1, y)

def layout_report(rooms):
    """Check that door-linked rooms sit where their doors say (east door of A meets the west door of B, door rows aligned across 30x17 cells) and that no two rooms
    share a map cell. Returns a list of problems (empty = consistent); positions come from each room's own mx, my."""
    byid = {r.id: r for r in rooms}
    cw = lambda r: -(-r.w // 30)
    bad = []
    for a in rooms:
        for d in a.doors:
            b = byid.get(d['to'])
            if not b: continue
            td = next(q for q in b.doors if q['id'] == d['door'])
            bx = a.mx + cw(a) if d['side'] == 'R' else a.mx - cw(b)
            by = a.my + d['ty'] // 17 - td['ty'] // 17
            if (bx, by) != (b.mx, b.my): bad.append('%s.%s -> %s.%s: wants %s but placed %s' % (a.id, d['id'], b.id, td['id'], (bx, by), (b.mx, b.my)))
    seen = {}
    for r in rooms:
        for cx in range(cw(r)):
            for cy in range(-(-r.h // 17)):
                k = (r.mx + cx, r.my + cy)
                if k in seen: bad.append('overlap %s %s at %s' % (r.id, seen[k], k))
                seen[k] = r.id
    return bad
