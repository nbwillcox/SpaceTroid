r"""Zone 3 (Magma Forge) room layouts -> js/rooms/zone3.js. Extra tiles: L lava (needs the heat suit), x wave-beam crystal block, D dash block (dash into it); spawns n cinder crawler, h ember hopper, e ember turret, z magmite (marker row = the row above the lava surface)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from zone1_gen import Room, BS

Z = []
def room(*a, **k):
    r = Room(*a, **k); r.zone = 3; Z.append(r); return r

def fgate():
    r = room('fgate', 'Forge Gate', 30, 17, 0, 6, wall_all=True)
    r.spawn('P', 4, 14); r.door('e', 'R', 12, 'blue', 'ember', 'w')
    r.fill(12, 15, 15, 15, 'L'); r.fill(22, 12, 25, 12, '#'); r.spawn('n', 20, 14)
    return r
fgate()

def ember():
    r = room('ember', 'Ember Hall', 60, 17, 1, 6)
    r.door('w', 'L', 12, 'blue', 'fgate', 'e'); r.door('e', 'R', 12, 'blue', 'beacon3', 'w')
    r.station('map', 5, 14)
    r.fill(20, 15, 34, 15, 'L'); r.plat(22, 26, 12); r.plat(29, 33, 12)
    r.fill(40, 12, 43, 14, '#'); r.ramp(10, 15, 2, True); r.fill(12, 13, 15, 14, '#'); r.ramp(16, 15, 2, False)
    r.spawn('n', 8, 14); r.spawn('n', 47, 14); r.spawn('h', 37, 14); r.spawn('z', 27, 14); r.spawn('z', 31, 14); r.spawn('e', 41, 11)
    r.wall(12, 2, 44, 14)
    return r
ember()

def beacon3():
    r = room('beacon3', 'Furnace Beacon', 20, 17, 3, 6, wall_all=True)
    r.door('w', 'L', 12, 'blue', 'ember', 'e'); r.door('e', 'R', 12, 'blue', 'smelter', 'w')
    r.station('save', 10, 14)
    return r
beacon3()

def smelter():
    r = room('smelter', 'The Smelter', 60, 17, 4, 6, wall_all=True)
    r.door('w', 'L', 12, 'blue', 'beacon3', 'e'); r.door('e', 'R', 12, 'blue', 'foundry', 'w')
    r.fill(12, 14, 47, 15, 'L')
    r.fill(15, 8, 18, 9, '#'); r.item('tank4', 'energyTank', 16, 7)       # an island above the vat; ride the lift up
    r.mover('x', 216, 736, 48, 0.9, 222); r.mover('y', 128, 222, 48, 0.7, 232)
    r.spawn('z', 30, 13); r.spawn('z', 40, 13); r.spawn('e', 53, 14); r.spawn('n', 6, 14); r.spawn('n', 52, 14)
    return r
smelter()

def foundry():
    r = room('foundry', 'Old Foundry', 30, 17, 6, 6, wall_all=True)
    r.door('w', 'L', 12, 'blue', 'smelter', 'e'); r.door('e', 'R', 12, 'blue', 'chimney', 'wl')
    r.fill(8, 15, 11, 15, 'L'); r.fill(18, 15, 21, 15, 'L')
    r.fill(13, 12, 17, 14, '#'); r.item('space', 'spaceJump', 15, 11)
    r.spawn('z', 9, 14); r.spawn('z', 19, 14); r.spawn('h', 5, 14); r.spawn('h', 25, 14)
    return r
foundry()

def chimney():
    r = room('chimney', 'Chimney', 30, 34, 7, 5, wall_all=True)
    r.door('wl', 'L', 29, 'blue', 'foundry', 'e'); r.door('wh', 'L', 2, 'blue', 'anvil', 'w')
    for (x0, x1, y) in [(4, 8, 29), (10, 14, 26), (16, 20, 21), (22, 26, 18), (16, 20, 13), (10, 14, 10), (4, 8, 5)]: r.plat(x0, x1, y)
    r.fill(1, 5, 3, 5, '#')
    r.spawn('z', 14, 31); r.spawn('e', 25, 31); r.spawn('n', 20, 31)
    return r
chimney()

def anvil():
    r = room('anvil', 'The Anvil', 30, 17, 8, 6, wall_all=True)
    r.door('w', 'L', 12, 'blue', 'chimney', 'wh'); r.door('e', 'R', 12, 'blue', 'slag', 'w')
    r.fill(12, 12, 17, 14, '#'); r.item('dash', 'dashBoots', 14, 11)
    r.fill(24, 12, 24, 14, 'D')
    r.spawn('h', 6, 14); r.spawn('h', 21, 14); r.spawn('e', 27, 14)
    return r
anvil()

def slag():
    r = room('slag', 'Slag Works', 60, 17, 9, 6, wall_all=True)
    r.door('w', 'L', 12, 'blue', 'anvil', 'e'); r.door('e', 'R', 12, 'blue', 'crucible', 'w')
    r.fill(14, 15, 20, 15, 'L'); r.fill(34, 15, 40, 15, 'L'); r.plat(15, 19, 12); r.plat(35, 39, 12)
    r.fill(26, 11, 28, 14, '#')
    r.fill(46, 12, 46, 14, 'D'); r.item('mtank6', 'missileTank', 52, 14)      # the room's last stretch is walled off by dash blocks
    r.spawn('n', 10, 14); r.spawn('n', 31, 14); r.spawn('h', 24, 14); r.spawn('e', 27, 10); r.spawn('z', 17, 14); r.spawn('z', 37, 14); r.spawn('e', 55, 14)
    return r
slag()

def crucible():
    r = room('crucible', 'The Crucible', 60, 17, 11, 6, wall_all=True)
    r.door('w', 'L', 12, 'blue', 'slag', 'e'); r.door('e', 'R', 12, 'blue', 'pre3', 'w')
    r.fill(14, 15, 26, 15, 'L'); r.plat(15, 18, 12); r.plat(21, 25, 11)
    r.fill(34, 12, 39, 14, '#'); r.fill(44, 12, 46, 14, '#')
    r.fill(40, 8, 52, 8, '#'); r.fill(40, 9, 40, 11, 'x'); r.fill(41, 12, 52, 12, '#'); r.fill(52, 9, 52, 11, '#'); r.item('mtank7', 'missileTank', 46, 11)   # crystal alcove: wave beam only
    r.spawn('e', 35, 11); r.spawn('n', 8, 14); r.spawn('n', 31, 14); r.spawn('h', 54, 14); r.spawn('z', 20, 14); r.spawn('e', 56, 14)
    return r
crucible()

def pre3():
    r = room('pre3', 'Overseer Approach', 30, 17, 13, 6, wall_all=True)
    r.door('w', 'L', 12, 'blue', 'crucible', 'e'); r.door('e', 'R', 12, 'blue', 'arena3', 'w')
    r.station('save', 12, 14)
    return r
pre3()

def arena3():
    r = room('arena3', 'Cinder Pit', 40, 17, 14, 6, wall_all=True)
    r.door('w', 'L', 11, 'blue', 'pre3', 'e'); r.door('e', 'R', 11, 'boss', 'lift3', 'w')
    r.fill(1, 14, 8, 14, '#'); r.fill(17, 14, 22, 14, '#'); r.fill(31, 14, 38, 14, '#')
    r.fill(9, 14, 16, 14, 'L'); r.fill(23, 14, 30, 14, 'L')
    r.plat(11, 14, 11); r.plat(25, 28, 11)
    r.spawn('K', 20, 13)
    return r
arena3()

def lift3():
    r = room('lift3', 'Surface Hatch', 30, 17, 16, 6, wall_all=True)
    r.door('w', 'L', 12, 'blue', 'arena3', 'e')
    r.item('wave', 'waveBeam', 10, 14); r.station('lift', 22, 14, to='rgate')
    return r
lift3()

if __name__ == '__main__':
    out = {}
    for r in Z:
        d = r.emit(); out[d['id']] = d
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'js', 'rooms', 'zone3.js')
    src = "/* GENERATED by tools/zone3_gen.py: zone 3 room layouts, doors, items, stations and moving platforms. */\n(function (G) {\n  G.rooms = G.rooms || {};\n  Object.assign(G.rooms, " + json.dumps(out, separators=(',', ':')) + ");\n})((window.SGS = window.SGS || {}));\n"
    open(path, 'w', encoding='utf-8').write(src)
    print('wrote', len(src), 'rooms', len(out))
