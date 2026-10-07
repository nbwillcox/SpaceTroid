r"""Zone 4 (Drowned Reactor) room layouts -> js/rooms/zone4.js. Extra tiles: W water (non-solid; in 'pressure' rooms it drains energy without the aqua suit), G grapple anchor (hang under a block); spawns j jelly, d drone, r reactor turret, a electric arc."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from room_kit import Room, BS

Z = []
def room(*a, **k):
    r = Room(*a, **k); r.zone = 4; Z.append(r); return r

def rgate():
    r = room('rgate', 'Reactor Gate', 30, 17, 0, 8, solid=True, wall_all=True)
    r.cave([(0, 14), (7, 15)], [(0, 2), (5, 5), (12, 3), (24, 2)])
    r.spawn('P', 3, 13); r.door('e', 'R', 12, 'blue', 'intake', 'w')
    r.flood(9, 23, 13); r.fill(14, 12, 17, 12, '#'); r.on('d', 25)
    r.hang(8, 3, 1); r.hang(20, 2, 2)
    return r
rgate()

def intake():
    r = room('intake', 'Intake Hall', 60, 17, 1, 8, solid=True)
    r.cave([(0, 15), (8, 13), (13, 15), (51, 13), (55, 15)], [(0, 2), (10, 4), (20, 2), (38, 5), (48, 2)])
    r.door('w', 'L', 12, 'blue', 'rgate', 'e'); r.door('e', 'R', 12, 'blue', 'beacon4', 'w')
    r.station('map', 5, 14)
    r.flood(11, 50, 10); r.plat(18, 22, 12); r.plat(30, 34, 11); r.fill(24, 13, 27, 14, '#')
    r.spawn('j', 20, 9); r.spawn('j', 38, 8); r.on('d', 9); r.on('d', 52); r.spawn('r', 26, 12)
    r.wall(14, 2, 46, 14)
    return r
intake()

def beacon4():
    r = room('beacon4', 'Coolant Beacon', 20, 17, 3, 8, solid=True, wall_all=True)
    r.cave([(0, 15)], [(0, 5), (3, 3), (6, 2), (14, 3), (17, 5)])
    r.door('w', 'L', 12, 'blue', 'intake', 'e'); r.door('e', 'R', 12, 'blue', 'sluice', 'w')
    r.station('save', 10, 14)
    return r
beacon4()

def sluice():
    r = room('sluice', 'Sluice Gate', 60, 17, 4, 8, solid=True, wall_all=True)
    r.cave([(0, 15), (4, 13), (8, 15), (52, 13), (56, 15)], [(0, 2), (8, 5), (24, 3), (34, 3), (48, 5), (54, 2)])
    r.door('w', 'L', 12, 'blue', 'beacon4', 'e'); r.door('e', 'R', 12, 'blue', 'pump', 'w')
    r.flood(8, 23, 11); r.flood(35, 50, 11); r.fill(26, 12, 32, 14, '#')
    r.spawn('a', 24, 14); r.spawn('a', 34, 14); r.spawn('r', 29, 11); r.spawn('j', 12, 9); r.spawn('j', 44, 9); r.on('d', 57)
    r.g[14][26] = 'b'; r.fill(27, 14, 29, 14, '.'); r.item('tank5', 'energyTank', 29, 14)      # a ball nook in the pillar, sealed by a shot block
    return r
sluice()

def pump():
    r = room('pump', 'Pump Room', 30, 17, 6, 8, solid=True, wall_all=True)
    r.cave([(0, 15), (10, 12), (19, 15)], [(0, 2), (4, 4), (12, 2), (24, 4)])
    r.door('w', 'L', 12, 'blue', 'sluice', 'e'); r.door('e', 'R', 12, 'blue', 'deepcut', 'w')
    r.flood(3, 26, 9); r.item('aqua', 'aquaSuit', 13, 11)
    r.spawn('j', 8, 8); r.spawn('j', 22, 9); r.on('d', 4)
    return r
pump()

def deepcut():
    r = room('deepcut', 'The Deep Cut', 60, 17, 7, 8, solid=True, wall_all=True)
    r.pressure = True
    r.cave([(0, 15), (6, 14), (10, 15)], [(0, 2), (6, 4), (14, 2), (30, 5), (40, 2), (50, 4), (54, 2)])
    r.door('w', 'L', 12, 'blue', 'pump', 'e'); r.door('e', 'R', 12, 'blue', 'coolant', 'w'); r.door('v', 'R', 5, 'green', 'vent', 'w')
    r.flood(1, 58, 2)
    r.fill(14, 12, 18, 14, '#'); r.fill(28, 9, 31, 14, '#'); r.fill(42, 12, 46, 14, '#'); r.plat(34, 38, 8); r.plat(50, 56, 8)
    r.fill(51, 8, 58, 8, '#'); r.fill(51, 7, 52, 7, '.')
    r.item('tank6', 'energyTank', 24, 14)
    r.spawn('j', 10, 9); r.spawn('j', 22, 6); r.spawn('j', 36, 11); r.spawn('j', 48, 7); r.spawn('r', 16, 11); r.spawn('r', 44, 11)
    return r
deepcut()

def coolant():
    r = room('coolant', 'Coolant Works', 30, 17, 9, 8, solid=True, wall_all=True)
    r.cave([(0, 15), (8, 14), (11, 13), (14, 12), (21, 13), (24, 14), (27, 15)], [(0, 2), (6, 4), (12, 2), (22, 4), (26, 2)])
    r.door('w', 'L', 12, 'blue', 'deepcut', 'e'); r.door('e', 'R', 12, 'blue', 'gantry', 'wl')
    r.item('grapple', 'grapple', 15, 11)
    r.flood(1, 6, 13)
    r.on('a', 4); r.on('a', 24); r.on('d', 3); r.spawn('j', 24, 10)
    return r
coolant()

def gantry():
    r = room('gantry', 'Gantry Shaft', 30, 34, 10, 7, solid=True, wall_all=True)
    r.cave([(0, 32)], [(0, 2)])
    r.door('wl', 'L', 29, 'blue', 'coolant', 'e'); r.door('eh', 'R', 3, 'blue', 'pre4', 'w')
    # three ledges seven rows apart, each with a ceiling slab and grapple anchors above it: grapple up, hang, and leap onto the ledge
    for (ly, sx0, sx1, lx0, lx1) in [(25, 9, 12, 6, 15), (18, 13, 16, 10, 19), (11, 17, 20, 14, 20)]:
        r.plat(lx0, lx1, ly)
        r.fill(sx0, ly - 4, sx1, ly - 4, '#')
        for x in range(sx0 + 1, sx1): r.g[ly - 3][x] = 'G'
    r.fill(22, 6, 28, 6, '#')
    r.fill(2, 30, 27, 31, 'W')
    r.fill(1, 14, 2, 22, '#'); r.fill(26, 12, 28, 22, '#'); r.fill(27, 24, 28, 28, '#')
    r.spawn('d', 24, 31); r.spawn('r', 26, 31); r.spawn('j', 8, 20); r.spawn('j', 18, 14)
    return r
gantry()

def vent():
    r = room('vent', 'Vent Chamber', 30, 17, 8, 9, solid=True, wall_all=True)
    r.cave([(0, 13), (10, 13), (13, 15), (19, 15), (22, 13)], [(0, 2), (4, 4), (10, 2), (22, 4)])
    r.door('w', 'L', 10, 'green', 'deepcut', 'v')
    r.item('stank', 'superTank', 15, 14)
    return r
vent()

def pre4():
    r = room('pre4', 'Core Approach', 30, 17, 11, 8, solid=True, wall_all=True)
    r.cave([(0, 15)], [(0, 2), (3, 4), (10, 2), (20, 2), (26, 4)])
    r.door('w', 'L', 12, 'blue', 'gantry', 'eh'); r.door('e', 'R', 12, 'blue', 'arena4', 'w')
    r.station('save', 12, 14)
    r.fill(6, 4, 7, 8, '#'); r.fill(22, 4, 23, 8, '#')
    return r
pre4()

def arena4():
    r = room('arena4', 'Flooded Core', 40, 17, 12, 8, solid=True, wall_all=True)
    r.cave([(0, 15)], [(0, 2), (2, 4), (8, 3), (13, 2), (27, 2), (32, 3), (38, 4)])
    r.door('w', 'L', 12, 'blue', 'pre4', 'e'); r.door('e', 'R', 12, 'boss', 'lift4', 'w')
    r.flood(1, 38, 2); r.plat(5, 9, 11); r.plat(30, 34, 11); r.plat(17, 22, 8)
    r.spawn('K', 20, 13)
    return r
arena4()

def lift4():
    r = room('lift4', 'Surface Lock', 30, 17, 14, 8, solid=True, wall_all=True)
    r.cave([(0, 15)], [(0, 2), (4, 4), (16, 2)])
    r.door('w', 'L', 12, 'blue', 'arena4', 'e')
    r.plat(7, 12, 12); r.item('super', 'superMissile', 10, 11); r.station('lift', 22, 14, to='hgate')
    r.fill(14, 4, 15, 7, '#')
    return r
lift4()

if __name__ == '__main__':
    out = {}
    for r in Z:
        d = r.emit(); out[d['id']] = d
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'js', 'rooms', 'zone4.js')
    src = "/* GENERATED by tools/zone4_gen.py: zone 4 room layouts, doors, items and stations. */\n(function (G) {\n  G.rooms = G.rooms || {};\n  Object.assign(G.rooms, " + json.dumps(out, separators=(',', ':')) + ");\n})((window.SGS = window.SGS || {}));\n"
    open(path, 'w', encoding='utf-8').write(src)
    print('wrote', len(src), 'rooms', len(out))
