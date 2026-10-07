"""Segment the supplied boss sheets (flat dark-navy background) into frames: returns, per sheet, a list of cell dicts with the main body bbox and the full bbox."""
import numpy as np
from PIL import Image
from collections import deque

GRID = {  # name: (cols, rows, labels)
    'beetle': (2, 3, ['walk', 'roar', 'tele', 'charge', 'stun0', 'stun1']),
    'jelly': (1, 2, ['bell', 'bell_open']),
    'heart': (2, 2, ['closed', 'open', 'wide', 'node']),
    'moth': (3, 2, ['fly', 'down', 'shoot', 'dive', 'stun', 'dead']),
    'wyrm': (2, 2, ['head', 'head_open', 'neck', 'splash']),
}

def load(name, root):
    im = Image.open('%s/%s.png' % (root, name)).convert('RGB')
    a = np.asarray(im).astype(np.int32)
    bg = np.median(a[:6, :].reshape(-1, 3), axis=0)
    d = np.abs(a - bg).sum(axis=2)
    return im, a, d

def components(mask, minpx=1):
    h, w = mask.shape
    lab = np.zeros((h, w), np.int32); comps = []
    n = 0
    for y in range(h):
        row = mask[y]
        for x in np.nonzero(row & (lab[y] == 0))[0]:
            if lab[y, x]: continue
            n += 1; q = deque([(y, x)]); lab[y, x] = n; x0 = x1 = x; y0 = y1 = y; cnt = 0
            while q:
                cy, cx = q.popleft(); cnt += 1
                if cx < x0: x0 = cx
                if cx > x1: x1 = cx
                if cy > y1: y1 = cy
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not lab[ny, nx]:
                            lab[ny, nx] = n; q.append((ny, nx))
            comps.append((n, x0, y0, x1, y1, cnt))
    return lab, comps

def segment(name, root, thr=60):
    im, a, d = load(name, root)
    mask = d > thr
    lab, comps = components(mask)
    cols, rows, labels = GRID[name]
    H, W = mask.shape; cw, ch = W / cols, H / rows
    cells = [dict(label=l, comps=[]) for l in labels]
    for (n, x0, y0, x1, y1, cnt) in comps:
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        i = int(cy // ch) * cols + int(cx // cw)
        if i >= len(cells): continue
        cells[i]['comps'].append((n, x0, y0, x1, y1, cnt))
    out = []
    for i, c in enumerate(cells):
        cx0, cy0 = (i % cols) * cw, (i // cols) * ch
        keep = []
        for comp in c['comps']:
            n, x0, y0, x1, y1, cnt = comp
            is_text = (y1 - y0) < 45 and (x1 - x0) < 320 and y0 < cy0 + 100 and x0 < cx0 + 330 and cnt < 2500
            if not is_text and cnt >= 12: keep.append(comp)
        if not keep: continue
        main = max(keep, key=lambda t: t[5])
        bx0 = min(t[1] for t in keep); by0 = min(t[2] for t in keep); bx1 = max(t[3] for t in keep); by1 = max(t[4] for t in keep)
        mask_ids = set(t[0] for t in keep)
        out.append(dict(label=c['label'], full=(bx0, by0, bx1, by1), main=main[1:5], ids=mask_ids))
    return im, lab, out

if __name__ == '__main__':
    import sys
    root = sys.argv[1]
    for nm in GRID:
        im, lab, cells = segment(nm, root)
        print(nm, im.size)
        for c in cells: print('  ', c['label'], 'full', c['full'], 'main', c['main'])
