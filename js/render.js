/* Draws a frame: parallax, baked room tiles (autotiled, with hash-placed decor), entities, shots, effects. 480x270 internal canvas. */
(function (G) {
  'use strict';
  const S = G.sprites, RM = G.room, T = 16, U = G.U, W = G.world;
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
      for (let ty = 0; ty < room.h; ty++) for (let tx = 0; tx < room.w; tx++) if (room.wall[ty * room.w + tx] || room.t[ty * room.w + tx] !== 1) {      /* layering: black space, then the room's back wall in EVERY non-rock cell (no gaps), then everything else on top */
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
      else if (k === 2) { x.drawImage(tile.edge[1][h % 3], 0, 6, 16, 6, px, py + 5, 16, 6); x.drawImage(tile.ledge, px, py); }      /* one-way ledge: a thin slab of the zone's own brick under the pale cap */
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
  /* the item-get moment: light rays from the raised cannon, the item floating up with a glow, and a quick white flash */
  R.getFx = function (ctx, g, time) {
    const a = g.getAnim, p = g.P, m = G.player.muzzle(p), t = a.t, big = a.big, fade = t > (big ? 140 : 62) ? Math.max(0, 1 - (t - (big ? 140 : 62)) / 24) : 1;
    const rise = Math.min(big ? 26 : 18, t * 0.5), cx = Math.round(m.x), cy = Math.round(m.y - 6 - rise);
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    const rays = big ? 12 : 8;
    for (let i = 0; i < rays; i++) {
      const ang = (i / rays) * 6.283 + t * 0.015, len = Math.min(big ? 46 : 26, t * 1.2) * (0.6 + 0.4 * Math.sin(t * 0.2 + i));
      for (let d = 6; d < len; d += 2) { const al = fade * (0.5 - d / (big ? 110 : 70)); if (al <= 0) break; ctx.fillStyle = 'rgba(255,240,170,' + al.toFixed(3) + ')'; ctx.fillRect(Math.round(cx + Math.cos(ang) * d), Math.round(cy + Math.sin(ang) * d), 2, 2); }
    }
    ctx.restore();
    ctx.globalAlpha = fade; W.drawItem(ctx, a.it.type, cx, cy + 14, t, Math.round(Math.sin(t * 0.12) * 2)); ctx.globalAlpha = 1;
  };
  /* a soft shaft of light falling on a shrine statue: stepped additive bands, with a few motes drifting up through it */
  R.shaft = function (ctx, d, room, time) {
    const big = d.statue === 'big', top = 32, bot = d.fy, h = bot - top, w0 = big ? 22 : 14, w1 = big ? 78 : 44;
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    for (let y = top; y < bot; y += 2) {
      const k = (y - top) / h, w = Math.round(w0 + (w1 - w0) * k), al = (0.085 - k * 0.05) * (0.8 + 0.2 * Math.sin(time * 1.3 + y * 0.05));
      if (al <= 0) continue; ctx.fillStyle = 'rgba(255,238,190,' + al.toFixed(3) + ')'; ctx.fillRect(Math.round(d.cx - w / 2), y, w, 2);
    }
    for (let i = 0; i < 7; i++) {
      const ph = (time * 14 + i * 37) % h, x = Math.round(d.cx + Math.sin(i * 2.7 + time * 0.6) * (w0 + (w1 - w0) * (ph / h)) * 0.4), y = Math.round(bot - ph);
      ctx.fillStyle = 'rgba(255,248,210,' + (0.55 * (1 - ph / h)).toFixed(3) + ')'; ctx.fillRect(x, y, 1, 1);
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
    ctx.fillStyle = '#000'; ctx.fillRect(0, 0, 480, 270);                     /* the black universe behind everything */
    ctx.translate(-ox, -oy);
    ctx.drawImage(room.baked, 0, 0);
    for (const d of room.decor || []) { if (d.statue) R.shaft(ctx, d, room, time); ctx.drawImage(d.img, d.x, d.y); }
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
      const fr = G.player.frame(p), ball = p.mode === 'ball' && !g.getAnim, right = p.face >= 0 || ball, c0 = right ? fr.r : fr.l, c = dying && (p.dead & 2) ? S.whiteOf(c0) : c0;
      const spin = p.spinning && !p.ground && !g.getAnim, hx = Math.round(p.x - (right ? fr.ax : fr.axl)), hy = Math.round(p.y - (spin ? 22 : 0) - fr.ay + (ball || spin || g.getAnim || g.saveAnim ? 0 : G.player.pose(p).dy));
      ctx.drawImage(c, hx, hy);
      if (g.saveAnim && g.saveAnim.t > 30 && g.saveAnim.t < 56) { ctx.globalAlpha = 0.75 * (1 - Math.abs(g.saveAnim.t - 42) / 12); ctx.drawImage(S.whiteOf(c0), hx, hy); ctx.globalAlpha = 1; }
      R.chargeFx(ctx, g, p, time);
    }
    if (g.saveAnim) R.saveLight(ctx, g.saveAnim, true);
    if (g.getAnim) R.getFx(ctx, g, time);
    if (room.lava.length) { ctx.globalAlpha = 0.5; lavaPass(); ctx.globalAlpha = 1; }
    if (room.water.length) waterPass(0.2);
    G.grapple.draw(ctx, g, time);
    for (const s of g.shots) R.shot(ctx, s, time);
    G.fx.draw(ctx);
    if (G.atmos) G.atmos.draw(ctx, g, 1, time);
    ctx.restore();
    if (g.getAnim && g.getAnim.t < 12) { ctx.globalAlpha = (g.getAnim.big ? 0.55 : 0.3) * (1 - g.getAnim.t / 12); ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, 480, 270); ctx.globalAlpha = 1; }
    if (G.atmos) G.atmos.vignette(ctx);
  };
  /* ---- beam art. Every beam type has its own look at every stage (build-up orb, normal / partial / full / overcharge shot):
     base = gold pulse (round, star flare, pulse rings) | ice = cyan crystal (diamond core, snowflake spikes, frost) | wave = violet ripple (rings, sine ribbons, crescents) | plasma = fire (flame tongues, embers, smoke).
     When several beams are switched on the highest one (plasma > wave > ice > base) sets the shape and each lower beam adds a small accent in its colour. ---- */
  const STY = {
    base: { c0: '#ffd24a', c1: '#fff6a0', dk: '#a8741a', hot: ['#ffffff', '#ffe9a0', '#ffd24a', '#fff6a0'] },
    ice: { c0: '#7ad8ff', c1: '#ffffff', dk: '#2a78c8', hot: ['#ffffff', '#d8f6ff', '#7ad8ff', '#b8ecff'] },
    wave: { c0: '#b878ff', c1: '#f2e0ff', dk: '#6a38b8', hot: ['#ffffff', '#f2e0ff', '#ff7ad8', '#7ae0ff'] },
    plasma: { c0: '#ff7a2a', c1: '#fff6a0', dk: '#a02808', hot: ['#ffffff', '#fff6a0', '#ffb040', '#ff5a20'] },
  };
  const disc = (ctx, x, y, r) => { for (let dy = -r; dy <= r; dy++) { const w = Math.floor(Math.sqrt(r * r + r - dy * dy + 0.25)); ctx.fillRect(x - w, y + dy, 2 * w + 1, 1); } };
  const ringPx = (ctx, x, y, r) => { const n = Math.max(12, r * 6); for (let i = 0; i < n; i++) { const a = i / n * 6.2832; ctx.fillRect(Math.round(x + Math.cos(a) * r), Math.round(y + Math.sin(a) * r), 1, 1); } };
  const arcPx = (ctx, x, y, r, a0, a1) => { const n = Math.max(8, Math.round(r * Math.abs(a1 - a0) * 1.4)); for (let i = 0; i <= n; i++) { const a = a0 + (a1 - a0) * i / n; ctx.fillRect(Math.round(x + Math.cos(a) * r), Math.round(y + Math.sin(a) * r), 1, 1); } };
  const flare = (ctx, x, y, L, diag) => {
    ctx.fillRect(x - L, y, 2 * L + 1, 1); ctx.fillRect(x, y - L, 1, 2 * L + 1);
    if (diag) for (let i = 1; i <= diag; i++) { ctx.fillRect(x + i, y + i, 1, 1); ctx.fillRect(x - i, y + i, 1, 1); ctx.fillRect(x + i, y - i, 1, 1); ctx.fillRect(x - i, y - i, 1, 1); }
  };
  const rhombus = (ctx, cx, cy, ux, uy, L, Wd) => {                               /* a diamond with its long axis along (ux, uy) */
    const R = Math.ceil(Math.max(L, Wd)) + 1, x0 = Math.round(cx), y0 = Math.round(cy);
    for (let dy = -R; dy <= R; dy++) for (let dx = -R; dx <= R; dx++) { const a = dx * ux + dy * uy, b = -dx * uy + dy * ux; if (Math.abs(a) / L + Math.abs(b) / Wd <= 1) ctx.fillRect(x0 + dx, y0 + dy, 1, 1); }
  };
  const spike = (ctx, x, y, a, l0, l1) => { const c = Math.cos(a), s = Math.sin(a); for (let i = l0; i <= l1; i++) ctx.fillRect(Math.round(x + c * i), Math.round(y + s * i), 1, 1); };
  const snow = (ctx, x, y, a0, l, barbs) => { for (let k = 0; k < 6; k++) { const a = a0 + k * 1.0472; spike(ctx, x, y, a, 1, l); if (barbs) for (const sgn of [-1, 1]) { const bx = x + Math.cos(a) * l * 0.62, by = y + Math.sin(a) * l * 0.62; spike(ctx, bx, by, a + sgn * 0.8, 1, Math.max(1, Math.round(l * 0.3))); } } };
  const ribbon = (ctx, x, y, ux, uy, len, amp, k, ph, th) => { for (let i = 1; i <= len; i++) { const off = amp * Math.sin(i * k + ph) * (1 - i / len * 0.35); ctx.globalAlpha = Math.max(0, 0.9 * (1 - i / len)); ctx.fillRect(Math.round(x - ux * i - uy * off), Math.round(y - uy * i + ux * off), th, th); } ctx.globalAlpha = 1; };
  const tongues = (ctx, x, y, r, n, t, long, st) => {                             /* flickering flame tongues around a point */
    for (let k = 0; k < n; k++) {
      const a = k / n * 6.2832 + t * 0.09 + Math.sin(k * 2.3) * 0.4, fl = 0.55 + 0.45 * Math.sin(t * 0.8 + k * 1.9), L = Math.round((r + long) * fl);
      for (let j = 0; j <= L; j++) { const q = j / Math.max(1, L); ctx.fillStyle = q < 0.4 ? st.c1 : q < 0.75 ? st.c0 : st.dk; ctx.fillRect(Math.round(x + Math.cos(a) * (r * 0.5 + j)), Math.round(y + Math.sin(a) * (r * 0.5 + j)), q < 0.5 ? 2 : 1, q < 0.5 ? 2 : 1); }
    }
  };
  const styleOf = (A) => { const b = A.beams || {}; return b.plasma ? 'plasma' : b.wave ? 'wave' : b.ice ? 'ice' : 'base'; };
  const modsOf = (A, style) => { const b = A.beams || {}, m = []; if (b.ice && style !== 'ice') m.push('ice'); if (b.wave && style !== 'wave') m.push('wave'); return m; };
  /* the small accents a lower beam adds to the shape of the beam on top */
  const accents = (ctx, x, y, r, mods, t, tier) => {
    for (const m of mods) {
      if (m === 'ice') { ctx.fillStyle = '#d8f6ff'; for (let i = 0; i < 3; i++) { const a = -t * 0.12 + i * 2.094; rhombus(ctx, x + Math.cos(a) * (r + 4), y + Math.sin(a) * (r + 4), 1, 0, 2 + tier * 0.5, 1.5); } }
      else if (m === 'wave') { ctx.fillStyle = '#d8b0ff'; ringPx(ctx, x, y, r + 3 + ((t >> 1) % 4)); }
    }
  };
  /* the build-up orb at the muzzle, one per beam type; tier 0 = just started, 1 = partial, 2 = full, 3 = overcharge */
  const ORB = {
    base(ctx, mx, my, tier, f, r, t, st) {
      ctx.fillStyle = tier === 3 ? st.hot[(t >> 1) & 3] : st.c0; disc(ctx, mx, my, r);
      if (r >= 3) { ctx.fillStyle = tier === 3 ? '#ffffff' : st.c1; disc(ctx, mx, my, Math.max(1, r - 2)); }
      if (tier >= 2) {
        ctx.fillStyle = '#ffffff'; disc(ctx, mx, my, tier === 3 ? 3 : 2);
        ctx.fillStyle = st.c1; ctx.globalAlpha = 0.85; flare(ctx, mx, my, r + 3 + ((t >> 1) & 1) * 2, tier === 3 ? r + 2 : 0);
        ctx.globalAlpha = 0.45; ringPx(ctx, mx, my, r + 2 + ((t >> 1) % 7)); ctx.globalAlpha = 1;                        /* pulse rings */
        const k = tier === 3 ? 7 : 3; for (let i = 0; i < k; i++) { const a = t * (tier === 3 ? 0.3 : 0.2) + i * 6.2832 / k; ctx.fillStyle = tier === 3 && (i & 1) ? '#ffffff' : st.c1; ctx.fillRect(Math.round(mx + Math.cos(a) * (r + 5)) - 1, Math.round(my + Math.sin(a) * (r + 5)) - 1, tier === 3 ? 3 : 2, tier === 3 ? 3 : 2); }
      }
    },
    ice(ctx, mx, my, tier, f, r, t, st) {                                                                             /* a crystal: two crossed diamonds inside a snowflake */
      const a = tier >= 2 ? t * 0.035 : 0.4, ux = Math.cos(a), uy = Math.sin(a), L = r + 2, Wd = Math.max(1.2, r * 0.62);
      ctx.fillStyle = tier === 3 ? st.hot[(t >> 2) & 3] : st.c0; rhombus(ctx, mx, my, ux, uy, L, Wd); rhombus(ctx, mx, my, -uy, ux, L, Wd);
      ctx.fillStyle = st.c1; rhombus(ctx, mx, my, ux, uy, L * 0.6, Wd * 0.6); if (tier >= 2) { ctx.fillStyle = '#ffffff'; disc(ctx, mx, my, tier === 3 ? 3 : 2); }
      if (tier >= 1) { ctx.fillStyle = st.c1; ctx.globalAlpha = 0.9; snow(ctx, mx, my, -a * 1.6, r + 3 + tier * 2, tier === 3); ctx.globalAlpha = 1; }
      if (tier >= 2) { const k = tier === 3 ? 6 : 3; for (let i = 0; i < k; i++) { const b = -t * 0.12 + i * 6.2832 / k; ctx.fillStyle = i & 1 ? '#ffffff' : st.c0; rhombus(ctx, mx + Math.cos(b) * (r + 7), my + Math.sin(b) * (r + 7), Math.cos(b + 1.57), Math.sin(b + 1.57), 3, 1.6); } }
    },
    wave(ctx, mx, my, tier, f, r, t, st) {                                                                            /* a core that keeps sending out ripples */
      const span = 12 + tier * 5, nR = 1 + tier;
      for (let i = 0; i < nR; i++) { const q = ((t * 0.32 + i * span / nR) % span) / span; ctx.globalAlpha = 0.9 * (1 - q); ctx.fillStyle = i & 1 ? st.c1 : st.c0; ringPx(ctx, mx, my, Math.round(r + 1 + q * span)); if (tier === 3) { ctx.fillStyle = '#ff7ad8'; ringPx(ctx, mx + 1, my, Math.round(r + 1 + q * span)); ctx.fillStyle = '#7ae0ff'; ringPx(ctx, mx - 1, my, Math.round(r + 1 + q * span)); } }
      ctx.globalAlpha = 1; ctx.fillStyle = tier === 3 ? st.hot[(t >> 1) & 3] : st.c0; disc(ctx, mx, my, r);
      if (r >= 3) { ctx.fillStyle = st.c1; disc(ctx, mx, my, Math.max(1, r - 2)); }
      if (tier >= 2) { ctx.fillStyle = '#ffffff'; disc(ctx, mx, my, tier === 3 ? 3 : 2); const k = tier === 3 ? 6 : 3; for (let i = 0; i < k; i++) { const a = t * 0.22 + i * 6.2832 / k, w = Math.sin(t * 0.4 + i * 2) * 2; ctx.fillStyle = i & 1 ? '#ffffff' : st.c1; ctx.fillRect(Math.round(mx + Math.cos(a) * (r + 5 + w)) - 1, Math.round(my + Math.sin(a) * (r + 5 + w)) - 1, 2, 2); } }
    },
    plasma(ctx, mx, my, tier, f, r, t, st) {                                                                          /* a fireball with licking flames */
      tongues(ctx, mx, my, r, 5 + tier * 2, t, 3 + tier * 3, st);
      ctx.fillStyle = st.dk; ctx.globalAlpha = 0.85; disc(ctx, mx, my, r + 1); ctx.globalAlpha = 1;
      ctx.fillStyle = tier === 3 ? st.hot[3 - ((t >> 1) & 1)] : st.c0; disc(ctx, mx, my, r);
      if (r >= 2) { ctx.fillStyle = '#ffb040'; disc(ctx, mx, my, Math.max(1, r - 1)); }
      if (r >= 3) { ctx.fillStyle = st.c1; disc(ctx, mx, my, Math.max(1, r - 3)); }
      if (tier >= 2) { ctx.fillStyle = '#ffffff'; disc(ctx, mx, my, tier === 3 ? 3 : 2); }
      const nE = 3 + tier * 2; for (let i = 0; i < nE; i++) { const q = ((t * 0.9 + i * 11) % 30) / 30; ctx.globalAlpha = 1 - q; ctx.fillStyle = q < 0.4 ? st.c1 : q < 0.75 ? st.c0 : st.dk; ctx.fillRect(Math.round(mx + Math.sin(i * 3.1 + t * 0.06) * (r + 3)), Math.round(my - r - q * (10 + tier * 6)), 1, 1); }
      ctx.globalAlpha = 1;
    },
  };
  R.chargeFx = function (ctx, g, p, time) {
    const ch = p.charge; if (!(ch > 0)) return;
    const CH = G.weapons.CHARGE, m = G.player.muzzle(p), mx = Math.round(m.x), my = Math.round(m.y), sty = styleOf(g.abil), st = STY[sty], mods = modsOf(g.abil, sty), t = Math.floor(time * 60);
    const tier = ch >= CH.mega ? 3 : ch >= CH.full ? 2 : ch >= CH.min ? 1 : 0, f = Math.min(1, ch / CH.full), pul = Math.sin(t * 0.55);
    ctx.save();
    if (tier >= 2) { ctx.globalCompositeOperation = 'lighter'; ctx.fillStyle = st.c0; ctx.globalAlpha = (tier === 3 ? 0.2 : 0.11) + 0.05 * pul; disc(ctx, Math.round(p.x), Math.round(p.y - 32), 13); disc(ctx, Math.round(p.x), Math.round(p.y - 14), 13); ctx.globalCompositeOperation = 'source-over'; }   /* the hero glows once the shot is ready */
    if (sty === 'base' || sty === 'ice') {                                                                            /* energy (or frost) streaming in toward the muzzle */
      const n = tier === 0 ? 2 : tier === 1 ? 4 : tier === 2 ? 6 : 9, slow = sty === 'ice' ? 28 : 20;
      for (let i = 0; i < n; i++) { const ph = ((t + i * 5) % slow) / slow, a = i * 2.399 + t * 0.07, d = (1 - ph) * (9 + tier * 6); ctx.fillStyle = ph > 0.65 ? st.c1 : st.c0; ctx.globalAlpha = 0.35 + 0.65 * ph; ctx.fillRect(Math.round(mx + Math.cos(a) * d), Math.round(my + Math.sin(a) * d), sty === 'ice' && (i & 1) ? 2 : 1, sty === 'ice' && (i & 1) ? 2 : 1); }
      ctx.globalAlpha = 1;
    }
    const r = tier === 0 ? 1 : tier === 1 ? 2 + Math.round(f * 3) : tier === 2 ? 6 : 9 + (pul > 0 ? 1 : 0);
    if (tier >= 1) { ctx.globalCompositeOperation = 'lighter'; ctx.fillStyle = st.c0; ctx.globalAlpha = 0.16 + 0.05 * tier; disc(ctx, mx, my, r + 3 + tier); ctx.globalAlpha = 0.22; disc(ctx, mx, my, r + 1); ctx.globalCompositeOperation = 'source-over'; ctx.globalAlpha = 1; }
    ORB[sty](ctx, mx, my, tier, f, r, t, st);
    if (tier >= 1) accents(ctx, mx, my, r, mods, t, tier);
    if (tier >= 2 && t % 3 === 0) { ctx.fillStyle = '#ffffff'; let ax = mx, ay = my; const a = Math.random() * 6.28, L = 8 + Math.random() * 8; for (let i = 0; i < L; i++) { ax += Math.cos(a) + (Math.random() - 0.5) * 1.6; ay += Math.sin(a) + (Math.random() - 0.5) * 1.6; ctx.fillRect(Math.round(ax), Math.round(ay), 1, 1); } }    /* arcs */
    for (const th of [CH.full, CH.mega]) if (ch >= th && ch < th + 9) { ctx.fillStyle = '#ffffff'; ctx.globalAlpha = 1 - (ch - th) / 9; ringPx(ctx, mx, my, 6 + (ch - th) * 3); ringPx(ctx, mx, my, 5 + (ch - th) * 3); ctx.globalAlpha = 1; }   /* a ring bursts out as each level is reached */
    ctx.restore();
  };
  /* the fired shots, one per beam type, tier 1 = partial, 2 = full, 3 = overcharge. Each draws from (x, y) = shot centre along the unit direction (ux, uy) */
  const glow = (ctx, x, y, r, col, a) => { ctx.globalCompositeOperation = 'lighter'; ctx.fillStyle = col; ctx.globalAlpha = a; disc(ctx, x, y, r); ctx.globalCompositeOperation = 'source-over'; ctx.globalAlpha = 1; };
  const SHOT = {
    base(ctx, s, st, x, y, ux, uy, t, tier) {
      const nT = tier === 1 ? 5 : tier === 2 ? 8 : 13, gap = tier === 1 ? 2.6 : tier === 2 ? 3 : 3.4;
      ctx.globalCompositeOperation = 'lighter'; ctx.fillStyle = st.c0;
      for (let i = nT; i >= 1; i--) { const k = 1 - i / (nT + 1); ctx.globalAlpha = 0.5 * k; disc(ctx, Math.round(s.x - ux * i * gap), Math.round(s.y - uy * i * gap), Math.max(1, Math.round(s.r * k * 0.95))); }
      ctx.globalCompositeOperation = 'source-over'; ctx.globalAlpha = 1; glow(ctx, x, y, s.r + 3 + tier, st.c0, 0.2 + (tier === 3 ? 0.08 * Math.sin(t * 0.6) : 0));
      ctx.fillStyle = tier === 3 ? st.hot[(t >> 1) & 3] : st.c0; disc(ctx, x, y, s.r); ctx.fillStyle = tier === 3 ? '#ffffff' : st.c1; disc(ctx, x, y, Math.max(1, s.r - 2));
      if (tier >= 2) { ctx.fillStyle = '#ffffff'; disc(ctx, x, y, tier === 3 ? 4 : 2); ctx.fillStyle = st.c1; flare(ctx, x, y, s.r + 3 + (t & 1) * 2, tier === 3 ? s.r + 1 : 0); }
      if (tier >= 2) { ctx.fillStyle = st.c1; for (let i = 1; i <= (tier === 3 ? 4 : 2); i++) { ctx.globalAlpha = 0.5 / i; ringPx(ctx, Math.round(s.x - ux * i * (6 + tier)), Math.round(s.y - uy * i * (6 + tier)), Math.round(s.r * (0.9 + i * 0.12))); } ctx.globalAlpha = 1; }   /* pulse rings left behind */
      if (tier === 3) for (let i = 0; i < 6; i++) { const a = t * 0.34 + i * 1.0472, d = s.r + 4 + Math.sin(t * 0.5 + i) * 1.5; ctx.fillStyle = i & 1 ? '#ffffff' : st.c1; ctx.fillRect(Math.round(x + Math.cos(a) * d) - 1, Math.round(y + Math.sin(a) * d) - 1, 3, 3); }
    },
    ice(ctx, s, st, x, y, ux, uy, t, tier) {
      const L = [0, 5 + s.f * 3, 10, 18][tier], Wd = [0, 2.6 + s.f, 5, 6.8][tier], px = -uy, py = ux;
      const nM = tier === 1 ? 0 : tier === 2 ? 4 : 8;                                                                  /* mist */
      ctx.globalCompositeOperation = 'lighter'; ctx.fillStyle = st.c0;
      for (let i = 1; i <= nM; i++) { ctx.globalAlpha = 0.2 * (1 - i / (nM + 1)); disc(ctx, Math.round(s.x - ux * (L * 0.5 + i * 4)), Math.round(s.y - uy * (L * 0.5 + i * 4)), Math.round(2 + i * 0.7 + tier)); }
      ctx.globalCompositeOperation = 'source-over'; ctx.globalAlpha = 1; glow(ctx, x, y, Math.round(Wd + 3), st.c0, 0.2);
      for (let i = 1; i <= 8 + tier * 2; i++) { const d = L * 0.6 + i * 2.1 + ((t * 0.7 + i * 3) % 3), o = Math.sin(i * 2.4 + t * 0.4) * (1.5 + tier), q = i / (9 + tier * 2); ctx.globalAlpha = 1 - q; ctx.fillStyle = i & 1 ? st.c1 : st.c0; ctx.fillRect(Math.round(s.x - ux * d + px * o), Math.round(s.y - uy * d + py * o + q * 3), 1, 1); }   /* frost dust drifting down behind */
      ctx.globalAlpha = 1;
      if (tier >= 2) { ctx.fillStyle = st.c0; const k = tier === 3 ? 3 : 2; for (let i = 0; i < k; i++) for (const sg of [-1, 1]) rhombus(ctx, s.x - ux * (3 + i * 5) + px * sg * (Wd + 2 + i), s.y - uy * (3 + i * 5) + py * sg * (Wd + 2 + i), ux, uy, 3.2 - i * 0.5, 1.6); }   /* shards flanking the crystal */
      ctx.fillStyle = st.dk; rhombus(ctx, s.x, s.y, ux, uy, L + 1.4, Wd + 1.2); ctx.fillStyle = tier === 3 ? st.hot[(t >> 2) & 3] : st.c0; rhombus(ctx, s.x, s.y, ux, uy, L, Wd);
      ctx.fillStyle = st.c1; rhombus(ctx, s.x, s.y, ux, uy, L * (tier === 3 ? 0.5 : 0.62), Wd * (tier === 3 ? 0.42 : 0.55)); ctx.fillStyle = '#ffffff'; rhombus(ctx, s.x, s.y, ux, uy, L * (tier === 3 ? 0.24 : 0.3), Wd * (tier === 3 ? 0.2 : 0.3));
      if (tier >= 2) { ctx.fillStyle = '#ffffff'; const n = Math.round(L * 1.4); for (let i = -n / 2; i < n / 2; i++) ctx.fillRect(Math.round(s.x + ux * i), Math.round(s.y + uy * i), 1, 1); }
      if (tier === 3) { ctx.fillStyle = st.c1; ctx.globalAlpha = 0.85; snow(ctx, x + Math.round(ux * L * 0.5), y + Math.round(uy * L * 0.5), t * 0.05, 9, true); ctx.globalAlpha = 1; for (let i = 0; i < 6; i++) { const a = -t * 0.18 + i * 1.0472; ctx.fillStyle = i & 1 ? '#ffffff' : st.c0; rhombus(ctx, x + Math.cos(a) * (Wd + 6), y + Math.sin(a) * (Wd + 6), Math.cos(a + 1.57), Math.sin(a + 1.57), 2.6, 1.3); } }
    },
    wave(ctx, s, st, x, y, ux, uy, t, tier) {
      const ang = Math.atan2(uy, ux), ph = -t * 0.55;
      glow(ctx, x, y, s.r + 4, st.c0, 0.2);
      ctx.fillStyle = st.dk; ribbon(ctx, s.x, s.y, ux, uy, [0, 20, 28, 36][tier], [0, 3, 4.5, 6.5][tier], 0.5, ph, 3);                    /* the ribbon the shot leaves in its wake */
      ctx.fillStyle = st.c0; ribbon(ctx, s.x, s.y, ux, uy, [0, 20, 28, 36][tier], [0, 3, 4.5, 6.5][tier], 0.5, ph, 2);
      if (tier >= 2) { ctx.fillStyle = st.c1; ribbon(ctx, s.x, s.y, ux, uy, [0, 0, 28, 36][tier], [0, 0, 4.5, 6.5][tier], 0.5, ph + 3.14, 2); }
      if (tier === 3) { ctx.fillStyle = '#ff7ad8'; ribbon(ctx, s.x + 0, s.y - 1, ux, uy, 30, 6, 0.5, ph + 1.5, 1); ctx.fillStyle = '#7ae0ff'; ribbon(ctx, s.x, s.y + 1, ux, uy, 30, 6, 0.5, ph - 1.5, 1); }
      if (tier === 1) { ctx.fillStyle = st.c0; ringPx(ctx, x, y, s.r); ringPx(ctx, x, y, s.r - 1); ctx.fillStyle = st.c1; disc(ctx, x, y, 1); }
      else {
        ctx.fillStyle = tier === 3 ? st.hot[(t >> 1) & 3] : st.c0; disc(ctx, x, y, s.r - (tier === 3 ? 1 : 1)); ctx.fillStyle = st.c1; disc(ctx, x, y, Math.max(1, s.r - 3)); ctx.fillStyle = '#ffffff'; disc(ctx, x, y, tier === 3 ? 3 : 1);
        ctx.fillStyle = st.c1; ringPx(ctx, x, y, s.r + 1);
      }
      if (tier === 3) for (let i = 0; i < 3; i++) { ctx.fillStyle = i === 1 ? '#ffffff' : st.c1; ctx.globalAlpha = 1 - i * 0.28; arcPx(ctx, x, y, s.r + 4 + i * 4 + (t % 4 < 2 ? 1 : 0), ang - 1.0, ang + 1.0); arcPx(ctx, x, y, s.r + 5 + i * 4 + (t % 4 < 2 ? 1 : 0), ang - 0.95, ang + 0.95); } ctx.globalAlpha = 1;   /* crescent wave fronts racing ahead */
      if (tier === 2) { ctx.fillStyle = st.c1; ctx.globalAlpha = 0.7; arcPx(ctx, x, y, s.r + 4, ang - 0.9, ang + 0.9); ctx.globalAlpha = 1; }
    },
    plasma(ctx, s, st, x, y, ux, uy, t, tier) {
      const px = -uy, py = ux, nT = [0, 7, 10, 15][tier];
      glow(ctx, x, y, s.r + 4 + tier, st.c0, 0.22);
      for (let i = nT; i >= 1; i--) { const q = i / nT, o = Math.sin(t * 0.7 + i * 1.7) * (1 + tier * 0.7) * q; ctx.fillStyle = q < 0.3 ? st.c0 : q < 0.65 ? st.dk : '#4a2018'; ctx.globalAlpha = (q < 0.65 ? 0.9 : 0.5) * (1 - q * 0.6); disc(ctx, Math.round(s.x - ux * i * (2.2 + tier * 0.5) + px * o), Math.round(s.y - uy * i * (2.2 + tier * 0.5) + py * o), Math.max(1, Math.round(s.r * (1 - q) * 0.9))); } ctx.globalAlpha = 1;   /* a flickering fire tail that cools to smoke */
      if (tier >= 2) tongues(ctx, x, y, s.r, tier === 3 ? 9 : 6, t, tier === 3 ? 9 : 5, st);
      ctx.fillStyle = st.dk; ctx.globalAlpha = 0.8; disc(ctx, x, y, s.r + (tier === 3 ? 2 : 1)); ctx.globalAlpha = 1;
      ctx.fillStyle = tier === 3 ? st.hot[3 - ((t >> 1) & 1)] : st.c0; disc(ctx, x, y, s.r); ctx.fillStyle = '#ffb040'; disc(ctx, x, y, Math.max(1, s.r - 2)); ctx.fillStyle = st.c1; disc(ctx, x, y, Math.max(1, s.r - 4 + (tier === 1 ? 1 : 0)));
      if (tier >= 2) { ctx.fillStyle = '#ffffff'; disc(ctx, x, y, tier === 3 ? 3 : 1); }
      for (let i = 0; i < 2 + tier * 2; i++) { const q = ((t * 1.1 + i * 7) % 24) / 24, d = s.r + q * (10 + tier * 5), o = Math.sin(i * 4.3 + t * 0.1) * (s.r + 1); ctx.globalAlpha = 1 - q; ctx.fillStyle = q < 0.35 ? st.c1 : q < 0.7 ? st.c0 : st.dk; ctx.fillRect(Math.round(s.x - ux * d + px * o), Math.round(s.y - uy * d + py * o), 1, 1); } ctx.globalAlpha = 1;   /* embers */
    },
  };
  R.chargedShot = function (ctx, s, time) {
    const x = Math.round(s.x), y = Math.round(s.y), sp = Math.hypot(s.vx, s.vy) || 1, ux = s.vx / sp, uy = s.vy / sp, sty = s.style || 'base';
    ctx.save(); SHOT[sty](ctx, s, STY[sty], x, y, ux, uy, s.t, s.tier); accents(ctx, x, y, s.r, s.mods || [], s.t, s.tier); ctx.restore();
  };
  /* the ordinary quick shot, also one look per beam */
  R.plainShot = function (ctx, s) {
    const sty = s.style || 'base', st = STY[sty], sp = Math.hypot(s.vx, s.vy) || 1, ux = s.vx / sp, uy = s.vy / sp, px = -uy, py = ux, t = s.t;
    for (let i = 5; i >= 0; i--) {
      let o = 0; if (sty === 'wave') o = Math.sin(t * 0.7 - i * 0.9) * 1.5;
      const x = Math.round(s.x - ux * i * 1.8 + px * o), y = Math.round(s.y - uy * i * 1.8 + py * o);
      ctx.fillStyle = i === 0 ? st.c1 : sty === 'plasma' && i > 3 ? st.dk : st.c0; ctx.globalAlpha = i > 3 ? 0.55 : 1;
      const big = i === 0 ? 3 : 2; if (sty === 'ice' && i === 0) { ctx.fillRect(x - 1, y - 1, 3, 3); ctx.fillStyle = '#ffffff'; ctx.fillRect(x, y, 1, 1); } else ctx.fillRect(x - 1, y - 1, big, big);
    }
    ctx.globalAlpha = 1;
    if (sty === 'ice' && t % 2 === 0) { ctx.fillStyle = '#ffffff'; ctx.fillRect(Math.round(s.x - ux * (4 + t % 6) + px * ((t * 5) % 5 - 2)), Math.round(s.y - uy * (4 + t % 6) + py * ((t * 5) % 5 - 2) + 1), 1, 1); }
    if (sty === 'plasma' && t % 2 === 0) { ctx.fillStyle = t & 2 ? st.c1 : st.c0; ctx.fillRect(Math.round(s.x - ux * (6 + t % 5) + px * ((t * 3) % 5 - 2)), Math.round(s.y - uy * (6 + t % 5) + py * ((t * 3) % 5 - 2) - 1), 1, 1); }
    if (s.mods && s.mods.length) accents(ctx, Math.round(s.x), Math.round(s.y), 1, s.mods, t, 0);
  };
  R.shot = function (ctx, s, time) {
    const x = Math.round(s.x), y = Math.round(s.y);
    if (s.kind === 'beam') {
      if (s.tier >= 1) return R.chargedShot(ctx, s, time);
      return R.plainShot(ctx, s);
    } else {
      const sup = s.kind === 'super', dx = s.dx, dy = s.dy;
      ctx.fillStyle = sup ? '#6cf08a' : '#e8ecf8';
      const len = 5; for (let i = 0; i < len; i++) ctx.fillRect(Math.round(s.x - dx * i * 1.2) - 1, Math.round(s.y - dy * i * 1.2) - 1, 3, 3);
      ctx.fillStyle = sup ? '#2a8a4a' : '#ec5c4a'; ctx.fillRect(Math.round(s.x + dx * 3) - 1, Math.round(s.y + dy * 3) - 1, 3, 3);
      ctx.fillStyle = '#ffd24a'; ctx.fillRect(Math.round(s.x - dx * 6) - 1, Math.round(s.y - dy * 6) - 1, 2, 2);
    }
  };
})((window.SGS = window.SGS || {}));
