"""The hero's upper body as a rig: ONE painted body (head, shoulders, chest; cut from the forward-aim frame with the cannon arm taken off and the chest under it filled in) plus the
cannon arm, rotated about the shoulder at 25 angles (90 down to -90, 7.5 degrees apart). Every torso frame is the same body with only the arm turned, so the head and chest can never
change between aim angles. Rotation happens at the source resolution, then each frame is scaled down and quantised together, like all the other art. Used by tools/hero_parts.py."""
import math
import numpy as np
from PIL import Image, ImageDraw

N_ANG = 25
ANGLES = [90 - 7.5 * i for i in range(N_ANG)]                  # elevation in degrees, up positive
NAMES = ['r%d' % i for i in range(N_ANG)]
PAD_X, PAD_Y, CW, CH = 30, 36, 150, 160                           # canvas (source pixels) around the 88 x 104 aim_0 frame
PIVOT = (37.0, 34.0)                                            # where the forearm meets the shoulder plate
ARM_SCALE = 1.22                                                # the cannon reads small at game size: a little more bulk
TIP0 = (82.0, 32.5)                                             # the cyan muzzle at 0 degrees
BELT_X, CUT_Y = 34.0, 59.0                                      # hip: centre of the belt band; the body is cut just under the belt
ARM_POLY = [(35, 28), (40, 27), (56, 27), (63, 25.5), (92, 25.5), (92, 46), (50, 46), (50, 41.5), (35, 41.5)]

def _parts(raw0):
    a = np.asarray(raw0).copy(); H, W = a.shape[:2]
    rr, gg, bb = a[..., 0].astype(int), a[..., 1].astype(int), a[..., 2].astype(int)
    pink = (rr > 150) & (gg < 120) & (bb > 100) & (rr - gg > 60)
    poly = Image.new('L', (W, H), 0); ImageDraw.Draw(poly).polygon(ARM_POLY, fill=255); inpoly = np.asarray(poly) > 0
    arm_m = inpoly & (a[..., 3] > 0) & ~pink
    arm = a.copy(); arm[~arm_m, 3] = 0
    body = a.copy(); body[arm_m, 3] = 0
    body[int(CUT_Y) + 1:, :, 3] = 0                                                                # legs are drawn separately
    return a, body, arm, arm_m

def _fill_body(body, a):
    """chest under the glove: continue the shoulder plate to the right; waist: dark abdomen between chest and belt"""
    H, W = body.shape[:2]
    for y in range(27, 43):
        for x in range(34, 47):
            if body[y, x, 3] == 0 and x - 11 >= 0 and body[y, x - 11, 3] > 0 and (x - 34) < 9: body[y, x] = body[y, x - 11]
    dark = (16, 24, 60, 255)
    for y in range(44, 52):
        for x in range(25, 43):
            if body[y, x, 3] == 0: body[y, x] = dark
    return body

def build(raw, s, preview=None):
    """-> {'r0'...: (PIL RGBA torso at game scale, hx, hy, tx, ty)} for all 25 angles"""
    raw0 = raw['aim_0']; a, body, arm, arm_m = _parts(raw0); body = _fill_body(body, a)
    def canvas(arr):
        c = Image.new('RGBA', (CW, CH), (0, 0, 0, 0)); c.alpha_composite(Image.fromarray(arr, 'RGBA'), (PAD_X, PAD_Y)); return c
    body_c = canvas(body); arm_c = canvas(arm)
    px, py = PIVOT[0] + PAD_X, PIVOT[1] + PAD_Y
    k = ARM_SCALE; arm_c = arm_c.convert('RGBa').transform(arm_c.size, Image.AFFINE, (1 / k, 0, px - px / k, 0, 1 / k, py - py / k), resample=Image.BICUBIC).convert('RGBA')
    gw, gh = round(CW * s), round(CH * s); f = gw / float(CW)
    frames = []
    for e in ANGLES:
        rot = arm_c.convert('RGBa').rotate(e, resample=Image.BICUBIC, center=(px, py)).convert('RGBA')
        comp = body_c.copy(); comp.alpha_composite(rot)
        sc = comp.convert('RGBa').resize((gw, gh), Image.LANCZOS).convert('RGBA'); q = np.asarray(sc).copy(); q[..., 3] = np.where(q[..., 3] > 110, 255, 0)
        frames.append(q)
    # one palette for every frame
    stack = np.concatenate([q[..., :3] for q in frames], axis=0)
    pal = Image.fromarray(stack, 'RGB').quantize(colors=64, method=Image.MEDIANCUT, dither=Image.NONE)
    out = {}
    hipx, hipy = (BELT_X + PAD_X) * f, (CUT_Y + PAD_Y) * f
    for name, e, q in zip(NAMES, ANGLES, frames):
        rgb = np.asarray(Image.fromarray(q[..., :3], 'RGB').quantize(palette=pal, dither=Image.NONE).convert('RGB'))
        im = np.dstack([rgb, q[..., 3]]); al = im[..., 3] > 0; ys, xs = np.nonzero(al); x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
        img = Image.fromarray(im[y0:y1 + 1, x0:x1 + 1], 'RGBA')
        ca, sa = math.cos(math.radians(e)), math.sin(math.radians(e)); dx, dy = (TIP0[0] - PIVOT[0]) * ARM_SCALE, (TIP0[1] - PIVOT[1]) * ARM_SCALE
        tx = PIVOT[0] + dx * ca + dy * sa; ty = PIVOT[1] - dx * sa + dy * ca
        gx, gy = (tx + PAD_X) * f, (ty + PAD_Y) * f
        out[name] = (img, hipx - x0, hipy - 1 - y0, gx - hipx, gy - (hipy - 1))
    if preview: preview(out, body_c, arm_c)
    return out
