"""Zone 1 boss, the Mossback Warden: a giant armoured beetle, 124 x 80, facing right. Ramp = crimson (o,1-4); glow seams use gold; moss uses A-F; core uses energy letters."""
import math
from art_kit import *

W, H = 124, 80
CX, CY, RX, RY = 48.0, 57.0, 47.0, 45.0
SEAMS = [12, 25, 38, 51, 64, 77]

def dome_y(x):
    nx = (x - CX) / RX
    return CY - RY * math.sqrt(max(0.0, 1 - nx * nx)) if abs(nx) < 1 else CY

def leg(cv, hip, knee, foot, w, ramp):
    cv.shape(tube([hip, knee], w, w * 0.9), ramp, 'o')                       # thigh
    cv.shape(tube([knee, foot], w * 0.8, w * 0.5), ramp, 'o')                # shin
    cv.shape(ell(knee[0], knee[1], w * 0.95, w * 0.95), ramp, 'o')           # armoured knee joint
    cv.shape(poly([(knee[0] - 3, knee[1] - 3), (knee[0] + 1, knee[1] - 12), (knee[0] + 4, knee[1] - 2)]), ramp, 'o')
    cv.shape(poly([(foot[0] - 2, foot[1] - 3), (foot[0] + 8, foot[1] + 1), (foot[0] + 3, foot[1] + 2), (foot[0] - 3, foot[1] + 1)]), ramp, 'o', bevel=False)       # hooked claw
    cv.put(foot[0] + 7, foot[1] + 1, 'w')

def legs(cv, phase):
    far = [(26, 0), (52, 2), (78, 1)]; near = [(14, 2), (42, 0), (66, 3)]
    for (x, ph) in far:
        lift = 4 if (phase + ph) % 4 in (1, 2) else 0
        leg(cv, (x + 4, 52), (x - 6, 62 - lift), (x - 9, 76 - lift), 4, 'ooo1')
    for (x, ph) in near:
        lift = 6 if (phase + ph) % 4 in (1, 2) else 0
        leg(cv, (x + 8, 54), (x - 8, 65 - lift), (x - 12, 77 - lift), 6, 'o123')

