r"""Zone 5 (Hive Core) room layouts -> js/rooms/zone5.js. Extra tiles: S scan block (invisible and non-solid until the scan visor is held, then solid); spawns u hive moth, g carapace guard, p spore pod, k egg spawner, K boss."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from room_kit import Room, BS

Z = []
def room(*a, **k):
    r = Room(*a, **k); r.zone = 5; Z.append(r); return r

def hgate():
    r = room('hgate', 'Hive Gate', 30, 17, 0, 10, solid=True, wall_all=True)
    r.cave([(0, 15), (8, 13), (14, 15)], [(0, 2), (5, 6), (12, 3), (20, 5), (26, 2)])
    r.spawn('P', 3, 14); r.door('e', 'R', 12, 'blue', 'bloom', 'w')
    r.on('g', 21)
    r.hang(9, 3, 1); r.hang(17, 2, 2)
    return r
hgate()

def bloom():
    r = room('bloom', 'The Bloom', 60, 17, 1, 10, solid=True)
    r.cave([(0, 15), (11, 13), (19, 15)], [(0, 2), (6, 5), (14, 3), (24, 6), (34, 4), (44, 6), (52, 3)])
    r.door('w', 'L', 12, 'blue', 'hgate', 'e'); r.door('e', 'R', 12, 'blue', 'beacon5', 'w')
    r.station('map', 5, 14)
    r.plat(24, 28, 11); r.plat(33, 37, 9)
    r.fill(40, 12, 43, 14, '#'); r.fill(48, 11, 56, 11, '#'); r.fill(49, 12, 55, 14, '.'); r.item('scan', 'scanVisor', 52, 10)
    r.on('g', 8); r.on('g', 30); r.spawn('k', 15, 12); r.spawn('k', 45, 11); r.spawn('u', 26, 7); r.spawn('p', 41, 11)
    r.wall(14, 2, 46, 14)
    return r
bloom()

def beacon5():
    r = room('beacon5', 'Brood Beacon', 20, 17, 3, 10, solid=True, wall_all=True)
    r.cave([(0, 15)], [(0, 7), (2, 5), (5, 3), (14, 3), (17, 5), (19, 7)])
    r.door('w', 'L', 12, 'blue', 'bloom', 'e'); r.door('e', 'R', 12, 'blue', 'maw', 'w')
    r.station('save', 10, 14)
    return r
beacon5()

def maw():
    r = room('maw', 'The Maw', 60, 17, 4, 10, solid=True, wall_all=True)
    r.cave([(0, 15), (5, 13), (10, 15), (52, 13), (56, 15)], [(0, 2)])
    r.door('w', 'L', 12, 'blue', 'beacon5', 'e'); r.door('e', 'R', 12, 'blue', 'ascent', 'wl')
    r.fill(12, 15, 46, 15, '^'); r.plat(14, 17, 12); r.plat(21, 24, 11); r.plat(28, 31, 12); r.plat(35, 38, 11); r.plat(42, 45, 12)
    r.fill(26, 8, 29, 8, 'S'); r.item('mtank8', 'missileTank', 27, 7)         # hidden stepping stones above the pit: scan to see them
    for x in (14, 18, 22, 34, 38, 42, 46): r.hang(x, 3, 1)                    # teeth
    r.spawn('u', 20, 7); r.spawn('u', 38, 6); r.on('g', 6); r.on('g', 52); r.on('p', 57)
    return r
maw()

def ascent():
    r = room('ascent', 'The Ascent', 30, 34, 6, 9, solid=True, wall_all=True)
    r.cave([(0, 32)], [(0, 2)])
    r.door('wl', 'L', 29, 'blue', 'maw', 'e'); r.door('eh', 'R', 4, 'blue', 'nest', 'w')
    for (x0, x1, y) in [(4, 8, 27), (12, 16, 22), (4, 8, 17), (12, 16, 12)]: r.fill(x0, y, x1, y, 'S')       # a hidden staircase, five rows apart (space jump between them): scan to see and stand on it
    r.fill(18, 7, 28, 7, '#')
    r.fill(1, 22, 3, 26, '#'); r.fill(1, 10, 2, 15, '#'); r.fill(24, 10, 28, 16, '#'); r.fill(24, 22, 28, 28, '#')
    r.spawn('u', 14, 20); r.spawn('u', 12, 9); r.spawn('g', 22, 31); r.spawn('k', 10, 31)
    return r
ascent()

def nest():
    r = room('nest', 'The Nest', 30, 17, 7, 9, solid=True, wall_all=True)
    r.cave([(0, 13), (8, 13), (11, 15), (18, 15), (21, 13)], [(0, 2), (6, 4), (12, 3), (20, 5), (26, 2)])
    r.door('w', 'L', 10, 'blue', 'ascent', 'eh'); r.door('e', 'R', 10, 'blue', 'vein', 'w')
    r.item('plasma', 'plasmaBeam', 14, 14)
    r.on('k', 4); r.on('k', 26); r.spawn('u', 14, 6); r.on('g', 24)
    return r
nest()

def vein():
    r = room('vein', 'The Vein', 60, 17, 7, 10, solid=True, wall_all=True)
    r.cave([(0, 15)], [(0, 2), (8, 5), (18, 3), (34, 2), (48, 4), (56, 2)])
    r.door('w', 'L', 12, 'blue', 'nest', 'e'); r.door('e', 'R', 12, 'blue', 'pre5', 'w'); r.door('v', 'R', 5, 'green', 'cache5', 'w')
    r.ramp(11, 15, 3, True); r.fill(14, 12, 16, 14, '#'); r.ramp(17, 15, 3, False)
    r.ramp(27, 15, 3, True); r.fill(30, 12, 33, 14, '#'); r.ramp(34, 15, 3, False)
    r.ramp(41, 15, 3, True); r.fill(44, 12, 46, 14, '#'); r.ramp(47, 15, 3, False)
    r.plat(50, 56, 8)
    r.fill(57, 8, 58, 8, '#'); r.fill(21, 15, 24, 15, '^'); r.plat(18, 26, 11)
    r.fill(37, 4, 42, 4, '#'); r.fill(37, 8, 42, 8, '#'); r.fill(42, 5, 42, 7, '#'); r.fill(37, 5, 37, 7, 'x'); r.plat(32, 36, 8); r.item('mtank9', 'missileTank', 40, 7)       # wave-crystal pocket
    r.on('g', 7); r.on('g', 26); r.on('g', 39); r.spawn('p', 15, 11); r.spawn('p', 45, 11); r.spawn('k', 52, 7); r.spawn('u', 22, 6)
    return r
vein()

def cache5():
    r = room('cache5', 'Brood Cache', 30, 17, 9, 9, solid=True, wall_all=True)
    r.cave([(0, 15), (12, 13), (18, 15)], [(0, 2), (5, 5), (12, 3), (22, 4)])
    r.door('w', 'L', 12, 'green', 'vein', 'v')
    r.item('tank7', 'energyTank', 14, 12)
    r.on('k', 4); r.on('k', 24)
    return r
cache5()

def pre5():
    r = room('pre5', 'Heart Approach', 30, 17, 9, 10, solid=True, wall_all=True)
    r.cave([(0, 15)], [(0, 2), (3, 5), (8, 3), (14, 5), (20, 3), (26, 2)])
    r.door('w', 'L', 12, 'blue', 'vein', 'e'); r.door('e', 'R', 12, 'blue', 'heartroom', 'w')
    r.station('save', 12, 14)
    return r
pre5()

def heartroom():
    r = room('heartroom', 'Hive Core', 40, 17, 10, 10, solid=True, wall_all=True)
    r.cave([(0, 15)], [(0, 2), (2, 4), (8, 3), (14, 2), (26, 2), (32, 3), (38, 4)])
    r.door('w', 'L', 12, 'blue', 'pre5', 'e'); r.door('e', 'R', 12, 'boss', 'esc1', 'w')
    r.plat(4, 8, 11); r.plat(31, 35, 11); r.plat(17, 22, 9)
    r.spawn('K', 20, 5)
    return r
heartroom()

def esc1():
    r = room('esc1', 'Collapse I', 60, 17, 12, 10, solid=True, wall_all=True)
    r.cave([(0, 15)], [(0, 2), (10, 5), (24, 3), (40, 6), (52, 2)])
    r.door('w', 'L', 12, 'blue', 'heartroom', 'e'); r.door('e', 'R', 12, 'blue', 'esc2', 'w')
    r.fill(14, 15, 18, 15, '^'); r.plat(13, 19, 12)
    r.ramp(27, 15, 3, True); r.fill(30, 12, 33, 14, '#'); r.ramp(34, 15, 3, False)
    r.fill(42, 15, 46, 15, '^'); r.plat(41, 47, 12)
    r.on('g', 24); r.spawn('u', 36, 8)
    return r
esc1()

def esc2():
    r = room('esc2', 'Collapse II', 60, 17, 14, 10, solid=True, wall_all=True)
    r.cave([(0, 15)], [(0, 2), (8, 4), (26, 6), (38, 3), (50, 5), (56, 2)])
    r.door('w', 'L', 12, 'blue', 'esc1', 'e'); r.door('e', 'R', 12, 'blue', 'hatch', 'w')
    r.fill(16, 15, 24, 15, '^'); r.plat(15, 18, 12); r.plat(21, 25, 11)
    r.ramp(31, 15, 3, True); r.fill(34, 12, 36, 14, '#'); r.ramp(37, 15, 3, False)
    r.ramp(41, 15, 3, True); r.fill(44, 12, 46, 14, '#'); r.ramp(47, 15, 3, False)
    r.plat(38, 42, 10)
    r.on('g', 29); r.spawn('u', 28, 7)
    return r
esc2()

def hatch():
    r = room('hatch', 'Surface Hatch', 30, 17, 16, 10, solid=True, wall_all=True)
    r.cave([(0, 15)], [(0, 6), (2, 4), (6, 2), (24, 2), (27, 4), (29, 6)])
    r.door('w', 'L', 12, 'blue', 'esc2', 'e')
    r.station('lift', 20, 14)
    return r
hatch()

if __name__ == '__main__':
    out = {}
    for r in Z:
        d = r.emit(); out[d['id']] = d
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'js', 'rooms', 'zone5.js')
    src = "/* GENERATED by tools/zone5_gen.py: zone 5 room layouts, doors, items and stations. */\n(function (G) {\n  G.rooms = G.rooms || {};\n  Object.assign(G.rooms, " + json.dumps(out, separators=(',', ':')) + ");\n})((window.SGS = window.SGS || {}));\n"
    open(path, 'w', encoding='utf-8').write(src)
    print('wrote', len(src), 'rooms', len(out))
