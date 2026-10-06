r"""Zone 5 (Hive Core) room layouts -> js/rooms/zone5.js. Extra tiles: S scan block (invisible and non-solid until the scan visor is held, then solid); spawns u hive moth, g carapace guard, p spore pod, k egg spawner, K boss."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from zone1_gen import Room, BS

Z = []
def room(*a, **k):
    r = Room(*a, **k); r.zone = 5; Z.append(r); return r

def hgate():
    r = room('hgate', 'Hive Gate', 30, 17, 0, 10, wall_all=True)
    r.spawn('P', 4, 14); r.door('e', 'R', 12, 'blue', 'bloom', 'w')
    r.fill(12, 12, 15, 12, '#'); r.spawn('g', 20, 14)
    return r
hgate()

def bloom():
    r = room('bloom', 'The Bloom', 60, 17, 1, 10)
    r.door('w', 'L', 12, 'blue', 'hgate', 'e'); r.door('e', 'R', 12, 'blue', 'beacon5', 'w')
    r.station('map', 5, 14)
    r.ramp(10, 15, 2, True); r.fill(12, 13, 17, 14, '#'); r.ramp(18, 15, 2, False); r.plat(24, 28, 11); r.plat(33, 37, 9)
    r.fill(40, 12, 43, 14, '#'); r.fill(48, 11, 56, 11, '#'); r.fill(49, 12, 55, 14, '.'); r.item('scan', 'scanVisor', 52, 10)
    r.spawn('g', 8, 14); r.spawn('g', 30, 14); r.spawn('k', 15, 12); r.spawn('k', 45, 11); r.spawn('u', 26, 7); r.spawn('p', 41, 11)
    r.wall(14, 2, 46, 14)
    return r
bloom()

def beacon5():
    r = room('beacon5', 'Brood Beacon', 20, 17, 3, 10, wall_all=True)
    r.door('w', 'L', 12, 'blue', 'bloom', 'e'); r.door('e', 'R', 12, 'blue', 'maw', 'w')
    r.station('save', 10, 14)
    return r
beacon5()

def maw():
    r = room('maw', 'The Maw', 60, 17, 4, 10, wall_all=True)
    r.door('w', 'L', 12, 'blue', 'beacon5', 'e'); r.door('e', 'R', 12, 'blue', 'ascent', 'wl')
    r.fill(12, 15, 46, 15, '^'); r.plat(14, 17, 12); r.plat(21, 24, 11); r.plat(28, 31, 12); r.plat(35, 38, 11); r.plat(42, 45, 12)
    r.fill(26, 8, 29, 8, 'S'); r.item('mtank8', 'missileTank', 27, 7)         # hidden stepping stones above the pit: scan to see them
    r.spawn('u', 20, 7); r.spawn('u', 38, 6); r.spawn('g', 6, 14); r.spawn('g', 52, 14); r.spawn('p', 55, 14)
    return r
maw()

def ascent():
    r = room('ascent', 'The Ascent', 30, 34, 6, 9, wall_all=True)
    r.door('wl', 'L', 29, 'blue', 'maw', 'e'); r.door('eh', 'R', 4, 'blue', 'nest', 'w')
    for (x0, x1, y) in [(4, 8, 27), (12, 16, 22), (4, 8, 17), (12, 16, 12)]: r.fill(x0, y, x1, y, 'S')       # a hidden staircase, five rows apart (space jump between them): scan to see and stand on it
    r.fill(18, 7, 28, 7, '#')
    r.spawn('u', 14, 20); r.spawn('u', 12, 9); r.spawn('g', 22, 31); r.spawn('k', 10, 31)
    return r
ascent()

def nest():
    r = room('nest', 'The Nest', 30, 17, 7, 9, wall_all=True)
    r.door('w', 'L', 12, 'blue', 'ascent', 'eh'); r.door('e', 'R', 12, 'blue', 'vein', 'w')
    r.fill(12, 12, 17, 14, '#'); r.item('plasma', 'plasmaBeam', 14, 11)
    r.spawn('k', 5, 14); r.spawn('k', 25, 14); r.spawn('u', 14, 6); r.spawn('g', 22, 14)
    return r
nest()

def vein():
    r = room('vein', 'The Vein', 60, 17, 7, 10, wall_all=True)
    r.door('w', 'L', 12, 'blue', 'nest', 'e'); r.door('e', 'R', 12, 'blue', 'pre5', 'w'); r.door('v', 'R', 5, 'green', 'cache5', 'w')
    r.fill(14, 12, 16, 14, '#'); r.fill(30, 12, 33, 14, '#'); r.fill(44, 12, 46, 14, '#'); r.plat(50, 56, 8)
    r.fill(57, 8, 58, 8, '#'); r.fill(20, 15, 24, 15, '^'); r.plat(18, 26, 11)
    r.fill(37, 4, 42, 4, '#'); r.fill(37, 8, 42, 8, '#'); r.fill(42, 5, 42, 7, '#'); r.fill(37, 5, 37, 7, 'x'); r.plat(32, 36, 8); r.item('mtank9', 'missileTank', 40, 7)       # wave-crystal pocket
    r.spawn('g', 8, 14); r.spawn('g', 27, 14); r.spawn('g', 40, 14); r.spawn('p', 15, 11); r.spawn('p', 45, 11); r.spawn('k', 52, 7); r.spawn('u', 22, 6)
    return r
vein()

def cache5():
    r = room('cache5', 'Brood Cache', 30, 17, 9, 9, wall_all=True)
    r.door('w', 'L', 12, 'green', 'vein', 'v')
    r.fill(12, 12, 17, 14, '#'); r.item('tank7', 'energyTank', 14, 11)
    r.spawn('k', 5, 14); r.spawn('k', 25, 14)
    return r
cache5()

def pre5():
    r = room('pre5', 'Heart Approach', 30, 17, 9, 10, wall_all=True)
    r.door('w', 'L', 12, 'blue', 'vein', 'e'); r.door('e', 'R', 12, 'blue', 'heartroom', 'w')
    r.station('save', 12, 14)
    return r
pre5()

def heartroom():
    r = room('heartroom', 'Hive Core', 40, 17, 10, 10, wall_all=True)
    r.door('w', 'L', 12, 'blue', 'pre5', 'e'); r.door('e', 'R', 12, 'boss', 'esc1', 'w')
    r.plat(4, 8, 11); r.plat(31, 35, 11); r.plat(17, 22, 9)
    r.spawn('K', 20, 5)
    return r
heartroom()

def esc1():
    r = room('esc1', 'Collapse I', 60, 17, 12, 10, wall_all=True)
    r.door('w', 'L', 12, 'blue', 'heartroom', 'e'); r.door('e', 'R', 12, 'blue', 'esc2', 'w')
    r.fill(14, 15, 18, 15, '^'); r.plat(13, 19, 12); r.fill(30, 12, 33, 14, '#'); r.fill(42, 15, 46, 15, '^'); r.plat(41, 47, 12)
    r.spawn('g', 24, 14); r.spawn('u', 36, 8)
    return r
esc1()

def esc2():
    r = room('esc2', 'Collapse II', 60, 17, 14, 10, wall_all=True)
    r.door('w', 'L', 12, 'blue', 'esc1', 'e'); r.door('e', 'R', 12, 'blue', 'hatch', 'w')
    r.fill(16, 15, 24, 15, '^'); r.plat(15, 18, 12); r.plat(21, 25, 11); r.fill(34, 12, 36, 14, '#'); r.fill(44, 12, 46, 14, '#'); r.plat(38, 42, 10)
    r.spawn('g', 30, 14); r.spawn('u', 28, 7)
    return r
esc2()

def hatch():
    r = room('hatch', 'Surface Hatch', 30, 17, 16, 10, wall_all=True)
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
