r"""Zone 4 (Drowned Reactor) room layouts -> js/rooms/zone4.js. Extra tiles: W water (non-solid; in 'pressure' rooms it drains energy without the aqua suit), G grapple anchor (hang under a block); spawns j jelly, d drone, r reactor turret, a electric arc."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from zone1_gen import Room, BS

Z = []
def room(*a, **k):
    r = Room(*a, **k); r.zone = 4; Z.append(r); return r

def rgate():
    r = room('rgate', 'Reactor Gate', 30, 17, 0, 8, wall_all=True)
    r.spawn('P', 4, 14); r.door('e', 'R', 12, 'blue', 'intake', 'w')
    r.fill(10, 13, 22, 14, 'W'); r.fill(14, 12, 17, 12, '#'); r.spawn('d', 25, 14)
    return r
rgate()

def intake():
    r = room('intake', 'Intake Hall', 60, 17, 1, 8)
    r.door('w', 'L', 12, 'blue', 'rgate', 'e'); r.door('e', 'R', 12, 'blue', 'beacon4', 'w')
    r.station('map', 5, 14)
    r.fill(14, 10, 46, 14, 'W'); r.plat(18, 22, 12); r.plat(30, 34, 11); r.fill(24, 13, 27, 14, '#')
    r.spawn('j', 20, 9); r.spawn('j', 38, 8); r.spawn('d', 9, 14); r.spawn('d', 52, 14); r.spawn('r', 26, 12)
    r.wall(14, 2, 46, 14)
    return r
intake()

def beacon4():
    r = room('beacon4', 'Coolant Beacon', 20, 17, 3, 8, wall_all=True)
    r.door('w', 'L', 12, 'blue', 'intake', 'e'); r.door('e', 'R', 12, 'blue', 'sluice', 'w')
    r.station('save', 10, 14)
    return r
beacon4()

def sluice():
    r = room('sluice', 'Sluice Gate', 60, 17, 4, 8, wall_all=True)
    r.door('w', 'L', 12, 'blue', 'beacon4', 'e'); r.door('e', 'R', 12, 'blue', 'pump', 'w')
    r.fill(6, 11, 22, 14, 'W'); r.fill(36, 11, 52, 14, 'W'); r.fill(26, 12, 32, 14, '#')
    r.spawn('a', 24, 14); r.spawn('a', 34, 14); r.spawn('r', 29, 11); r.spawn('j', 12, 9); r.spawn('j', 44, 9); r.spawn('d', 56, 14)
    r.g[14][26] = 'b'; r.fill(27, 14, 29, 14, '.'); r.item('tank5', 'energyTank', 29, 14)      # a ball nook in the pillar, sealed by a shot block
    return r
sluice()

def pump():
    r = room('pump', 'Pump Room', 30, 17, 6, 8, wall_all=True)
    r.door('w', 'L', 12, 'blue', 'sluice', 'e'); r.door('e', 'R', 12, 'blue', 'deepcut', 'w')
    r.fill(3, 9, 26, 14, 'W'); r.fill(12, 12, 17, 14, '#'); r.item('aqua', 'aquaSuit', 14, 11)
    r.spawn('j', 8, 8); r.spawn('j', 22, 9); r.spawn('d', 4, 14)
    return r
pump()

def deepcut():
    r = room('deepcut', 'The Deep Cut', 60, 17, 7, 8, wall_all=True)
    r.pressure = True
    r.door('w', 'L', 12, 'blue', 'pump', 'e'); r.door('e', 'R', 12, 'blue', 'coolant', 'w'); r.door('v', 'R', 5, 'green', 'vent', 'w')
    r.fill(1, 2, 58, 14, 'W')
    r.fill(14, 12, 18, 14, '#'); r.fill(28, 9, 31, 14, '#'); r.fill(42, 12, 46, 14, '#'); r.plat(34, 38, 8); r.plat(50, 56, 8)
    r.fill(51, 8, 58, 8, '#'); r.fill(51, 7, 52, 7, '.')
    r.item('tank6', 'energyTank', 24, 14)
    r.spawn('j', 10, 9); r.spawn('j', 22, 6); r.spawn('j', 36, 11); r.spawn('j', 48, 7); r.spawn('r', 16, 11); r.spawn('r', 44, 11)
    return r
deepcut()

def coolant():
    r = room('coolant', 'Coolant Works', 30, 17, 9, 8, wall_all=True)
    r.door('w', 'L', 12, 'blue', 'deepcut', 'e'); r.door('e', 'R', 12, 'blue', 'gantry', 'wl')
    r.fill(12, 12, 17, 14, '#'); r.item('grapple', 'grapple', 14, 11)
    r.fill(3, 13, 10, 14, 'W'); r.fill(19, 13, 27, 14, 'W')
    r.spawn('a', 8, 14); r.spawn('a', 22, 14); r.spawn('d', 5, 14); r.spawn('j', 24, 11)
    return r
coolant()

def gantry():
    r = room('gantry', 'Gantry Shaft', 30, 34, 10, 7, wall_all=True)
    r.door('wl', 'L', 29, 'blue', 'coolant', 'e'); r.door('eh', 'R', 3, 'blue', 'pre4', 'w')
    # three ledges seven rows apart, each with a ceiling slab and grapple anchors above it: grapple up, hang, and leap onto the ledge
    for (ly, sx0, sx1, lx0, lx1) in [(25, 9, 12, 6, 15), (18, 13, 16, 10, 19), (11, 17, 20, 14, 20)]:
        r.plat(lx0, lx1, ly)
        r.fill(sx0, ly - 4, sx1, ly - 4, '#')
        for x in range(sx0 + 1, sx1): r.g[ly - 3][x] = 'G'
    r.fill(22, 6, 28, 6, '#')
    r.fill(2, 30, 27, 31, 'W')
    r.spawn('d', 24, 31); r.spawn('r', 26, 31); r.spawn('j', 8, 20); r.spawn('j', 18, 14)
    return r
gantry()

def vent():
    r = room('vent', 'Vent Chamber', 30, 17, 8, 9, wall_all=True)
    r.door('w', 'L', 12, 'green', 'deepcut', 'v')
    r.fill(12, 12, 17, 14, '#'); r.item('stank', 'superTank', 14, 11)
    return r
vent()

def pre4():
    r = room('pre4', 'Core Approach', 30, 17, 11, 8, wall_all=True)
    r.door('w', 'L', 12, 'blue', 'gantry', 'eh'); r.door('e', 'R', 12, 'blue', 'arena4', 'w')
    r.station('save', 12, 14)
    return r
pre4()

def arena4():
    r = room('arena4', 'Flooded Core', 40, 17, 12, 8, wall_all=True)
    r.door('w', 'L', 12, 'blue', 'pre4', 'e'); r.door('e', 'R', 12, 'boss', 'lift4', 'w')
    r.fill(1, 2, 38, 14, 'W'); r.plat(5, 9, 11); r.plat(30, 34, 11); r.plat(17, 22, 8)
    r.spawn('K', 20, 13)
    return r
arena4()

def lift4():
    r = room('lift4', 'Surface Lock', 30, 17, 14, 8, wall_all=True)
    r.door('w', 'L', 12, 'blue', 'arena4', 'e')
    r.item('super', 'superMissile', 10, 14); r.station('lift', 22, 14, to='hgate')
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