def shell(cv, open_core=False, glow=0, dazed=False):
    inside = lambda x, y: ((x - CX) / RX) ** 2 + ((y - CY) / RY) ** 2 <= 1 and y <= 58
    cut = (lambda x, y: ((x - 28) / 16.0) ** 2 + ((y - 26) / 9.0) ** 2 <= 1) if open_core else (lambda x, y: False)
    cv.shape(minus(inside, cut), 'o123', 'o', light=lit(CX, CY, RX, RY, -0.55, -0.6), cells=(10, 3))
    # heavy crown horns along the dome, each with a dark root and a bright tip
    for (x, h, lean) in [(10, 9, -3), (22, 14, -2), (35, 17, -1), (50, 17, 1), (64, 14, 2), (77, 10, 3)]:
        y = dome_y(x)
        if open_core and 10 < x < 46 and y < 40: continue
        cv.shape(poly([(x - 5, y + 6), (x + lean - 1, y - h), (x + lean + 1, y - h), (x + 5, y + 5)]), 'o123', 'o')
        cv.put(x + lean, y - h + 1, '4')
    # plate seams: dark grooves, a hot ember line running through them
    for sx in SEAMS:
        pts = []
        for y in range(12, 57, 3):
            x = sx - 0.22 * (CY - y)
            if inside(x, y) and not cut(x, y): pts.append((round(x), y))
        if len(pts) < 3: continue
        for a, b in zip(pts, pts[1:]): cv.line(a[0], a[1], b[0], b[1], 'o', 2)
        if glow: cv.crack(pts[1:-1], 'Y' if glow > 1 else 'y', 'y' if glow > 1 else 'k', 'k', 1)
        else:
            for (x, y) in pts[2:-1:2]: cv.put(x, y, 'k')
    # scars: pale gashes across the shell
    for (x0, y0, x1, y1) in [(18, 30, 30, 22), (56, 28, 68, 36), (70, 20, 76, 28)]:
        cv.line(x0, y0, x1, y1, '4', 1)
        cv.line(x0, y0 + 1, x1, y1 + 1, 'o', 1)
    # armoured skirt: overlapping plates with hooked spikes
    for i, x in enumerate(range(4, 92, 11)):
        cv.shape(poly([(x, 53), (x + 12, 53), (x + 13, 62), (x + 6, 66 + (i % 2) * 3), (x - 1, 62)]), 'oo12', 'o')
        cv.put(x + 6, 58, 'k'); cv.put(x + 3, 56, '3')
    # moss and thorn vines
    for (mx, my, mr) in [(24, 22, 5), (44, 14, 6), (62, 19, 4), (18, 38, 3), (80, 34, 3)]:
        for dy in range(-mr, mr + 1):
            for dx in range(-mr, mr + 1):
                x, y = mx + dx, my + dy
                if dx * dx + dy * dy <= mr * mr and inside(x, y) and not cut(x, y) and hash2(x, y, 4) > 0.3:
                    cv.put(x, y, 'ABCD'[int(hash2(x, y, 6) * 4) % 4])
    for (vx, vy, vl) in [(34, 44, 10), (60, 46, 8), (74, 44, 9), (14, 46, 7)]:
        for i in range(vl):
            cv.put(vx + (1 if i % 4 == 2 else 0), vy + i, 'C' if i % 3 else 'D')
        cv.put(vx + 2, vy + vl - 1, 'F'); cv.put(vx - 1, vy + vl - 2, 'F')
    if open_core:
        # broken shell: jagged bone teeth around a raw hole, the core glowing inside
        for k in range(16):
            a = k / 16.0 * 6.283; x = 28 + math.cos(a) * 19; y = 26 + math.sin(a) * 10.4
            cv.shape(poly([(x - 2.6, y - 0.5), (x + math.cos(a) * 5, y + math.sin(a) * 5 - 1), (x + 2.6, y + 0.5)]), 'o234', 'o', bevel=False)
        cv.shape(ell(28, 26, 15.5, 8.4), 'obnU', 'o', bevel=False)
        pulse = 1 if glow else 0
        cv.shape(ell(28, 26, 12.5 - pulse, 6.6 - pulse * 0.4), 'dgeE', 'd', light=lit(28, 26, 12, 7, -0.3, -0.5))
        cv.shape(ell(28, 26, 6.5, 3.4), 'eEhh', None, bevel=False)
        cv.put(22, 24, 'h'); cv.put(23, 24, 'h'); cv.put(34, 28, 'E')
        for (x, y, l) in [(16, 30, 6), (40, 31, 5), (28, 34, 7)]:                      # veins running out of the hole
            cv.line(x, y, x + (4 if x < 28 else -4), y + l, 'U', 1)

