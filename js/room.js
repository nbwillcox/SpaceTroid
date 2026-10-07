/* A room: ASCII tile map -> typed tile array plus queries. Tile types: 0 air, 1 solid, 2 one-way ledge, 3 slope rising right, 4 slope rising left, 5 shot block, 6 bomb block, 7 missile block, 8 spikes. */
(function (G) {
  'use strict';
  const T = 16;
  const CH = { '.': 0, '#': 1, '=': 2, '/': 3, '\\': 4, 'b': 5, 'B': 6, 'M': 7, '^': 8, 'i': 10, 'L': 11, 'x': 12, 'D': 13, 'W': 14, 'G': 15, 'S': 16 };
  const R = { T: { AIR: 0, SOLID: 1, LEDGE: 2, SLR: 3, SLL: 4, SHOT: 5, BOMB: 6, MISSILE: 7, SPIKE: 8 } };
  G.room = R;
  R.build = function (def) {
    const rows = def.map, h = rows.length, w = rows.reduce((m, r) => Math.max(m, r.length), 0);
    const room = { id: def.id, def, w, h, pw: w * T, ph: h * T, t: new Uint8Array(w * h), wall: new Uint8Array(w * h), spawns: [], doors: def.doors || [], items: def.items || [], zone: def.zone || 1, name: def.name || '' };
    for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
      const c = rows[y][x] || '.';
      if (c in CH) room.t[y * w + x] = CH[c];
      else if (c === 'w') room.wall[y * w + x] = 1;
      else if (c !== ' ') room.spawns.push({ ch: c, x: x * T + 8, y: y * T + T, tx: x, ty: y });
    }
    room.water = []; for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) if (room.t[y * w + x] === 14) room.water.push({ tx: x, ty: y, top: y === 0 || room.t[(y - 1) * w + x] !== 14 });
    room.anchors = []; for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) if (room.t[y * w + x] === 15) room.anchors.push({ x: x * T + 8, y: y * T + 8, tx: x, ty: y });
    room.lava = []; for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) if (room.t[y * w + x] === 11) room.lava.push({ tx: x, ty: y, top: y === 0 || room.t[(y - 1) * w + x] !== 11 });
    /* cells that sit inside a back-wall region (hidden scan blocks, anchors, water, lava, spawn markers) get the same wall tile behind them, so nothing shows through as a gap */
    const cand = new Uint8Array(w * h);
    for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) { const c = rows[y][x] || '.'; if (c === 'S' || c === 'G' || c === 'W' || c === 'L' || (!(c in CH) && c !== 'w' && c !== ' ')) cand[y * w + x] = 1; }
    for (let pass = 0; pass < 2; pass++) for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
      const i = y * w + x; if (!cand[i] || room.wall[i]) continue;
      let n = 0; for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) { if (!dx && !dy) continue; const xx = x + dx, yy = y + dy; if (xx >= 0 && yy >= 0 && xx < w && yy < h && room.wall[yy * w + xx]) n++; }
      if (n >= 5) room.wall[i] = 1;
    }
    /* back wall: any marked 'w' cell, or every air cell when def.wallAll is set */
    if (def.wallAll) for (let i = 0; i < w * h; i++) if (!room.t[i]) room.wall[i] = 1;
    return room;
  };
  /* tile type at tile coords; outside left/right/bottom counts as solid, above the top as air */
  R.at = (room, tx, ty) => (ty < 0 ? 0 : tx < 0 || tx >= room.w || ty >= room.h ? 1 : room.t[ty * room.w + tx]);
  R.isSolid = (k) => k === 1 || k === 5 || k === 6 || k === 7 || k === 9 || k === 10 || k === 12 || k === 13;
  R.solidAt = (room, tx, ty) => { const k = R.at(room, tx, ty); return k === 16 ? !!room.scanOn : R.isSolid(k); };
  R.set = (room, tx, ty, k) => { if (tx >= 0 && ty >= 0 && tx < room.w && ty < room.h) { room.t[ty * room.w + tx] = k; room.dirty = true; } };
  /* y of the walkable surface of a tile at local pixel column lx (0..15), or null */
  R.surface = (k, ty, lx) => (k === 1 || k === 5 || k === 6 || k === 7 || k === 9 || k === 10 || k === 12 || k === 13 || k === 2 ? ty * T : k === 3 ? ty * T + 16 - lx : k === 4 ? ty * T + 1 + lx : null);
})((window.SGS = window.SGS || {}));
