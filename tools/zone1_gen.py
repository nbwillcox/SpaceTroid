r"""Zone 1 (Crash Site): hand-built room layouts -> js/rooms/zone1.js. Tile letters: # solid, = ledge, / \ slopes, b shot block, B bomb block, M missile block, ^ spikes, w backdrop wall;
spawns: P start, c crawler, m moth, o pod (the marker's tile row is the row whose bottom edge is the feet)."""
import json, os
BS = chr(92)

class Room:
    def __init__(s, rid, name, w, h, mx, my, wall_all=False):
        s.id, s.name, s.w, s.h, s.mx, s.my = rid, name, w, h, mx, my
        s.g = [['.'] * w for _ in range(h)]
        s.doors, s.items, s.stations, s.decor = [], [], [], []
        s.fill(0, 0, w - 1, 1, '#'); s.fill(0, h - 2, w - 1, h - 1, '#'); s.fill(0, 0, 0, h - 1, '#'); s.fill(w - 1, 0, w - 1, h - 1, '#')
        s.wall_all = wall_all
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
    def station(s, typ, tx, ty): s.stations.append({'type': typ, 'tx': tx, 'ty': ty})
    def emit(s):
        if s.wall_all: s.wall(1, 2, s.w - 2, s.h - 3, ragged=False)
        rows = [''.join(r) for r in s.g]
        d = {'id': s.id, 'name': s.name, 'zone': 1, 'mx': s.mx, 'my': s.my, 'map': rows, 'doors': s.doors, 'items': s.items, 'stations': s.stations, 'decor': s.decor}
        return d

ROOMS = []

def crash():
    r = Room('crash', 'Crash Site', 60, 17, 0, 1)
    r.decor.append({'kind': 'wreck', 'x': 40, 'y': 186})
    r.spawn('P', 18, 14)
    r.ramp(26, 15, 2, True); r.fill(28, 13, 33, 14, '#'); r.ramp(34, 15, 2, False)
    r.plat(22, 26, 11); r.plat(38, 43, 10); r.plat(44, 48, 7)
    r.fill(50, 13, 52, 14, '#'); r.fill(53, 14, 55, 14, '#')
    for (x, y) in [(33, 12), (46, 14)]: r.spawn('c', x, y)
    r.spawn('m', 40, 6)
    r.wall(1, 2, 8, 14)
    r.door('e', 'R', 12, 'blue', 'hall', 'w')
    return r
ROOMS.append(crash())

def hall():
    r = Room('hall', 'Overgrown Hall', 60, 17, 2, 1)
    r.door('w', 'L', 12, 'blue', 'crash', 'e'); r.door('e', 'R', 12, 'blue', 'beacon', 'w')
    r.station('map', 6, 14)
    r.fill(24, 15, 27, 15, '^')
    r.plat(22, 29, 11)
    r.ramp(12, 15, 2, True); r.fill(14, 13, 18, 14, '#'); r.ramp(19, 15, 2, False)
    r.fill(40, 12, 46, 14, '#'); r.plat(36, 38, 12); r.plat(48, 53, 10)
    r.spawn('c', 16, 12); r.spawn('c', 33, 14); r.spawn('o', 43, 11); r.spawn('m', 30, 6); r.spawn('m', 52, 8)
    r.wall(14, 2, 46, 14)
    return r
ROOMS.append(hall())

def beacon():
    r = Room('beacon', 'Beacon Room', 20, 17, 4, 1, wall_all=True)
    r.door('w', 'L', 12, 'blue', 'hall', 'e'); r.door('e', 'R', 12, 'blue', 'shaft', 'wl')
    r.station('save', 10, 14)
    r.fill(5, 12, 7, 12, '#'); r.fill(13, 12, 15, 12, '#')
    return r
ROOMS.append(beacon())