def head(cv, state='closed', dx=0, dy=0, glow=0):
    ox, oy = 80 + dx, 24 + dy
    # antennae: thick and barbed, swept back over the shell
    for (ax, ay, bx, by) in [(ox + 14, oy + 4, ox + 22, oy - 14), (ox + 18, oy + 6, ox + 30, oy - 6)]:
        cv.line(ax, ay, bx, by, 'o', 3); cv.line(ax, ay, bx, by, '2', 1)
        for t in (0.4, 0.7):
            x = ax + (bx - ax) * t; y = ay + (by - ay) * t; cv.line(round(x), round(y), round(x) - 4, round(y) - 1, 'o', 2)
    # swept-back horns on the brow
    cv.shape(poly([(ox + 8, oy + 5), (ox - 9, oy - 12), (ox - 4, oy - 2), (ox + 12, oy + 9)]), 'o123', 'o')
    cv.shape(poly([(ox + 16, oy + 3), (ox + 8, oy - 14), (ox + 14, oy - 6), (ox + 24, oy + 6)]), 'o123', 'o')
    # skull: a heavy wedge with plated cheeks
    sk = poly([(ox - 4, oy + 10), (ox + 8, oy + 2), (ox + 26, oy + 3), (ox + 38, oy + 14), (ox + 41, oy + 27), (ox + 34, oy + 36), (ox + 14, oy + 38), (ox - 2, oy + 30)])
    cv.shape(sk, 'o123', 'o', light=lit(ox + 18, oy + 20, 24, 20, -0.5, -0.6), cells=(6, 8))
    cv.shape(poly([(ox + 3, oy + 11), (ox + 32, oy + 8), (ox + 36, oy + 14), (ox + 2, oy + 17)]), 'oo1o', 'o', bevel=False)      # heavy brow ridge in shadow
    cv.shape(poly([(ox - 3, oy + 26), (ox - 14, oy + 36), (ox + 4, oy + 33)]), 'o112', 'o')                                     # cheek spikes
    cv.shape(poly([(ox + 8, oy + 36), (ox + 4, oy + 46), (ox + 16, oy + 38)]), 'o112', 'o')
    if state == 'dazed':
        cv.line(ox + 14, oy + 14, ox + 30, oy + 18, 'o', 2); cv.line(ox + 12, oy + 24, ox + 24, oy + 26, 'o', 1)
        cv.line(ox + 18, oy + 12, ox + 22, oy + 20, 'k', 1)
    else:
        e = glow * 0.7
        cv.shape(poly([(ox + 14, oy + 15), (ox + 34, oy + 12), (ox + 30, oy + 22 + e), (ox + 18, oy + 22 + e)]), 'kkYY', 'o', bevel=False)       # slanted blazing eye
        cv.shape(poly([(ox + 21, oy + 14.5), (ox + 29, oy + 13.5), (ox + 28, oy + 19), (ox + 23, oy + 19.5)]), 'YwwW', None, bevel=False)
        cv.rect(ox + 25, oy + 14, ox + 26, oy + 20, 'q')
        cv.eye(ox + 8, oy + 22, 2.6, 2.0, 'Yw', 'q', 'yk', slit=False)
    # mandibles: huge hooked pincers with serrated inner edges; they part when roaring
    gap = {'closed': 0, 'open': 13, 'low': 3, 'dazed': 7}.get(state, 0)
    mx, my = ox + 36, oy + 26
    cv.shape(poly([(mx - 4, my - 6 - gap // 2), (mx + 14, my - 4 - gap), (mx + 26, my + 4 - gap), (mx + 28, my + 12 - gap), (mx + 20, my + 8 - gap), (mx + 8, my + 4 - gap // 2), (mx - 4, my + 4 - gap // 2)]), 'o123', 'o')
    cv.shape(poly([(mx - 4, my + 8 + gap // 2), (mx + 8, my + 10 + gap // 2), (mx + 20, my + 16 + gap), (mx + 28, my + 10 + gap), (mx + 26, my + 20 + gap), (mx + 14, my + 22 + gap), (mx - 4, my + 17 + gap // 2)]), 'o123', 'o')
    for k in range(4):                                                                                             # fangs along both jaws
        cv.shape(poly([(mx + 2 + k * 5, my + 4 - gap // 2), (mx + 4 + k * 5, my + 10 - gap // 2 + (gap > 5) * 3), (mx + 6 + k * 5, my + 4 - gap // 2)]), 'wwww', 'o', bevel=False)
        cv.shape(poly([(mx + 2 + k * 5, my + 10 + gap // 2), (mx + 4 + k * 5, my + 4 + gap // 2 - (gap > 5) * 3), (mx + 6 + k * 5, my + 10 + gap // 2)]), 'wwww', 'o', bevel=False)
    if state == 'open':
        cv.rect(mx + 2, my + 3, mx + 18, my + 12, 'k'); cv.rect(mx + 5, my + 6, mx + 15, my + 9, 'y'); cv.rect(mx + 8, my + 7, mx + 12, my + 8, 'Y')

def beetle(phase=0, state='closed', head_dy=0, head_dx=0, glow=0, open_core=False, dazed=False):
    cv = Cv(W, H)
    legs(cv, phase)
    shell(cv, open_core, glow, dazed)
    head(cv, 'dazed' if dazed else state, head_dx, head_dy, glow)
    if dazed:
        for (x, y) in [(8, 10), (20, 6), (46, 4), (60, 8), (95, 14), (100, 40)]: cv.put(x, y, 'w'); cv.put(x + 1, y + 1, 'Y')
    return cv.rows()

def build():
    walk = [beetle(p, 'closed', head_dy=(1 if p in (1, 2) else 0)) for p in range(4)]
    rear = beetle(1, 'open', head_dy=-6, head_dx=-1)
    tele = [beetle(0, 'low', head_dy=4, glow=1 + i) for i in range(2)]
    charge = [beetle(i * 2, 'low', head_dy=7, head_dx=2, glow=2) for i in range(2)]
    stun = [beetle(0, 'closed', head_dy=9, glow=i, open_core=True, dazed=True) for i in range(2)]
    return {'walk': walk, 'rear': rear, 'tele': tele, 'charge': charge, 'stun': stun}

if __name__ == '__main__':
    for r in beetle(0): print(r)
