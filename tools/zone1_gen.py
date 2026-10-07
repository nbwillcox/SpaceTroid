r"""Zone 1 (Crash Site): hand-built room layouts -> js/rooms/zone1.js. Tile letters: # solid, = ledge, / \ slopes, b shot block, B bomb block, M missile block, ^ spikes, w backdrop wall;
spawns: P start, c crawler, m moth, o pod (the marker's tile row is the row whose bottom edge is the feet)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from room_kit import Room, BS

ROOMS = []

def crash():
    r = Room('crash', 'Crash Site', 60, 17, 0, 1, solid=True)
    r.cave([(0, 12), (14, 15), (34, 12), (38, 10), (50, 12)], [(0, 2), (36, 4), (47, 2)])
    r.decor.append({'kind': 'wreck', 'x': 40, 'y': 138})
    r.spawn('P', 10, 11)
    r.hang(14, 2, 3); r.hang(15, 1, 1); r.hang(24, 2, 2); r.hang(40, 2, 3); r.hang(44, 1, 2)
    r.plat(19, 23, 11); r.plat(26, 30, 8); r.plat(44, 48, 6)
    r.on('c', 19); r.on('c', 28); r.on('c', 42); r.spawn('m', 40, 5)
    r.wall(1, 2, 12, 11)
    r.door('e', 'R', 9, 'blue', 'hall', 'w')
    return r
ROOMS.append(crash())

def hall():
    r = Room('hall', 'Overgrown Hall', 60, 17, 2, 1, solid=True)
    r.cave([(0, 12), (12, 15), (44, 15), (48, 12)], [(0, 2), (17, 5), (22, 6), (38, 5), (45, 2)])
    r.door('w', 'L', 9, 'blue', 'crash', 'e'); r.door('e', 'R', 9, 'blue', 'beacon', 'w')
    r.station('map', 6, 11)
    r.fill(24, 15, 26, 15, '^')
    r.plat(21, 28, 11); r.plat(50, 55, 8)
    r.hang(26, 3, 1); r.hang(31, 2, 2); r.hang(34, 4, 1); r.hang(20, 2, 1)
    r.on('c', 16); r.on('c', 34); r.on('o', 40); r.spawn('m', 30, 8); r.spawn('m', 52, 6)
    r.wall(14, 2, 46, 14)
    return r
ROOMS.append(hall())

def beacon():
    r = Room('beacon', 'Beacon Room', 20, 17, 4, 1, solid=True, wall_all=True)
    r.cave([(0, 15), (7, 13), (14, 15)], [(0, 7), (4, 5), (7, 3), (13, 5), (16, 7)])
    r.door('w', 'L', 12, 'blue', 'hall', 'e'); r.door('e', 'R', 12, 'blue', 'shaft', 'wl')
    r.station('save', 9, 12)
    return r
ROOMS.append(beacon())

def shaft():
    r = Room('shaft', 'Collapsed Shaft', 30, 34, 5, 0, solid=True, wall_all=True)
    r.cave([(0, 32)], [(0, 2)])
    r.door('wl', 'L', 29, 'blue', 'beacon', 'e'); r.door('el', 'R', 29, 'blue', 'cellar', 'w'); r.door('eh', 'R', 5, 'blue', 'ruins', 'w')
    for (x0, x1, y) in [(4, 8, 29), (10, 14, 26), (16, 20, 23), (22, 26, 20), (16, 20, 17), (10, 14, 14), (4, 8, 11)]: r.plat(x0, x1, y)
    r.fill(10, 8, 28, 8, '#'); r.fill(14, 9, 15, 10, '#'); r.fill(22, 9, 22, 11, '#')
    r.fill(27, 18, 28, 18, '#'); r.fill(27, 20, 28, 20, '#'); r.g[19][27] = 'b'   # a ball-sized nook sealed by one shot block (crouch to shoot it)
    r.item('tank1', 'energyTank', 28, 19)
    r.fill(1, 12, 2, 19, '#'); r.fill(1, 22, 3, 27, '#'); r.fill(26, 24, 28, 27, '#'); r.fill(25, 25, 25, 26, '#')
    r.spawn('m', 14, 18); r.spawn('m', 8, 8); r.spawn('c', 20, 31); r.spawn('c', 12, 31)
    return r
ROOMS.append(shaft())

def cellar():
    r = Room('cellar', 'Root Cellar', 30, 17, 6, 1, solid=True, wall_all=True)
    r.cave([(0, 15), (14, 13), (19, 13), (22, 15)], [(0, 3), (10, 5), (18, 4), (24, 2)])
    r.door('w', 'L', 12, 'blue', 'shaft', 'el'); r.door('e', 'R', 14, 'open', 'passage', 'w', h=1)
    r.fill(24, 12, 28, 13, '#')
    r.item('morph', 'morph', 12, 14)
    r.spawn('c', 8, 14); r.spawn('m', 18, 9)
    for (x, n) in [(5, 3), (8, 5), (12, 2), (15, 4), (19, 5), (21, 2)]: r.hang(x, n, 1)
    r.fill(6, 11, 9, 11, '=')
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
    r = Room('cache', 'Missile Cache', 30, 17, 9, 2, solid=True, wall_all=True)
    r.cave([(0, 15), (16, 12), (27, 15)], [(0, 2), (8, 4), (20, 3), (26, 2)])
    r.door('w', 'L', 14, 'open', 'passage', 'e', h=1)
    r.fill(1, 12, 5, 13, '#')
    r.item('missile', 'missile', 22, 11)
    r.on('o', 10); r.spawn('m', 12, 7)
    r.hang(11, 3, 1); r.hang(14, 2, 2)
    return r
ROOMS.append(cache())

def ruins():
    r = Room('ruins', 'Upper Ruins', 60, 17, 6, 0, solid=True)
    r.cave([(0, 15), (31, 13), (41, 15)], [(0, 2), (30, 3), (44, 2)])
    r.door('w', 'L', 12, 'blue', 'shaft', 'eh'); r.door('e', 'R', 12, 'red', 'vault', 'w')
    r.plat(8, 12, 12); r.plat(14, 18, 9); r.plat(20, 24, 6)
    r.item('mtank1', 'missileTank', 22, 5)
    r.plat(33, 37, 10); r.plat(46, 52, 10); r.fill(44, 7, 45, 9, '#')
    r.hang(40, 2, 2); r.hang(26, 2, 2); r.hang(52, 2, 3)
    for x in (15, 34, 44): r.on('c', x)
    r.spawn('o', 36, 11); r.spawn('m', 22, 8); r.spawn('m', 36, 5); r.spawn('m', 52, 7)
    r.wall(18, 2, 36, 14)
    return r
ROOMS.append(ruins())

def vault():
    r = Room('vault', 'Bomb Vault', 30, 17, 8, 0, solid=True, wall_all=True)
    r.cave([(0, 15), (11, 12), (19, 15)], [(0, 2)])
    r.door('w', 'L', 12, 'red', 'ruins', 'e'); r.door('e', 'R', 12, 'blue', 'rootfall', 'wt')
    r.item('bombs', 'bombs', 13, 11)
    r.on('c', 4); r.on('c', 25); r.spawn('m', 14, 6)
    for (x, n) in [(6, 5), (10, 3), (16, 3), (21, 5)]: r.hang(x, n, 2)
    return r
ROOMS.append(vault())

def rootfall():
    r = Room('rootfall', 'Rootfall', 30, 34, 9, 0, solid=True, wall_all=True)
    r.cave([(0, 32)], [(0, 2)])
    r.door('wt', 'L', 5, 'blue', 'vault', 'e'); r.door('el', 'R', 29, 'blue', 'cavern', 'w')
    r.fill(1, 8, 12, 8, '#'); r.fill(13, 8, 15, 9, 'B'); r.fill(16, 8, 28, 8, '#')
    r.fill(25, 5, 25, 7, 'M'); r.fill(26, 2, 28, 4, '#'); r.item('tank2', 'energyTank', 27, 7)
    for (x0, x1, y) in [(10, 17, 11), (14, 18, 14), (20, 24, 17), (14, 18, 20), (8, 12, 23), (14, 18, 26), (20, 24, 29)]: r.plat(x0, x1, y)
    r.fill(2, 31, 6, 31, '^')
    r.fill(1, 17, 3, 22, '#'); r.fill(1, 25, 2, 29, '#'); r.fill(26, 12, 28, 16, '#'); r.fill(27, 21, 28, 25, '#')
    r.spawn('m', 20, 12); r.spawn('m', 10, 20); r.spawn('c', 5, 7)
    return r
ROOMS.append(rootfall())

def cavern():
    r = Room('cavern', 'Deep Cavern', 60, 17, 10, 1, solid=True, wall_all=True)
    r.cave([(0, 15)], [(0, 2), (5, 5), (14, 3), (28, 6), (36, 3), (50, 2)])
    r.door('w', 'L', 12, 'blue', 'rootfall', 'el'); r.door('e', 'R', 12, 'blue', 'approach', 'w')
    r.fill(10, 15, 13, 15, '^'); r.plat(9, 14, 12)
    r.ramp(16, 15, 2, True); r.fill(18, 13, 20, 14, '#'); r.ramp(21, 15, 2, False)
    r.fill(26, 12, 29, 14, '#'); r.plat(22, 25, 9)
    r.fill(31, 15, 34, 15, '^')
    # pillars two tiles apart climb to a ball tunnel in a hanging slab; its mouth is sealed with bomb blocks
    r.fill(38, 13, 40, 14, '#'); r.fill(43, 11, 45, 14, '#'); r.fill(47, 9, 50, 10, '#')   # last step floats, so the floor path to the door stays open beneath it
    r.fill(51, 2, 58, 9, '#'); r.fill(51, 8, 57, 8, '.'); r.fill(51, 8, 52, 8, 'B')
    r.item('mtank3', 'missileTank', 56, 8)
    for (x, y) in [(15, 14), (24, 14), (36, 14), (41, 12)]: r.spawn('c', x, y)
    r.spawn('o', 28, 11); r.spawn('m', 18, 7); r.spawn('m', 34, 6); r.spawn('m', 46, 6)
    return r
ROOMS.append(cavern())

def approach():
    r = Room('approach', 'Warden\'s Approach', 30, 17, 12, 1, solid=True, wall_all=True)
    r.cave([(0, 15)], [(0, 2), (3, 4), (26, 2)])
    r.door('w', 'L', 12, 'blue', 'cavern', 'e'); r.door('e', 'R', 12, 'blue', 'arena', 'w')
    r.station('save', 12, 14)
    r.fill(8, 5, 9, 8, '#'); r.fill(19, 5, 20, 8, '#'); r.fill(19, 12, 22, 12, '#')
    return r
ROOMS.append(approach())

def arena():
    r = Room('arena', 'Warden Chamber', 40, 17, 13, 1, solid=True, wall_all=True)
    r.cave([(0, 15)], [(0, 2), (2, 4), (9, 3), (14, 2), (26, 2), (31, 3), (37, 4)])
    r.door('w', 'L', 12, 'blue', 'approach', 'e'); r.door('e', 'R', 12, 'boss', 'lift', 'w')
    r.plat(5, 9, 12); r.plat(30, 34, 12)
    r.spawn('K', 30, 14)
    return r
ROOMS.append(arena())

def lift():
    r = Room('lift', 'Lift Shaft', 30, 17, 15, 1, solid=True, wall_all=True)
    r.cave([(0, 15), (7, 13), (13, 15)], [(0, 2), (4, 5), (14, 3), (18, 2), (28, 5)])
    r.door('w', 'L', 12, 'blue', 'arena', 'e')
    r.item('charge', 'charge', 9, 12)
    r.station('lift', 22, 14, to='gate')
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
