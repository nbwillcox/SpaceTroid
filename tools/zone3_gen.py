r"""Zone 3 (Magma Forge) room layouts -> js/rooms/zone3.js. Extra tiles: L lava (needs the heat suit), x wave-beam crystal block, D dash block (dash into it); spawns n cinder crawler, h ember hopper, e ember turret, z magmite (marker row = the row above the lava surface)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from room_kit import Room, BS

Z = []
def room(*a, **k):
    r = Room(*a, **k); r.zone = 3; Z.append(r); return r

def fgate():
    r = room('fgate', 'Forge Gate', 30, 17, 0, 6, solid=True, wall_all=True)
    r.cave([(0, 13), (6, 15)], [(0, 2), (6, 5), (14, 3), (22, 2)])
    r.spawn('P', 2, 12); r.door('e', 'R', 12, 'blue', 'ember', 'w')
    r.fill(12, 14, 15, 15, 'L'); r.fill(22, 12, 25, 12, '#'); r.on('n', 20)
    r.hang(9, 3, 1); r.hang(18, 2, 2)
    return r
fgate()

def ember():
    r = room('ember', 'Ember Hall', 60, 34, 1, 6, solid=True)
    r.cave([(0, 15), (10, 13), (18, 15), (36, 13), (44, 15), (47, 17, 's'), (50, 15, 's')], [(0, 2), (8, 5), (18, 3), (24, 6), (32, 3), (40, 5), (48, 2)], y1=16)
    r.door('w', 'L', 12, 'blue', 'fgate', 'e'); r.door('e', 'R', 12, 'blue', 'beacon3', 'w')
    r.station('map', 5, 14)
    r.fill(20, 14, 33, 15, 'L'); r.plat(22, 26, 11); r.plat(29, 33, 11)
    r.on('n', 7); r.on('n', 54); r.on('h', 56); r.spawn('z', 27, 13); r.spawn('z', 31, 13); r.on('e', 39)
    r.wall(12, 2, 44, 14)
    # forge cellar: reached through the gap at x 47..49; lava runs along the west half, and a wall of dash blocks seals a tank at the far end
    r.cave([(0, 32)], [(0, 19), (4, 22), (12, 19), (20, 22), (28, 19), (41, 17, 's'), (53, 17), (54, 19, 's'), (58, 21)], y0=17, y1=33)
    r.stair(47, 49, 32)
    r.fill(14, 31, 38, 32, 'L')
    r.fill(1, 19, 9, 31, '#'); r.fill(2, 29, 8, 31, '.'); r.fill(9, 29, 9, 31, 'D'); r.item('mtankE', 'missileTank', 3, 31)
    r.on('n', 12); r.on('h', 41); r.spawn('z', 20, 30); r.spawn('z', 30, 30); r.on('e', 52)
    r.door('eb', 'R', 29, 'blue', 'slagcell', 'w')
    r.wall(1, 18, 58, 32, ragged=False)
    return r
ember()

def beacon3():
    r = room('beacon3', 'Furnace Beacon', 20, 17, 3, 6, solid=True, wall_all=True)
    r.cave([(0, 15)], [(0, 6), (18, 6)])
    r.door('w', 'L', 12, 'blue', 'ember', 'e'); r.door('e', 'R', 12, 'blue', 'smelter', 'w')
    r.station('save', 10, 14)
    r.fill(5, 6, 6, 8, '#'); r.fill(13, 6, 14, 8, '#')
    return r
beacon3()

def smelter():
    r = room('smelter', 'The Smelter', 60, 17, 4, 6, solid=True, wall_all=True)
    r.cave([(0, 15), (6, 13), (11, 15), (50, 13), (55, 15)], [(0, 2), (8, 4), (14, 2), (48, 4), (54, 2)])
    r.door('w', 'L', 12, 'blue', 'beacon3', 'e'); r.door('e', 'R', 12, 'blue', 'foundry', 'w')
    r.fill(12, 14, 47, 15, 'L')
    r.fill(15, 8, 18, 9, '#'); r.item('tank4', 'energyTank', 16, 7)       # an island above the vat; ride the lift up
    r.mover('x', 216, 736, 48, 0.9, 222); r.mover('y', 128, 222, 48, 0.7, 232)
    r.spawn('z', 30, 13); r.spawn('z', 40, 13); r.on('e', 51); r.on('n', 7); r.on('n', 57)
    return r
smelter()

def foundry():
    r = room('foundry', 'Old Foundry', 30, 17, 6, 6, solid=True, wall_all=True)
    r.cave([(0, 15), (12, 12), (18, 15)], [(0, 2), (5, 5), (12, 3), (20, 5), (26, 2)])
    r.door('w', 'L', 12, 'blue', 'smelter', 'e'); r.door('e', 'R', 12, 'blue', 'chimney', 'wl')
    r.fill(4, 14, 7, 15, 'L'); r.fill(20, 14, 23, 15, 'L')
    r.item('space', 'spaceJump', 13, 11)
    r.spawn('z', 5, 13); r.spawn('z', 21, 13); r.on('h', 3); r.on('h', 26)
    return r
foundry()

def chimney():
    r = room('chimney', 'Chimney', 30, 34, 7, 5, solid=True, wall_all=True)
    r.cave([(0, 32)], [(0, 2)])
    r.door('wl', 'L', 29, 'blue', 'foundry', 'e'); r.door('wh', 'L', 2, 'blue', 'anvil', 'w')
    for (x0, x1, y) in [(4, 8, 29), (10, 14, 26), (16, 20, 21), (22, 26, 18), (16, 20, 13), (10, 14, 10), (4, 8, 5)]: r.plat(x0, x1, y)
    r.fill(1, 5, 3, 5, '#')
    r.fill(1, 12, 2, 19, '#'); r.fill(1, 23, 3, 28, '#'); r.fill(26, 9, 28, 15, '#'); r.fill(26, 24, 28, 28, '#'); r.fill(24, 25, 25, 27, '#')
    r.spawn('z', 14, 31); r.spawn('e', 25, 31); r.spawn('n', 20, 31)
    r.hang(14, 4, 2); r.hang(22, 3, 2)
    return r
chimney()

def anvil():
    r = room('anvil', 'The Anvil', 30, 17, 8, 6, solid=True, wall_all=True)
    r.cave([(0, 15), (11, 12), (18, 15)], [(0, 2), (6, 4), (20, 2), (25, 5)])
    r.door('w', 'L', 12, 'blue', 'chimney', 'wh'); r.door('e', 'R', 12, 'blue', 'slag', 'w')
    r.item('dash', 'dashBoots', 13, 11)
    r.fill(24, r.cl[24], 24, 14, 'D')                    # a dash block seals the whole passage, floor to roof
    r.on('h', 5); r.on('h', 21); r.on('e', 27)
    return r
anvil()

def slag():
    r = room('slag', 'Slag Works', 60, 17, 9, 6, solid=True, wall_all=True)
    r.cave([(0, 15)], [(0, 2), (8, 4), (22, 6), (30, 3), (44, 5), (54, 2)])
    r.door('w', 'L', 12, 'blue', 'anvil', 'e'); r.door('e', 'R', 12, 'blue', 'crucible', 'w')
    r.fill(14, 14, 20, 15, 'L'); r.fill(34, 14, 40, 15, 'L'); r.plat(15, 19, 11); r.plat(35, 39, 11)
    r.ramp(23, 15, 3, True); r.fill(26, 12, 28, 14, '#'); r.ramp(29, 15, 3, False)
    r.fill(46, r.cl[46], 46, 14, 'D'); r.item('mtank6', 'missileTank', 52, 14)      # the room's last stretch is walled off by dash blocks
    r.on('n', 10); r.on('n', 33); r.on('h', 22); r.spawn('e', 27, 11); r.spawn('z', 17, 13); r.spawn('z', 37, 13); r.on('e', 55)
    return r
slag()

def crucible():
    r = room('crucible', 'The Crucible', 60, 17, 11, 6, solid=True, wall_all=True)
    r.cave([(0, 15)], [(0, 2), (8, 4), (28, 3), (40, 2)])
    r.door('w', 'L', 12, 'blue', 'slag', 'e'); r.door('e', 'R', 12, 'blue', 'pre3', 'w')
    r.fill(14, 14, 26, 15, 'L'); r.plat(15, 18, 11); r.plat(21, 25, 10)
    r.fill(34, 12, 39, 14, '#'); r.fill(44, 12, 46, 14, '#')
    r.fill(40, 8, 52, 8, '#'); r.fill(40, 9, 40, 11, 'x'); r.fill(41, 12, 52, 12, '#'); r.fill(52, 9, 52, 11, '#'); r.item('mtank7', 'missileTank', 46, 11)   # crystal alcove: wave beam only
    r.spawn('e', 35, 11); r.on('n', 8); r.on('n', 31); r.on('h', 54); r.spawn('z', 20, 13); r.on('e', 56)
    r.hang(30, 3, 2); r.hang(10, 2, 1)
    return r
crucible()

def pre3():
    r = room('pre3', 'Overseer Approach', 30, 17, 13, 6, solid=True, wall_all=True)
    r.cave([(0, 15)], [(0, 2), (3, 5), (26, 2)])
    r.door('w', 'L', 12, 'blue', 'crucible', 'e'); r.door('e', 'R', 12, 'blue', 'arena3', 'w')
    r.station('save', 12, 14)
    r.fill(7, 5, 8, 9, '#'); r.fill(21, 5, 22, 9, '#')
    return r
pre3()

def arena3():
    r = room('arena3', 'Cinder Pit', 40, 17, 14, 6, solid=True, wall_all=True)
    r.cave([(0, 14)], [(0, 2), (2, 5), (8, 3), (14, 2), (26, 2), (32, 3), (38, 5)])
    r.door('w', 'L', 11, 'blue', 'pre3', 'e'); r.door('e', 'R', 11, 'boss', 'lift3', 'w')
    r.fill(9, 14, 16, 14, 'L'); r.fill(23, 14, 30, 14, 'L')
    r.plat(11, 14, 11); r.plat(25, 28, 11)
    r.spawn('K', 20, 13)
    return r
arena3()

def lift3():
    r = room('lift3', 'Surface Hatch', 30, 17, 16, 6, solid=True, wall_all=True)
    r.cave([(0, 15), (5, 14), (9, 13), (14, 15)], [(0, 2), (4, 4), (16, 2), (24, 4)])
    r.door('w', 'L', 12, 'blue', 'arena3', 'e')
    r.item('wave', 'waveBeam', 10, 12); r.station('lift', 22, 14, to='rgate')
    return r
lift3()

def slagcell():
    r = room('slagcell', 'Slag Cell', 30, 17, 3, 7, solid=True, wall_all=True)
    r.style = ['pipes', 'glow']
    r.cave([(0, 15)], [(0, 2), (6, 5), (16, 3), (22, 5)])
    r.door('w', 'L', 12, 'blue', 'ember', 'eb')
    r.fill(7, 14, 13, 15, 'L'); r.plat(8, 12, 11)
    r.fill(17, r.cl[17], 17, 14, 'D')                    # a dash block seals the rest of the cell, floor to roof
    r.item('mtankD', 'missileTank', 24, 14)
    r.on('n', 4); r.on('h', 21); r.spawn('z', 10, 13); r.on('n', 26)
    return r
slagcell()

if __name__ == '__main__':
    import build_world; build_world.main()