def shaft():
    r = Room('shaft', 'Collapsed Shaft', 30, 34, 5, 0, wall_all=True)
    r.door('wl', 'L', 29, 'blue', 'beacon', 'e'); r.door('el', 'R', 29, 'blue', 'cellar', 'w'); r.door('eh', 'R', 5, 'blue', 'ruins', 'w')
    for (x0, x1, y) in [(4, 8, 29), (10, 14, 26), (16, 20, 23), (22, 26, 20), (16, 20, 17), (10, 14, 14), (4, 8, 11)]: r.plat(x0, x1, y)
    r.fill(10, 8, 28, 8, '#')
    r.fill(27, 18, 28, 18, '#'); r.fill(27, 20, 28, 20, '#'); r.g[19][27] = 'b'   # a ball-sized nook sealed by one shot block (crouch to shoot it)
    r.item('tank1', 'energyTank', 28, 19)
    r.spawn('m', 14, 18); r.spawn('m', 8, 8); r.spawn('c', 20, 31); r.spawn('c', 12, 31)
    return r
ROOMS.append(shaft())

def cellar():
    r = Room('cellar', 'Root Cellar', 30, 17, 6, 1, wall_all=True)
    r.door('w', 'L', 12, 'blue', 'shaft', 'el'); r.door('e', 'R', 14, 'open', 'passage', 'w', h=1)
    r.fill(24, 12, 28, 13, '#')
    r.item('morph', 'morph', 12, 14)
    r.spawn('c', 8, 14); r.spawn('m', 18, 8)
    r.fill(6, 11, 9, 11, '='); 
    return r
ROOMS.append(cellar())

def passage():
    r = Room('passage', 'Narrow Passage', 60, 17, 7, 1, wall_all=True)
    r.door('w', 'L', 14, 'open', 'cellar', 'e', h=1); r.door('e', 'R', 14, 'open', 'cache', 'w', h=1)
    r.fill(1, 2, 58, 14, '#')                                   # solid mass; the ball tunnel is carved out of it
    r.fill(1, 14, 18, 14, '.'); r.fill(17, 13, 36, 13, '.'); r.g[14][19] = '/'            # headroom starts two tiles before each ramp so the 16px ball clears the ceiling
    r.fill(20, 14, 34, 14, '#'); r.g[14][35] = BS
    r.fill(36, 14, 40, 14, '.'); r.fill(39, 13, 52, 13, '.'); r.g[14][41] = '/'
    r.fill(42, 14, 50, 14, '#'); r.g[14][51] = BS
    r.fill(52, 14, 58, 14, '.')
    r.fill(30, 11, 46, 11, '.'); r.fill(30, 12, 31, 12, 'B')           # an upper ball tunnel sealed by bomb blocks: bomb-jump up through them
    r.item('mtank2', 'missileTank', 45, 11)
    return r
ROOMS.append(passage())

def cache():
    r = Room('cache', 'Missile Cache', 30, 17, 9, 2, wall_all=True)
    r.door('w', 'L', 14, 'open', 'passage', 'e', h=1)
    r.fill(1, 12, 5, 13, '#')
    r.fill(18, 12, 24, 14, '#'); r.plat(8, 12, 11)
    r.item('missile', 'missile', 22, 11)
    r.spawn('o', 14, 14); r.spawn('m', 12, 6)
    return r
ROOMS.append(cache())

def ruins():
    r = Room('ruins', 'Upper Ruins', 60, 17, 6, 0)
    r.door('w', 'L', 12, 'blue', 'shaft', 'eh'); r.door('e', 'R', 12, 'red', 'vault', 'w')
    r.plat(8, 12, 12); r.plat(14, 18, 9); r.plat(20, 24, 6)
    r.item('mtank1', 'missileTank', 22, 5)
    r.fill(29, 12, 31, 14, '#')
    r.ramp(38, 15, 2, True); r.fill(40, 13, 46, 14, '#'); r.ramp(47, 15, 2, False)
    r.plat(33, 37, 10); r.plat(50, 54, 10)
    for (x, y) in [(15, 14), (42, 12), (34, 14)]: r.spawn('c', x, y)
    r.spawn('o', 30, 11); r.spawn('m', 22, 7); r.spawn('m', 36, 5); r.spawn('m', 52, 7)
    r.wall(18, 2, 36, 14)
    return r
ROOMS.append(ruins())

def vault():
    r = Room('vault', 'Bomb Vault', 30, 17, 8, 0, wall_all=True)
    r.door('w', 'L', 12, 'red', 'ruins', 'e'); r.door('e', 'R', 12, 'blue', 'rootfall', 'wt')
    r.fill(13, 12, 17, 14, '#')
    r.item('bombs', 'bombs', 15, 11)
    r.spawn('c', 6, 14); r.spawn('c', 24, 14); r.spawn('m', 14, 6)
    return r
