/* Draws a frame: parallax, baked room tiles (autotiled, with hash-placed decor), entities, shots, effects. 480x270 internal canvas. */
(function (G) {
  'use strict';
  const S = G.sprites, RM = G.room, T = 16, U = G.U;
  const R = {};
  G.render = R;
  const solidish = (room, tx, ty) => { const k = RM.at(room, tx, ty); return k === 1 || k === 3 || k === 4 || k === 5 || k === 6 || k === 7 || k === 9 || k === 10 || k === 12 || k === 13; };
  const hash = (a, b) => ((a * 73856093) ^ (b * 19349663)) >>> 0;
  /* bake the static layers of a room into one canvas (re-run when blocks break) */
  R.bake = function (room) {
    const TS = S.tilesets[room.zone || 1], tile = TS, deco = TS.deco;
    const c = room.baked && room.baked.width === room.pw && room.baked.height === room.ph ? room.baked : document.createElement('canvas');
    c.width = room.pw; c.height = room.ph;
    const x = c.getContext('2d'); x.imageSmoothingEnabled = false; x.clearRect(0, 0, c.width, c.height);
    if (!room.wallLayer) {                                                  /* the back wall (tiles plus this room's own dressing) is built once per room entry */
      const wl = document.createElement('canvas'); wl.width = room.pw; wl.height = room.ph;
      const wx = wl.getContext('2d'); wx.imageSmoothingEnabled = false;
      for (let ty = 0; ty < room.h; ty++) for (let tx = 0; tx < room.w; tx++) if (room.wall[ty * room.w + tx]) {
        const h = hash(tx, ty), v = h % 11 === 0 ? 3 : (tx + ty * 2) % 3;
        wx.drawImage(tile.wall[v], tx * T, ty * T);
      }
      if (G.walldeco) G.walldeco.apply(wx, room, TS);
      room.wallLayer = wl;
    }
    x.drawImage(room.wallLayer, 0, 0);
    for (let ty = 0; ty < room.h; ty++) for (let tx = 0; tx < room.w; tx++) {
      const k = RM.at(room, tx, ty), h = hash(tx, ty), px = tx * T, py = ty * T;
      if (k === 1) {
        const m = (!solidish(room, tx, ty - 1) ? 1 : 0) | (!solidish(room, tx + 1, ty) && tx + 1 < room.w ? 2 : 0) | (!solidish(room, tx, ty + 1) && ty + 1 < room.h ? 4 : 0) | (!solidish(room, tx - 1, ty) && tx > 0 ? 8 : 0);
        let img;
        if (m) img = tile.edge[m][h % 3];
        else {
          const d = (!solidish(room, tx - 1, ty - 1) ? 1 : 0) | (!solidish(room, tx + 1, ty - 1) ? 2 : 0) | (!solidish(room, tx + 1, ty + 1) ? 4 : 0) | (!solidish(room, tx - 1, ty + 1) ? 8 : 0);
          img = d ? tile.diag[d] : tile.edge[0][h % 3];
        }
        x.drawImage(img, px, py);
        if ((m & 1) && !(m & 8) && !(m & 2)) { const r = h % 9; if (r < tile.top.length) { const [im, ox, oy] = tile.top[r]; x.drawImage(im, px + ox, py - oy); } }
        if ((m & 4) && !(m & 8) && !(m & 2) && h % 7 === 0) { const [im, ox] = tile.hang[h % tile.hang.length]; x.drawImage(im, px + ox, py + 16); }
      } else if (k === 3) x.drawImage(tile.slopeR, px, py);
      else if (k === 4) x.drawImage(tile.slopeL, px, py);
      else if (k === 2) { x.drawImage(tile.wall[(tx + ty * 2) % 3], px, py); x.drawImage(tile.ledge, px, py); }
      else if (k === 5) x.drawImage(tile.shot, px, py);
      else if (k === 6) x.drawImage(tile.bomb, px, py);
      else if (k === 7) x.drawImage(tile.missile, px, py);
      else if (k === 8) x.drawImage(tile.spikes, px, py);
      else if (k === 10) x.drawImage(tile.ice, px, py);
      else if (k === 12) x.drawImage(tile.wave, px, py);
      else if (k === 13) x.drawImage(tile.dashblock, px, py);
    }
    room.baked = c; room.dirty = false;
  };
  /* the light that rises from a save pad: stepped bands that grow upward, rising sparkles and a bright base; front = the thin inner beam drawn over the hero */
  R.saveLight = function (ctx, a, front) {
    const t = a.t, grow = Math.min(1, t / 30), h = Math.round(84 * (1 - (1 - grow) * (1 - grow))), fade = t > 58 ? Math.max(0, 1 - (t - 58) / 26) : 1;
    if (fade <= 0) return;
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    for (let y = 0; y < h; y += 2) {
      if ((y >> 2) % 3 === 2 && !front) continue;
      const k = 1 - y / 100, w = Math.round((front ? 10 : 26) * (0.6 + 0.4 * k)) & ~1, al = fade * (front ? 0.34 : 0.5) * k;
      ctx.fillStyle = 'rgba(150,244,255,' + al.toFixed(3) + ')'; ctx.fillRect(Math.round(a.x - w / 2), a.y - 2 - y, w, 2);
    }
    if (!front) {
      ctx.fillStyle = 'rgba(210,252,255,' + (0.55 * fade).toFixed(3) + ')'; ctx.fillRect(Math.round(a.x - 15), a.y - 3, 30, 2); ctx.fillRect(Math.round(a.x - 9), a.y - 5, 18, 2);
      for (let i = 0; i < 16; i++) {
        const ph = (t * 1.5 + i * 11) % 84; if (ph > h) continue;
        const x = Math.round(a.x + (((i * 37) % 19) - 9) * (1 - ph / 110)), y = Math.round(a.y - 4 - ph), sz = i % 3 === 0 ? 2 : 1;
        ctx.fillStyle = 'rgba(240,255,255,' + (fade * (0.9 - ph / 120)).toFixed(3) + ')'; ctx.fillRect(x, y, sz, sz);
      }
    }
    ctx.restore();
  };
  R.camera = function (g, snap) {
    const p = g.P, room = g.room, cam = g.cam, W = 480, H = 270;
    const tx = p.x + p.face * 22 - W / 2, ty = p.y - 36 - H / 2 - 24;
    if (snap) { cam.x = tx; cam.y = ty; } else { cam.x += (tx - cam.x) * 0.1; cam.y += (ty - cam.y) * 0.12; }
    cam.x = room.pw <= W ? (room.pw - W) / 2 : U.clamp(cam.x, 0, room.pw - W);
    cam.y = room.ph <= H ? (room.ph - H) / 2 : U.clamp(cam.y, 0, room.ph - H);
  };
  R.draw = function (ctx, g, time) {
    const room = g.room, cam = g.cam, p = g.P;
    if (!room.baked || room.dirty) R.bake(room);
    ctx.save();
    const sh = G.settings.shake && !G.settings.reduced ? g.shake : 0;
    let ox = Math.round(cam.x), oy = Math.round(cam.y);
    if (sh > 0.3) { ox += Math.round((Math.random() - 0.5) * sh); oy += Math.round((Math.random() - 0.5) * sh); }
    /* parallax (horizontal only) */
    const bg = S.bgs[room.zone || 1], fx = -Math.floor(cam.x * 0.12) % 480, mx = -Math.floor(cam.x * 0.4) % 480;
    ctx.fillStyle = '#05071a'; ctx.fillRect(0, 0, 480, 270);
    const rx0 = Math.max(0, -ox), rx1 = Math.min(480, room.pw - ox), ry0 = Math.max(0, -oy), ry1 = Math.min(270, room.ph - oy);
    ctx.save(); ctx.beginPath(); ctx.rect(rx0, ry0, rx1 - rx0, ry1 - ry0); ctx.clip();
    for (const [img, o] of [[bg.far, fx], [bg.mid, mx]]) { const a = o < 0 ? o : o - 480; ctx.drawImage(img, a, 0); ctx.drawImage(img, a + 480, 0); }
    ctx.restore();
    ctx.translate(-ox, -oy);
    ctx.drawImage(room.baked, 0, 0);
    for (const d of room.decor || []) ctx.drawImage(d.img, d.x, d.y);
    if (G.atmos) G.atmos.draw(ctx, g, 0, time);
    G.world.drawBack(ctx, g, time);
    G.enemies.draw(ctx, g, time);
    G.bosses.draw(ctx, g, time);
    const TS3 = S.tilesets[room.zone || 1], lf = Math.floor(time * 6) & 3;
    const lavaPass = () => { for (const l of room.lava) { const lx = l.tx * T, ly = l.ty * T; if (lx + 16 < ox || lx > ox + 480 || ly + 16 < oy || ly > oy + 270) continue; ctx.drawImage((l.top ? TS3.lavaTop : TS3.lava)[(lf + l.tx) & 3], lx, ly); } };
    if (room.lava.length) { lavaPass(); if (G.atmos) G.atmos.lavaGlow(ctx, room, ox, oy); }
    const waterPass = (a) => { ctx.globalAlpha = a; for (const w of room.water) { const wx = w.tx * T, wy = w.ty * T; if (wx + 16 < ox || wx > ox + 480 || wy + 16 < oy || wy > oy + 270) continue; ctx.fillStyle = '#2a78c8'; ctx.fillRect(wx, wy, 16, 16); if (w.top) { ctx.fillStyle = '#c8f0ff'; ctx.fillRect(wx, wy + (Math.floor(time * 3 + w.tx) & 1), 16, 1); } else if ((w.tx * 7 + w.ty * 13 + Math.floor(time * 2)) % 9 === 0) { ctx.fillStyle = '#a8e8ff'; ctx.fillRect(wx + 5, wy + 6, 2, 2); } } ctx.globalAlpha = 1; };
    if (room.water.length) waterPass(0.26);
    if (room.scanTiles === undefined) { room.scanTiles = []; for (let y = 0; y < room.h; y++) for (let x = 0; x < room.w; x++) if (room.t[y * room.w + x] === 16) room.scanTiles.push([x, y]); }
    for (const [sx, sy] of room.scanTiles) {                          /* hidden scan blocks: solid and visible only while scanning; a faint shimmer hints at them */
      const px = sx * T, py = sy * T;
      if (g.abil.scan && room.scanOn) { ctx.fillStyle = '#10305a'; ctx.fillRect(px, py, 16, 16); ctx.fillStyle = '#38c0b0'; ctx.fillRect(px, py, 16, 1); ctx.fillRect(px, py + 15, 16, 1); ctx.fillRect(px, py, 1, 16); ctx.fillRect(px + 15, py, 1, 16); ctx.fillStyle = '#86f0f2'; ctx.fillRect(px + 3, py + 3, 10, 1); ctx.fillRect(px + 3, py + 3, 1, 10); ctx.fillStyle = '#244850'; ctx.fillRect(px + 5, py + 6, 6, 5); }
      else if (g.abil.scan && (sx * 5 + sy * 3 + Math.floor(time * 2)) % 11 === 0) { ctx.fillStyle = 'rgba(134,240,242,0.45)'; ctx.fillRect(px + 2 + (sx % 3) * 4, py + 1 + (sy % 3) * 4, 1, 1); }
    }
    G.movers.draw(ctx, g); G.world.drawFront(ctx, g, time);
    for (const b of g.bombs) {
      const fl = Math.floor(b.t / (b.t > 30 ? 3 : 6)) & 1, r = b.big ? 7 : 4, bx = Math.round(b.x), by = Math.round(b.y);
      ctx.fillStyle = b.big ? '#6b3d14' : '#2e3452'; ctx.fillRect(bx - r, by - r + 1, r * 2, r * 2 - 2); ctx.fillRect(bx - r + 1, by - r, r * 2 - 2, r * 2);
      ctx.fillStyle = b.big ? '#efba42' : '#5a658a'; ctx.fillRect(bx - r + 1, by - r + 1, r - 1, 2);
      ctx.fillStyle = fl ? '#fff2a8' : '#ef7a2a'; ctx.fillRect(bx, by - r - 2, 2, 2);
    }
    if (g.saveAnim) R.saveLight(ctx, g.saveAnim, false);
    /* hero */
    const dying = p.dead > 0 && p.dead < 16;                                 /* a short white-flash collapse before the explosion */
    if (dying || (!p.dead && !(p.inv > 0 && Math.floor(time * 20) % 2 && p.hurt === 0))) {
      const fr = G.player.frame(p), c0 = p.face >= 0 ? fr.r : fr.l, c = dying && (p.dead & 2) ? S.whiteOf(c0) : c0;
      if (p.mode === 'ball') ctx.drawImage(c, Math.round(p.x - 8), Math.round(p.y - 16));
      else if (p.spinning && !p.ground) ctx.drawImage(c, Math.round(p.x - 24), Math.round(p.y - 22 - 24));
      else ctx.drawImage(c, Math.round(p.x - S.heroAx), Math.round(p.y - (fr.ay || S.heroAy)));
      if (g.saveAnim && g.saveAnim.t > 30 && g.saveAnim.t < 56) { ctx.globalAlpha = 0.75 * (1 - Math.abs(g.saveAnim.t - 42) / 12); ctx.drawImage(S.whiteOf(c0), Math.round(p.x - S.heroAx), Math.round(p.y - (fr.ay || S.heroAy))); ctx.globalAlpha = 1; }
      if (p.charge > 0) { const m = G.player.muzzle(p), r = 1 + Math.floor(p.charge / 14); ctx.fillStyle = p.charge >= 50 ? '#fff' : '#ffd24a'; ctx.fillRect(Math.round(m.x) - r, Math.round(m.y) - r, r * 2, r * 2); if (Math.floor(time * 30) & 1) { ctx.fillStyle = '#fff6a0'; ctx.fillRect(Math.round(m.x) - r - 1, Math.round(m.y), 1, 1); ctx.fillRect(Math.round(m.x) + r, Math.round(m.y), 1, 1); } }
    }
    if (g.saveAnim) R.saveLight(ctx, g.saveAnim, true);
    if (room.lava.length) { ctx.globalAlpha = 0.5; lavaPass(); ctx.globalAlpha = 1; }
    if (room.water.length) waterPass(0.2);
    G.grapple.draw(ctx, g, time);
    for (const s of g.shots) R.shot(ctx, s, time);
    G.fx.draw(ctx);
    if (G.atmos) G.atmos.draw(ctx, g, 1, time);
    ctx.restore();
    if (G.atmos) G.atmos.vignette(ctx);
  };
  R.shot = function (ctx, s, time) {
    const x = Math.round(s.x), y = Math.round(s.y);
    if (s.kind === 'beam') {
      if (s.big) { ctx.fillStyle = s.col[0]; ctx.fillRect(x - 5, y - 3, 10, 6); ctx.fillRect(x - 3, y - 5, 6, 10); ctx.fillStyle = s.col[1]; ctx.fillRect(x - 3, y - 2, 6, 4); ctx.fillRect(x - 2, y - 3, 4, 6); return; }
      const sp = Math.hypot(s.vx, s.vy) || 1, ux = s.vx / sp, uy = s.vy / sp;      /* a short streak along the true direction of travel */
      for (let i = 5; i >= 0; i--) { const px = Math.round(s.x - ux * i * 1.8), py = Math.round(s.y - uy * i * 1.8); ctx.fillStyle = i === 0 ? s.col[1] : i < 3 ? s.col[0] : s.col[0]; ctx.globalAlpha = i > 3 ? 0.55 : 1; ctx.fillRect(px - 1, py - 1, i === 0 ? 3 : 2, i === 0 ? 3 : 2); } ctx.globalAlpha = 1;
    } else {
      const sup = s.kind === 'super', dx = s.dx, dy = s.dy;
      ctx.fillStyle = sup ? '#6cf08a' : '#e8ecf8';
      const len = 5; for (let i = 0; i < len; i++) ctx.fillRect(Math.round(s.x - dx * i * 1.2) - 1, Math.round(s.y - dy * i * 1.2) - 1, 3, 3);
      ctx.fillStyle = sup ? '#2a8a4a' : '#ec5c4a'; ctx.fillRect(Math.round(s.x + dx * 3) - 1, Math.round(s.y + dy * 3) - 1, 3, 3);
      ctx.fillStyle = '#ffd24a'; ctx.fillRect(Math.round(s.x - dx * 6) - 1, Math.round(s.y - dy * 6) - 1, 2, 2);
    }
  };
})((window.SGS = window.SGS || {}));
