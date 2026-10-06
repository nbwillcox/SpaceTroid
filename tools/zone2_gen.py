"""Zone 2 (Cryo Vaults) room layouts -> js/rooms/zone2.js. Extra tiles: i slippery ice floor; spawns f frostling, q wisp (freeze it with the ice beam to make a stepping stone), t shard turret, v icicle (marker on the first row below the ceiling)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from zone1_gen import Room, BS

Z = []
def room(*a, **k):
    r = Room(*a, **k); r.zone = 2; Z.append(r); return r

def gate():
    r = room('gate', 'Frozen Landing', 30, 17, 0, 4, wall_all=True)
    r.spawn('P', 4, 14); r.door('e', 'R', 12, 'blue', 'drift', 'w')
    r.fill(9, 15, 19, 15, 'i'); r.fill(22, 12, 25, 12, '#')
    r.spawn('f', 17, 14); r.spawn('v', 14, 2); r.spawn('v', 21, 2)
    return r
gate()

def drift():
    r = room('drift', 'Snowdrift Hall', 60, 17, 1, 4)
    r.door('w', 'L', 12, 'blue', 'gate', 'e'); r.door('e', 'R', 12, 'blue', 'beacon2', 'w')
    r.station('map', 5, 14)
    r.fill(8, 15, 18, 15, 'i'); r.fill(40, 15, 50, 15, 'i'); r.fill(28, 15, 30, 15, '^')
    r.plat(26, 32, 12); r.fill(34, 12, 37, 14, '#'); r.plat(52, 56, 11)
    r.ramp(20, 15, 2, True); r.fill(22, 13, 24, 14, '#'); r.ramp(25, 15, 2, False)
    for (x, y) in [(14, 2), (16, 2), (30, 2), (45, 2), (48, 2)]: r.spawn('v', x, y)
    r.spawn('f', 12, 14); r.spawn('f', 42, 14); r.spawn('q', 30, 8); r.spawn('t', 35, 11)
    r.wall(14, 2, 40, 14)
    return r
drift()

def beacon2():
    r = room('beacon2', 'Cold Beacon', 20, 17, 3, 4, wall_all=True)
    r.door('w', 'L', 12, 'blue', 'drift', 'e'); r.door('e', 'R', 12, 'blue', 'gallery', 'w')
    r.station('save', 10, 14); r.spawn('v', 6, 2); r.spawn('v', 14, 2)
    return r
beacon2()

def gallery():
    r = room('gallery', 'Crystal Gallery', 60, 17, 4, 4)
    r.door('w', 'L', 12, 'blue', 'beacon2', 'e'); r.door('e', 'R', 12, 'blue', 'chasm', 'w'); r.door('n', 'R', 3, 'blue', 'icecache', 'w')
    r.fill(6, 15, 14, 15, 'i'); r.fill(30, 15, 40, 15, 'i')
    r.fill(18, 12, 20, 14, '#'); r.fill(38, 12, 40, 14, '#')
    r.plat(8, 12, 12); r.plat(24, 28, 12)
    r.plat(44, 48, 12); r.plat(49, 53, 9); r.fill(54, 6, 58, 6, '#')
    r.item('mtank4', 'missileTank', 51, 8)
    r.spawn('t', 19, 11); r.spawn('t', 39, 11); r.spawn('f', 10, 14); r.spawn('f', 34, 14); r.spawn('q', 26, 7); r.spawn('q', 45, 8)
    for x in (12, 26, 44, 52): r.spawn('v', x, 2)
    r.wall(10, 2, 50, 14)
    return r
gallery()

def icecache():
    r = room('icecache', 'Ice Cache', 30, 17, 5, 5, wall_all=True)
    r.door('w', 'L', 12, 'blue', 'gallery', 'n')
    r.fill(12, 12, 17, 14, '#'); r.item('ice', 'iceBeam', 14, 11)
    r.spawn('t', 5, 14); r.spawn('f', 23, 14); r.spawn('v', 14, 2); r.spawn('v', 20, 2)
    return r
icecache()

def chasm():
    r = room('chasm', 'Wisp Chasm', 60, 17, 6, 4, wall_all=True)
    r.door('w', 'L', 12, 'blue', 'gallery', 'e'); r.door('e', 'R', 12, 'blue', 'bridge', 'w')
    r.fill(9, 15, 49, 15, '^')
    r.plat(11, 14, 12); r.plat(18, 21, 11); r.plat(26, 29, 12); r.plat(34, 37, 11); r.plat(42, 45, 12)
    r.fill(30, 8, 33, 8, '#'); r.item('tank3', 'energyTank', 31, 7)     # high ledge: freeze a wisp to reach it
    r.spawn('q', 31, 11); r.spawn('q', 22, 8); r.spawn('t', 52, 14); r.spawn('f', 4, 14)
    for x in (16, 24, 40): r.spawn('v', x, 2)
    return r
chasm()

def bridge():
    r = room('bridge', 'Frozen Bridge', 60, 17, 8, 4, wall_all=True)
    r.door('w', 'L', 12, 'blue', 'chasm', 'e'); r.door('e', 'R', 12, 'blue', 'shaft2', 'wl')
    r.fill(2, 15, 57, 15, 'i')
    r.fill(14, 12, 16, 14, '#'); r.fill(30, 12, 32, 14, '#'); r.fill(46, 12, 48, 14, '#')
    r.spawn('t', 15, 11); r.spawn('t', 31, 11); r.spawn('t', 47, 11); r.spawn('f', 22, 14); r.spawn('f', 38, 14)
    r.g[14][30] = 'B'; r.g[14][31] = '.'; r.item('mtank5', 'missileTank', 31, 14)      # a ball nook in the middle pillar, sealed by a bomb block
    return r
bridge()

def shaft2():
    r = room('shaft2', 'Frostfall', 30, 34, 10, 3, wall_all=True)
    r.door('wl', 'L', 29, 'blue', 'bridge', 'e'); r.door('eh', 'R', 3, 'blue', 'pre2', 'w')
    for (x0, x1, y) in [(4, 8, 29), (10, 14, 26), (16, 20, 23), (22, 26, 20), (16, 20, 17), (10, 14, 14), (14, 18, 9), (20, 27, 6)]: r.plat(x0, x1, y)
    r.fill(20, 6, 28, 6, '#')
    r.spawn('q', 12, 12)          # the gap between the 14 and 9 ledges: freeze this wisp and use it as a step
    r.spawn('t', 25, 31); r.spawn('f', 8, 31); r.spawn('q', 8, 18)
    for x in (6, 12, 20, 24): r.spawn('v', x, 2)
    return r
shaft2()

def pre2():
    r = room('pre2', 'Sentinel Approach', 30, 17, 11, 4, wall_all=True)
    r.door('w', 'L', 12, 'blue', 'shaft2', 'eh'); r.door('e', 'R', 12, 'blue', 'arena2', 'w')
    r.station('save', 12, 14); r.spawn('v', 8, 2); r.spawn('v', 20, 2)
    return r
pre2()

def arena2():
    r = room('arena2', 'Rime Hall', 40, 17, 12, 4, wall_all=True)
    r.door('w', 'L', 12, 'blue', 'pre2', 'e'); r.door('e', 'R', 12, 'boss', 'heat', 'w')
    r.plat(5, 9, 11); r.plat(30, 34, 11); r.plat(17, 22, 8)
    r.spawn('K', 28, 14)
    return r
arena2()

def heat():
    r = room('heat', 'Thermal Vault', 30, 17, 14, 4, wall_all=True)
    r.door('w', 'L', 12, 'blue', 'arena2', 'e')
    r.item('heat', 'heatSuit', 10, 14); r.station('lift', 22, 14, to='fgate')
    return r
heat()

if __name__ == '__main__':
    out = {}
    for r in Z:
        d = r.emit(); out[d['id']] = d
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'js', 'rooms', 'zone2.js')
    src = "/* GENERATED by tools/zone2_gen.py: zone 2 room layouts, doors, items and stations. */\n(function (G) {\n  G.rooms = G.rooms || {};\n  Object.assign(G.rooms, " + json.dumps(out, separators=(',', ':')) + ");\n})((window.SGS = window.SGS || {}));\n"
    open(path, 'w', encoding='utf-8').write(src)
    print('wrote', len(src), 'rooms', len(out))
