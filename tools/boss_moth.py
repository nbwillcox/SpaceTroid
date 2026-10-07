"""Zone 2 boss, the Rimewing Sovereign: a skeletal ice moth, 140 x 100, symmetric, drawn with the teal ramp (o,1-4); eyes use visor letters, the core uses energy letters."""
import math
from art_kit import *

W, H = 140, 100
MX = 70.0                                  # body axis
SH = (61.0, 45.0)                          # left shoulder
DARKEN = {'4': '3', '3': '2', '2': '1', 'V': 'x', 'W': 'V'}

def mirror_into(cv, left):
    """copy the left half of `left` onto cv mirrored on the body axis, one shade darker (light comes from the left)"""
    for y in range(H):
        for x in range(int(MX)):
            c = left.g[y][x]
            if c != '.': cv.put(int(2 * MX - 1 - x), y, DARKEN.get(c, c))
            if c != '.': cv.put(x, y, c)

def wing(cv, base, spread=1.0, ragged=True, dim=0, droop=0):
    """the left wing: a dark ragged membrane stretched between four thick bone fingers, ice crystals growing off the leading edge; base = angle in degrees
    (0 = straight out, 90 = straight up, negative = down)"""
    offs = [38, 13, -12, -36]; lens = [50, 62, 60, 46]
    tips = []; dirs = []
    for o, L in zip(offs, lens):
        phi = math.radians(base + o * spread)
        dx, dy = -math.cos(phi), -math.sin(phi)
        if dy < -0.01: L = min(L, (SH[1] - 3) / -dy)
        if dy > 0.01: L = min(L, (H - 4 - SH[1]) / dy)
        if dx < -0.01: L = min(L, (SH[0] - 2) / -dx)
        tips.append((SH[0] + dx * L, SH[1] + dy * L + droop * L * 0.12)); dirs.append((dx, dy, L))
    mem = [(SH[0] + 2, SH[1] - 2)]
    for i, t in enumerate(tips):
        mem.append(t)
        if i + 1 < len(tips):
            n = tips[i + 1]; mem.append(((t[0] + n[0]) / 2 * 0.74 + SH[0] * 0.26, (t[1] + n[1]) / 2 * 0.74 + SH[1] * 0.26))
    mem.append((SH[0] + 2, SH[1] + 6))
    cv.shape(poly(mem), 'o112' if not dim else 'ooo1', 'o', bevel=False, light=lambda x, y: 0.18 + 0.32 * hash2(int(x) // 2, int(y) // 2, 5) + (0.35 if hash2(int(x), int(y), 9) > 0.93 else 0))
    for (dx, dy, L), t in zip(dirs, tips):                          # veins fanning out between the fingers
        for k in (0.3, 0.5, 0.7, 0.9):
            px, py = SH[0] + dx * L * k, SH[1] + dy * L * k
            cv.line(round(px), round(py), round(px + dy * 4 + dx * 3), round(py - dx * 4 + dy * 3), 'x' if not dim else '1', 1)
    ramp = '2344' if not dim else 'o122'
    for (dx, dy, L), t in zip(dirs, tips):                          # fingers: thick bone, lit from above, ending in hooked claws
        cv.line(round(SH[0]), round(SH[1]), round(t[0]), round(t[1]), 'o', 5)
        cv.line(round(SH[0]), round(SH[1]), round(t[0]), round(t[1]), ramp[1], 3)
        cv.line(round(SH[0]), round(SH[1] - 1), round(t[0]), round(t[1] - 1), ramp[3], 1)
        cv.shape(poly([(t[0] - dy * 3, t[1] + dx * 3), (t[0] + dx * 7, t[1] + dy * 7 + 3), (t[0] + dy * 3, t[1] - dx * 3)]), ramp, 'o', bevel=False)
        cv.put(t[0] + dx * 6, t[1] + dy * 6 + 3, 'w')
    dx, dy, L = dirs[0]; nx, ny = dy, -dx                           # ice crystals growing off the leading edge
    for k in (0.28, 0.46, 0.64, 0.82):
        px, py = SH[0] + dx * L * k, SH[1] + dy * L * k
        cv.shape(poly([(px - dx * 3, py - dy * 3), (px + nx * 9 + dx * 2, py + ny * 9 + dy * 2), (px + dx * 3, py + dy * 3)]), ramp, 'o', bevel=False)
    cv.shape(ell(SH[0], SH[1], 6, 6), ramp, 'o', light=lit(SH[0], SH[1], 6, 6))                  # shoulder joint

def body(cv, state='fly', glow=0, head_dy=0, core_open=False, dim=0):
    # abdomen: segmented, tapering to an icicle stinger
    ay = 66
    for i in range(7):
        r = 8 - i * 0.8; y = ay + i * 4.4
        cv.shape(ell(MX, y, r, 3.4), '1223' if not dim else 'oo11', 'o', light=lit(MX, y, r, 3.4, -0.4, -0.7))
    for i in range(1, 6):                                                                          # barbs down both sides of the abdomen
        y = ay + i * 4.4
        for sg in (-1, 1):
            r = 8 - i * 0.8
            cv.shape(poly([(MX + sg * (r - 1), y - 2.5), (MX + sg * (r + 7 - i * 0.6), y + 3), (MX + sg * (r - 1), y + 1.5)]), '2344', 'o', bevel=False)
    cv.shape(poly([(MX - 3, 94), (MX, 106 - 2), (MX + 3, 94)]), '2344', 'o', bevel=False)
    # thorax: ribcage over a shell, the glowing core behind a cracked plate
    cv.shape(ell(MX, 52, 13, 17), '1234' if not dim else 'oo12', 'o', light=lit(MX, 52, 13, 17, -0.5, -0.6))
    for k in range(5):
        y = 42 + k * 5
        cv.line(round(MX - 11 + abs(k - 2)), y, round(MX - 2), y + 1, 'o', 1); cv.line(round(MX + 11 - abs(k - 2)), y, round(MX + 2), y + 1, 'o', 1)
        cv.put(MX - 8, y - 1, 'w' if not dim else '2')
    for sg in (-1, 1):                                                                              # pauldron spikes
        cv.shape(poly([(MX + sg * 8, 40), (MX + sg * 19, 30), (MX + sg * 15, 44), (MX + sg * 10, 46)]), '2344', 'o')
    cv.shape(ell(MX, 56, 6.5, 8), 'oobn', 'o', bevel=False)                                  # core socket
    if core_open or glow:
        cv.shape(ell(MX, 56, 5.2, 6.4), 'dgeE', 'd', light=lit(MX, 56, 5, 6, -0.3, -0.5))
        cv.shape(ell(MX, 56, 2.6, 3.2), 'eEhh', None, bevel=False)
    else:
        cv.shape(ell(MX, 56, 4.2, 5.4), 'obUn', None, bevel=False)
        cv.put(MX, 56, 'e'); cv.put(MX - 1, 55, 'd')
    # crooked legs
    for (sx, sy, k) in [(58, 54, -1), (56, 60, -1), (59, 66, -1)]:
        for sg in (1, -1):
            x0 = MX + sg * (MX - sx) * -1
            cv.line(round(MX + sg * (MX - sx)), sy, round(MX + sg * (MX - sx + 8)), sy + 8, 'o', 2)
            cv.line(round(MX + sg * (MX - sx + 8)), sy + 8, round(MX + sg * (MX - sx + 6)), sy + 18, 'o', 2)
            cv.put(MX + sg * (MX - sx + 6), sy + 19, 'w')
    # head: a horned skull with a crown of icicles
    hy = 25 + head_dy
    for (ax, ay2, bx, by2) in [(MX - 7, hy - 6, MX - 26, hy - 24), (MX + 7, hy - 6, MX + 26, hy - 24)]:           # long whip antennae
        cv.line(round(ax), round(ay2), round(bx), round(by2), 'o', 3); cv.line(round(ax), round(ay2), round(bx), round(by2), '3', 1)
        cv.shape(poly([(bx - 2, by2), (bx, by2 - 8), (bx + 2, by2)]), '2344', 'o', bevel=False)
    for (sx, h2) in [(-7, 11), (0, 14), (7, 11)]:                                                                  # crown
        cv.shape(poly([(MX + sx - 3, hy - 7), (MX + sx, hy - 7 - h2), (MX + sx + 3, hy - 7)]), '2344', 'o')
    cv.shape(ell(MX, hy, 14, 12), '1234' if not dim else 'oo12', 'o', light=lit(MX, hy, 14, 12, -0.5, -0.6))
    cv.shape(poly([(MX - 12, hy - 3), (MX, hy - 5), (MX + 12, hy - 3), (MX + 10, hy + 1), (MX, hy - 1), (MX - 10, hy + 1)]), 'ooo1', 'o', bevel=False)   # brow
    if state == 'stun':
        cv.line(round(MX - 9), hy + 2, round(MX - 3), hy + 4, 'o', 2); cv.line(round(MX + 9), hy + 2, round(MX + 3), hy + 4, 'o', 2)
    elif dim:
        cv.put(MX - 6, hy + 2, '2'); cv.put(MX + 6, hy + 2, '2')
    else:
        for sg in (-1, 1):                                                                                           # blazing eyes: a big slanted pair plus a cluster
            cv.shape(poly([(MX + sg * 3, hy - 1), (MX + sg * 13, hy - 4), (MX + sg * 11, hy + 5), (MX + sg * 4, hy + 5)]), 'qxVW', 'o', bevel=False)
            cv.put(MX + sg * 8, hy - 1, 'W'); cv.put(MX + sg * 7, hy, 'W'); cv.put(MX + sg * 8, hy, 'W')
            cv.put(MX + sg * 3, hy - 4, 'V'); cv.put(MX + sg * 5, hy - 5, 'V')
    # mandibles: two curved fangs, parting when it fires
    gap = {'fly': 1, 'shoot': 6, 'stun': 4, 'dive': 0}.get(state, 1)
    for sg in (-1, 1):
        cv.shape(poly([(MX + sg * 3, hy + 9), (MX + sg * (8 + gap), hy + 13), (MX + sg * (13 + gap), hy + 27), (MX + sg * (9 + gap), hy + 24), (MX + sg * 2, hy + 13)]), '2344', 'o')
        for k in range(3): cv.put(MX + sg * (7 + gap + k * 0.8), hy + 15 + k * 3, 'w')
        cv.put(MX + sg * (12 + gap), hy + 26, 'w')
    if state == 'shoot':
        cv.shape(ell(MX, hy + 17, 5, 5), 'VWWW', 'x', bevel=False); cv.shape(ell(MX, hy + 17, 2.2, 2.2), 'wwww', None, bevel=False)

def moth(base=15, state='fly', glow=0, head_dy=0, spread=1.0, core_open=False, dim=0, droop=0):
    cv = Cv(W, H)
    left = Cv(W, H)
    wing(left, base, spread, True, dim, droop)
    mirror_into(cv, left)
    body(cv, state, glow, head_dy, core_open, dim)
    return cv.rows()

def build():
    fly = [moth(b, 'fly', head_dy=(1 if i in (1, 2) else 0)) for i, b in enumerate([40, 22, -4, 22])]
    shoot = [moth(24, 'shoot', glow=1, head_dy=-1) for i in range(2)]
    shoot[1] = moth(28, 'shoot', glow=1, head_dy=-2)
    dive = moth(62, 'dive', head_dy=3, spread=0.5)
    stun = [moth(-48, 'stun', glow=i, head_dy=5, spread=0.7, core_open=True, dim=1, droop=1) for i in range(2)]
    dead = moth(-62, 'stun', head_dy=7, spread=0.5, dim=1, droop=2)
    return {'fly': fly, 'shoot': shoot, 'dive': dive, 'stun': stun, 'dead': dead}

if __name__ == '__main__':
    for r in moth(15): print(r)
