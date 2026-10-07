"""Zone 2 (Cryo Vaults) room layouts -> js/rooms/zone2.js. Extra tiles: i slippery ice floor; spawns f frostling, q wisp (freeze it with the ice beam to make a stepping stone), t shard turret, v icicle (marker on the first row below the ceiling)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from room_kit import Room, BS

Z = []
def room(*a, **k):
    r = Room(*a, **k); r.zone = 2; Z.append(r); return r

def gate():
    r = room('gate', 'Frozen Landing', 30, 17, 0, 4, solid=True, wall_all=True)
    r.cave([(0, 13), (8, 15)], [(0, 2), (5, 4), (11, 2)])
    r.spawn('P', 3, 12); r.door('e', 'R', 12, 'blue', 'drift', 'w')
    r.surf(9, 19); r.fill(22, 12, 25, 12, '#')
    r.on('f', 17); r.top(14, 'v'); r.top(21, 'v')
    return r
gate()

def drift():
    r = room('drift', 'Snowdrift Hall', 60, 17, 1, 4, solid=True)
    r.cave([(0, 15), (10, 12), (20, 15), (36, 12), (48, 15)], [(0, 2), (8, 4), (18, 2), (26, 3), (34, 6), (46, 3), (52, 2)])
    r.door('w', 'L', 12, 'blue', 'gate', 'e'); r.door('e', 'R', 12, 'blue', 'beacon2', 'w')
    r.station('map', 5, 14)
    r.surf(10, 16); r.surf(36, 44); r.surf(50, 56); r.fill(28, 15, 30, 15, '^')
    r.plat(26, 32, 12); r.plat(52, 56, 11)
    for x in (4, 22, 30, 48): r.top(x, 'v')
    r.on('f', 12); r.on('f', 50); r.spawn('q', 30, 8); r.on('t', 40)
    r.wall(14, 2, 40, 14)
    return r
drift()

def beacon2():
    r = room('beacon2', 'Cold Beacon', 20, 17, 3, 4, solid=True, wall_all=True)
    r.cave([(0, 15)], [(0, 8), (4, 6), (7, 4), (9, 2), (11, 4), (14, 6), (17, 8)])
    r.door('w', 'L', 12, 'blue', 'drift', 'e'); r.door('e', 'R', 12, 'blue', 'gallery', 'w')
    r.station('save', 10, 14); r.top(5, 'v'); r.top(14, 'v')
    return r
beacon2()

def gallery():
    r = room('gallery', 'Crystal Gallery', 60, 17, 4, 4, solid=True)
    r.cave([(0, 15)], [(0, 2), (10, 4), (22, 2), (34, 5), (46, 3), (52, 2)])
    r.door('w', 'L', 12, 'blue', 'beacon2', 'e'); r.door('e', 'R', 12, 'blue', 'chasm', 'w'); r.door('n', 'R', 3, 'blue', 'icecache', 'w')
    r.ramp(16, 15, 2, True); r.fill(18, 13, 20, 14, '#'); r.ramp(21, 15, 2, False)
    r.ramp(36, 15, 2, True); r.fill(38, 13, 40, 14, '#'); r.ramp(41, 15, 2, False)
    r.surf(6, 14); r.surf(26, 35)
    r.plat(8, 12, 12); r.plat(24, 28, 12)
    r.plat(44, 48, 12); r.plat(49, 53, 9); r.fill(54, 6, 58, 6, '#')
    r.item('mtank4', 'missileTank', 51, 8)
    r.spawn('t', 19, 12); r.spawn('t', 39, 12); r.on('f', 10); r.on('f', 31); r.spawn('q', 26, 7); r.spawn('q', 45, 8)
    for x in (12, 26, 44): r.top(x, 'v')
    r.hang(30, 3, 2); r.hang(16, 2, 1)
    r.wall(10, 2, 50, 14)
    return r
gallery()

def icecache():
    r = room('icecache', 'Ice Cache', 30, 17, 5, 5, solid=True, wall_all=True)
    r.cave([(0, 15), (10, 12), (18, 15)], [(0, 2), (6, 4), (10, 2), (20, 4)])
    r.door('w', 'L', 12, 'blue', 'gallery', 'n')
    r.item('ice', 'iceBeam', 12, 11)
    r.door('e', 'R', 12, 'blue', 'shelf', 'w')
    r.on('t', 4); r.on('f', 23); r.top(13, 'v'); r.top(24, 'v')
    return r
icecache()

def chasm():
    r = room('chasm', 'Wisp Chasm', 60, 17, 6, 4, solid=True, wall_all=True)
    r.cave([(0, 15)], [(0, 2), (6, 5), (13, 3), (24, 2), (36, 4), (46, 2)])
    r.door('w', 'L', 12, 'blue', 'gallery', 'e'); r.door('e', 'R', 12, 'blue', 'bridge', 'w')
    r.fill(9, 15, 49, 15, '^')
    r.plat(10, 15, 12); r.plat(18, 23, 11); r.plat(26, 31, 13); r.plat(34, 39, 12); r.plat(42, 49, 13)    # gaps of two tiles; the last platform runs down to the floor at the east end
    r.fill(30, 8, 33, 8, '#'); r.item('tank3', 'energyTank', 31, 7)     # high ledge: freeze a wisp to reach it
    r.spawn('q', 28, 11); r.spawn('q', 22, 8); r.on('t', 52); r.on('f', 4)
    for x in (16, 28, 40): r.top(x, 'v')
    r.hang(8, 3, 2); r.hang(19, 2, 1); r.hang(38, 3, 2)
    return r
chasm()

def bridge():
    r = room('bridge', 'Frozen Bridge', 60, 34, 8, 4, solid=True, wall_all=True)
    r.cave([(0, 15), (22, 17, 's'), (25, 15, 's'), (38, 17, 's'), (41, 15, 's')], [(0, 2), (6, 5), (12, 3), (24, 6), (36, 3), (44, 5), (52, 2)], y1=16)
    r.door('w', 'L', 12, 'blue', 'chasm', 'e'); r.door('e', 'R', 12, 'blue', 'shaft2', 'wl')
    r.surf(2, 57)
    r.ramp(12, 15, 2, True); r.fill(14, 13, 16, 14, '#'); r.ramp(17, 15, 2, False)
    r.fill(30, 12, 32, 14, '#')
    r.ramp(44, 15, 2, True); r.fill(46, 13, 48, 14, '#'); r.ramp(49, 15, 2, False)
    r.spawn('t', 15, 12); r.spawn('t', 31, 11); r.spawn('t', 47, 12); r.on('f', 20); r.on('f', 35)
    r.g[14][30] = 'B'; r.g[14][31] = '.'; r.item('mtank5', 'missileTank', 31, 14)      # a ball nook in the middle pillar, sealed by a bomb block
    r.wall(1, 2, 58, 16, ragged=False)
    # gorge: the deck has two gaps (x 22..24 and 38..40); the cavern below is lined with ice, and ledges climb back out through either gap
    r.cave([(0, 32)], [(0, 19), (4, 22), (12, 19), (15, 17, 's'), (47, 19, 's'), (50, 22), (56, 19)], y0=17, y1=33)
    r.surf(2, 57)
    r.stair(22, 24, 32); r.stair(38, 40, 32)
    r.fill(1, 19, 9, 31, '#'); r.fill(2, 29, 8, 31, '.'); r.fill(9, 29, 9, 31, 'B'); r.item('mtankG', 'missileTank', 3, 31)
    r.door('eb', 'R', 29, 'blue', 'grotto', 'w')
    r.on('f', 14); r.on('f', 30); r.on('f', 46); r.on('t', 52)
    r.wall(1, 18, 58, 32, ragged=False)
    return r
bridge()

def shaft2():
    r = room('shaft2', 'Frostfall', 30, 34, 10, 3, solid=True, wall_all=True)
    r.cave([(0, 32)], [(0, 2)])
    r.door('wl', 'L', 29, 'blue', 'bridge', 'e'); r.door('eh', 'R', 3, 'blue', 'pre2', 'w')
    for (x0, x1, y) in [(4, 8, 29), (10, 14, 26), (16, 20, 23), (22, 26, 20), (16, 20, 17), (10, 14, 14), (14, 18, 9), (20, 27, 6)]: r.plat(x0, x1, y)
    r.fill(20, 6, 28, 6, '#')
    r.fill(1, 12, 2, 18, '#'); r.fill(1, 22, 3, 27, '#'); r.fill(25, 22, 28, 26, '#'); r.fill(26, 10, 28, 14, '#'); r.fill(1, 6, 8, 7, '#')
    r.spawn('q', 12, 12)          # the gap between the 14 and 9 ledges: freeze this wisp and use it as a step
    r.spawn('t', 25, 31); r.spawn('f', 8, 31); r.spawn('q', 8, 18)
    for x in (12, 16): r.spawn('v', x, 2)
    r.hang(6, 3, 1); r.hang(12, 2, 1)
    return r
shaft2()

def pre2():
    r = room('pre2', 'Sentinel Approach', 30, 17, 11, 4, solid=True, wall_all=True)
    r.cave([(0, 15), (5, 14), (10, 15), (20, 14), (25, 15)], [(0, 2), (3, 4), (9, 2), (21, 4)])
    r.door('w', 'L', 12, 'blue', 'shaft2', 'eh'); r.door('e', 'R', 12, 'blue', 'arena2', 'w')
    r.station('save', 12, 14); r.spawn('v', 8, 2); r.spawn('v', 18, 2)
    r.fill(14, 5, 15, 7, '#')
    return r
pre2()

def arena2():
    r = room('arena2', 'Rime Hall', 40, 17, 12, 4, solid=True, wall_all=True)
    r.cave([(0, 15)], [(0, 2), (2, 5), (8, 3), (13, 2), (27, 2), (32, 3), (38, 5)])
    r.door('w', 'L', 12, 'blue', 'pre2', 'e'); r.door('e', 'R', 12, 'boss', 'heat', 'w')
    r.plat(5, 9, 11); r.plat(30, 34, 11); r.plat(17, 22, 8)
    r.spawn('K', 28, 14)
    return r
arena2()

def heat():
    r = room('heat', 'Thermal Vault', 30, 17, 14, 4, solid=True, wall_all=True)
    r.cave([(0, 15), (9, 13), (14, 15)], [(0, 2), (4, 4), (16, 2), (24, 3)])
    r.door('w', 'L', 12, 'blue', 'arena2', 'e')
    r.item('heat', 'heatSuit', 10, 12); r.station('lift', 22, 14, to='fgate')
    return r
heat()

def grotto():
    r = room('grotto', 'Glimmer Grotto', 30, 17, 10, 5, solid=True, wall_all=True)
    r.style = ['glow', 'streaks']; r.tone = 0.8
    r.cave([(0, 15)], [(0, 2), (6, 5), (16, 3), (24, 6)])
    r.door('w', 'L', 12, 'blue', 'bridge', 'eb')
    r.surf(1, 28)
    r.fill(7, 15, 10, 15, '^'); r.fill(15, 15, 18, 15, '^')                      # slippery ice between two spike pits: hop the ledges
    r.plat(7, 10, 12); r.plat(15, 18, 12)
    r.fill(22, 12, 27, 14, '#'); r.item('mtankF', 'missileTank', 24, 11)
    r.on('f', 13); r.on('f', 20); r.spawn('t', 27, 11); r.top(5, 'v'); r.top(20, 'v')
    return r
grotto()

def shelf():
    r = room('shelf', 'Frozen Shelf', 60, 17, 6, 5, solid=True, wall_all=True)
    r.style = ['pillars', 'streaks']
    r.cave([(0, 15)], [(0, 2), (10, 5), (24, 3), (38, 2), (54, 4)])
    r.door('w', 'L', 12, 'blue', 'icecache', 'e')
    r.surf(1, 58)
    r.plat(40, 45, 13); r.fill(44, 8, 47, 8, '#'); r.item('tankS', 'energyTank', 45, 7)       # high ledge: freeze the wisp to climb
    r.spawn('q', 42, 11); r.on('f', 10); r.on('f', 30); r.on('t', 54)
    for x in (14, 28, 36): r.top(x, 'v')
    r.hang(20, 3, 2); r.hang(50, 2, 1)
    return r
shelf()

if __name__ == '__main__':
    import build_world; build_world.main()