ROOMS.append(vault())

def rootfall():
    r = Room('rootfall', 'Rootfall', 30, 34, 9, 0, wall_all=True)
    r.door('wt', 'L', 5, 'blue', 'vault', 'e'); r.door('el', 'R', 29, 'blue', 'cavern', 'w')
    r.fill(1, 8, 12, 8, '#'); r.fill(13, 8, 15, 9, 'B'); r.fill(16, 8, 28, 8, '#')
    r.fill(25, 5, 25, 7, 'M'); r.fill(26, 2, 28, 4, '#'); r.item('tank2', 'energyTank', 27, 7)
    for (x0, x1, y) in [(10, 17, 11), (14, 18, 14), (20, 24, 17), (14, 18, 20), (8, 12, 23), (14, 18, 26), (20, 24, 29)]: r.plat(x0, x1, y)
    r.fill(2, 31, 6, 31, '^')
    r.spawn('m', 20, 12); r.spawn('m', 10, 20); r.spawn('c', 5, 7)
    return r
ROOMS.append(rootfall())

def cavern():
    r = Room('cavern', 'Deep Cavern', 60, 17, 10, 1, wall_all=True)
    r.door('w', 'L', 12, 'blue', 'rootfall', 'el'); r.door('e', 'R', 12, 'blue', 'approach', 'w')
    r.fill(10, 15, 13, 15, '^'); r.plat(9, 14, 12)
    r.fill(18, 13, 20, 14, '#'); r.fill(26, 12, 29, 14, '#'); r.plat(22, 25, 9)
    r.fill(31, 15, 34, 15, '^')
    # pillars two tiles apart climb to a ball tunnel in a hanging slab; its mouth is sealed with bomb blocks
    r.fill(38, 13, 40, 14, '#'); r.fill(43, 11, 45, 14, '#'); r.fill(47, 9, 50, 10, '#')   # last step floats, so the floor path to the door stays open beneath it
    r.fill(51, 2, 58, 9, '#'); r.fill(51, 8, 57, 8, '.'); r.fill(51, 8, 52, 8, 'B')
    r.item('mtank3', 'missileTank', 56, 8)
    for (x, y) in [(15, 14), (23, 14), (36, 14), (41, 12)]: r.spawn('c', x, y)
    r.spawn('o', 28, 11); r.spawn('m', 18, 7); r.spawn('m', 34, 6); r.spawn('m', 46, 6)
    return r
ROOMS.append(cavern())

def approach():
    r = Room('approach', 'Warden\'s Approach', 30, 17, 12, 1, wall_all=True)
    r.door('w', 'L', 12, 'blue', 'cavern', 'e'); r.door('e', 'R', 12, 'blue', 'arena', 'w')
    r.station('save', 12, 14)
    r.fill(19, 12, 22, 12, '#')
    return r
ROOMS.append(approach())

def arena():
    r = Room('arena', 'Warden Chamber', 40, 17, 13, 1, wall_all=True)
    r.door('w', 'L', 12, 'blue', 'approach', 'e'); r.door('e', 'R', 12, 'boss', 'lift', 'w')
    r.plat(5, 9, 11); r.plat(30, 34, 11)
    r.spawn('K', 30, 14)
    return r
ROOMS.append(arena())

def lift():
    r = Room('lift', 'Lift Shaft', 30, 17, 15, 1, wall_all=True)
    r.door('w', 'L', 12, 'blue', 'arena', 'e')
    r.item('charge', 'charge', 10, 14)
    r.station('lift', 22, 14)
    return r
ROOMS.append(lift())

if __name__ == '__main__':
    out = {}
    for r in ROOMS:
        d = r.emit(); out[d['id']] = d
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'js', 'rooms', 'zone1.js')
    src = "/* GENERATED by tools/zone1_gen.py: zone 1 room layouts, doors, items and stations. */\n(function (G) {\n  G.rooms = G.rooms || {};\n  Object.assign(G.rooms, " + json.dumps(out, separators=(',', ':')) + ");\n})((window.SGS = window.SGS || {}));\n"
    open(path, 'w', encoding='utf-8').write(src)
    print('wrote', len(src), 'rooms', len(out))
