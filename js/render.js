/* Draws a frame: parallax, baked room tiles (autotiled, with hash-placed decor), entities, shots, effects. 480x270 internal canvas. */
(function (G) {
  'use strict';
  const S = G.sprites, RM = G.room, T = 16, U = G.U;
  const R = {};
  G.render = R;
  const solidish = (room, tx, ty) => { const k = RM.at(room, tx, ty); return k === 1 || k === 3 || k === 4 || k === 5 || k === 6 || k === 7; };
  const hash = (a, b) => ((a * 73856093) ^ (b * 19349663)) >>> 0;
  /* bake the static layers of a room into one canvas (re-run when blocks break) */
  R.bake = function (room) {
    const c = room.baked && room.baked.width === room.pw && room.baked.height === room.ph ? room.baked : document.createElement('canvas');
    c.width = room.pw; c.height = room.ph;
    const x = c.getContext('2d'); x.imageSmoothingEnabled = false; x.clearRect(0, 0, c.width, c.height);
    for (let ty = 0; ty < room.h; ty++) for (let tx = 0; tx < room.w; tx++) if (room.wall[ty * room.w + tx]) {
      const h = hash(tx, ty), v = h % 11 === 0 ? 3 : (tx + ty * 2) % 3;
      x.drawImage(S.tile.wall[v], tx * T, ty * T);
    }
    for (let ty = 0; ty < room.h; ty++) for (let tx = 0; tx < room.w; tx++) {
      const k = RM.at(room, tx, ty), h = hash(tx, ty), px = tx * T, py = ty * T;
      if (k === 1) {
        const m = (!solidish(room, tx, ty - 1) ? 1 : 0) | (!solidish(room, tx + 1, ty) && tx + 1 < room.w ? 2 : 0) | (!solidish(room, tx, ty + 1) && ty + 1 < room.h ? 4 : 0) | (!solidish(room, tx - 1, ty) && tx > 0 ? 8 : 0);
        let img;
        if (m) img = S.tile.edge[m][h % 3];
        else {
          const d = (!solidish(room, tx - 1, ty - 1) ? 1 : 0) | (!solidish(room, tx + 1, ty - 1) ? 2 : 0) | (!solidish(room, tx + 1, ty + 1) ? 4 : 0) | (!solidish(room, tx - 1, ty + 1) ? 8 : 0);
          img = d ? S.tile.diag[d] : S.tile.edge[0][h % 3];
        }
        x.drawImage(img, px, py);
        if ((m & 1) && !(m & 8) && !(m & 2)) { const r = h % 9; if (r === 0) x.drawImage(S.deco.tuft, px + 3, py - 7); else if (r === 1) x.drawImage(S.deco.fern, px, py - 11); else if (r === 2) x.drawImage(S.deco.rubble, px, py - 7); }
        if ((m & 4) && !(m & 8) && !(m & 2) && h % 7 === 0) x.drawImage(S.deco.vine[h % 3], px + 4, py + 16);
      } else if (k === 3) x.drawImage(S.tile.slopeR, px, py);
      else if (k === 4) x.drawImage(S.tile.slopeL, px, py);
      else if (k === 2) x.drawImage(S.tile.ledge, px, py);
      else if (k === 5) x.drawImage(S.tile.shot, px, py);
      else if (k === 6) x.drawImage(S.tile.bomb, px, py);
      else if (k === 7) x.drawImage(S.tile.missile, px, py);
      else if (k === 8) x.drawImage(S.tile.spikes, px, py);
    }
    room.baked = c; room.dirty = false;
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
    const bg = S.bg1, fx = -Math.floor(cam.x * 0.12) % 480, mx = -Math.floor(cam.x * 0.4) % 480;
    for (const [img, o] of [[bg.far, fx], [bg.mid, mx]]) { const a = o < 0 ? o : o - 480; ctx.drawImage(img, a, 0); ctx.drawImage(img, a + 480, 0); }
    ctx.translate(-ox, -oy);
    ctx.drawImage(room.baked, 0, 0);
    for (const d of room.decor || []) ctx.drawImage(d.img, d.x, d.y);
    G.enemies.draw(ctx, g, time);
    for (const b of g.bombs) { const fl = Math.floor(b.t / (b.t > 30 ? 3 : 6)) & 1; ctx.fillStyle = '#2e3452'; ctx.fillRect(Math.round(b.x) - 4, Math.round(b.y) - 3, 8, 7); ctx.fillRect(Math.round(b.x) - 3, Math.round(b.y) - 4, 6, 9); ctx.fillStyle = '#5a658a'; ctx.fillRect(Math.round(b.x) - 3, Math.round(b.y) - 3, 3, 2); ctx.fillStyle = fl ? '#fff2a8' : '#ef7a2a'; ctx.fillRect(Math.round(b.x), Math.round(b.y) - 6, 2, 2); }
    /* hero */
    if (!p.dead && !(p.inv > 0 && Math.floor(time * 20) % 2 && p.hurt === 0)) {
      const fr = G.player.frame(p), c = p.face >= 0 ? fr.r : fr.l;
      if (p.mode === 'ball') ctx.drawImage(c, Math.round(p.x - 8), Math.round(p.y - 15));
      else ctx.drawImage(c, Math.round(p.x - S.heroAx), Math.round(p.y - S.heroAy));
      if (p.charge > 0) { const m = G.player.muzzle(p), r = 1 + Math.floor(p.charge / 14); ctx.fillStyle = p.charge >= 50 ? '#fff' : '#ffd24a'; ctx.fillRect(Math.round(m.x) - r, Math.round(m.y) - r, r * 2, r * 2); if (Math.floor(time * 30) & 1) { ctx.fillStyle = '#fff6a0'; ctx.fillRect(Math.round(m.x) - r - 1, Math.round(m.y), 1, 1); ctx.fillRect(Math.round(m.x) + r, Math.round(m.y), 1, 1); } }
    }
    for (const s of g.shots) R.shot(ctx, s, time);
    G.fx.draw(ctx);
    ctx.restore();
  };
  R.shot = function (ctx, s, time) {
    const x = Math.round(s.x), y = Math.round(s.y);
    if (s.kind === 'beam') {
      const a = Math.abs(s.vx) >= Math.abs(s.vy) * 1.5 ? 'h' : Math.abs(s.vy) >= Math.abs(s.vx) * 1.5 ? 'v' : 'd';
      if (s.big) { ctx.fillStyle = s.col[0]; ctx.fillRect(x - 5, y - 3, 10, 6); ctx.fillRect(x - 3, y - 5, 6, 10); ctx.fillStyle = s.col[1]; ctx.fillRect(x - 3, y - 2, 6, 4); ctx.fillRect(x - 2, y - 3, 4, 6); return; }
      ctx.fillStyle = s.col[0];
      if (a === 'h') { ctx.fillRect(x - 4, y - 1, 8, 3); ctx.fillStyle = s.col[1]; ctx.fillRect(x - 3, y, 6, 1); }
      else if (a === 'v') { ctx.fillRect(x - 1, y - 4, 3, 8); ctx.fillStyle = s.col[1]; ctx.fillRect(x, y - 3, 1, 6); }
      else { ctx.fillRect(x - 2, y - 2, 4, 4); ctx.fillStyle = s.col[1]; ctx.fillRect(x - 1, y - 1, 2, 2); }
    } else {
      const sup = s.kind === 'super', dx = s.dx, dy = s.dy;
      ctx.fillStyle = sup ? '#6cf08a' : '#e8ecf8';
      const len = 5; for (let i = 0; i < len; i++) ctx.fillRect(Math.round(s.x - dx * i * 1.2) - 1, Math.round(s.y - dy * i * 1.2) - 1, 3, 3);
      ctx.fillStyle = sup ? '#2a8a4a' : '#ec5c4a'; ctx.fillRect(Math.round(s.x + dx * 3) - 1, Math.round(s.y + dy * 3) - 1, 3, 3);
      ctx.fillStyle = '#ffd24a'; ctx.fillRect(Math.round(s.x - dx * 6) - 1, Math.round(s.y - dy * 6) - 1, 2, 2);
    }
  };
})((window.SGS = window.SGS || {}));
