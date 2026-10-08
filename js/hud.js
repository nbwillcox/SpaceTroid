/* Heads-up display: energy + tanks, missile / super counts, charge bar. */
(function (G) {
  'use strict';
  const PX = G.px, H = {};
  G.hud = H;
  const txt = (ctx, s, x, y, c, a) => PX.text(ctx, s, x, y, { s: 1, c: c || '#e8f0ff', o: '#0a0e2c', a });
  H.draw = function (ctx, g, time) {
    const p = g.P, max = G.player.enMax(p), full = Math.floor(p.en / 100), rest = Math.ceil(p.en % 100);
    ctx.fillStyle = 'rgba(10,14,44,0.55)'; ctx.fillRect(4, 4, 92, 30);
    txt(ctx, 'EN', 8, 8, '#86f0f2'); txt(ctx, String(Math.max(0, p.en > 0 && p.en < 1 ? 1 : Math.ceil(p.en))).padStart(3, '0'), 24, 8, p.en < 30 && Math.floor(time * 4) % 2 ? '#ec5c4a' : '#ffffff');
    for (let i = 0; i < p.tanks; i++) { const x = 8 + i * 8, on = i < full; ctx.fillStyle = on ? '#8ea2d2' : '#2a3050'; ctx.fillRect(x, 17, 6, 1); ctx.fillRect(x, 24, 6, 1); ctx.fillStyle = on ? '#2c6ad8' : '#162050'; ctx.fillRect(x, 18, 6, 6); ctx.fillStyle = on ? '#f2ffff' : '#3a4a80'; ctx.fillRect(x + 2, 19, 2, 1); ctx.fillRect(x + 2, 21, 2, 1); ctx.fillRect(x + 2, 23, 2, 1); ctx.fillRect(x + 1, 19, 1, 5); }
    ctx.fillStyle = '#10142e'; ctx.fillRect(8, 26, 84, 3); ctx.fillStyle = p.en / max < 0.3 ? '#ec5c4a' : '#4cd2b8'; ctx.fillRect(8, 26, Math.round(84 * Math.min(1, p.en / Math.max(1, max))), 3);
    const DS = G.sprites.drop;
    if (g.abil.missiles) { const sel = p.sel === 0; ctx.fillStyle = sel ? '#efba42' : '#3a3550'; ctx.fillRect(100, 5, 36, 14); ctx.fillStyle = '#10142e'; ctx.fillRect(101, 6, 34, 12); ctx.drawImage(DS.missile[0], 105, 6); txt(ctx, String(p.missiles).padStart(2, '0'), 117, 9, sel ? '#fff2a8' : '#98a6ca'); }
    if (g.abil.supers) { const sel = p.sel === 1; ctx.fillStyle = sel ? '#6cf08a' : '#3a3550'; ctx.fillRect(138, 5, 30, 14); ctx.fillStyle = '#10142e'; ctx.fillRect(139, 6, 28, 12); ctx.drawImage(DS.super[0], 143, 6); txt(ctx, String(p.supers).padStart(2, '0'), 152, 9, sel ? '#d8ffe0' : '#98a6ca'); }
    if (g.abil.sbombs) { ctx.fillStyle = '#3a3550'; ctx.fillRect(170, 5, 30, 14); ctx.fillStyle = '#10142e'; ctx.fillRect(171, 6, 28, 12); ctx.drawImage(DS.sbomb[0], 173, 6); txt(ctx, String(p.sbombs).padStart(2, '0'), 184, 9, '#ffe2b0'); }
    if (p.charge > 0) {
      const CH = G.weapons.CHARGE, c = p.charge >= CH.mega ? (Math.floor(time * 12) & 1 ? '#ffffff' : '#ff9ad8') : p.charge >= CH.full ? '#ffffff' : p.charge >= CH.min ? '#ffd24a' : '#8a7a40';
      ctx.fillStyle = '#10142e'; ctx.fillRect(100, 22, 40, 5); ctx.fillStyle = c; ctx.fillRect(101, 23, Math.round(38 * p.charge / CH.max), 3);
      ctx.fillStyle = '#566cac'; for (const th of [CH.min, CH.full, CH.mega]) ctx.fillRect(101 + Math.round(38 * th / CH.max), 22, 1, 1);
    }
    const B = g.abil.beams; let x = 102; for (const [k, c, n] of [['ice', '#7ad8ff', 'I'], ['wave', '#b878ff', 'W'], ['plasma', '#ff7a2a', 'P']]) if (g.abil['has' + n.replace('I', 'Ice').replace('W', 'Wave').replace('P', 'Plasma')]) { ctx.fillStyle = B[k] ? c : '#2a3050'; ctx.fillRect(x, 31, 6, 3); x += 8; }
    if (p.dead > 30) { ctx.fillStyle = 'rgba(10,14,44,' + Math.min(0.8, (p.dead - 30) / 60) + ')'; ctx.fillRect(0, 0, 480, 270); if (p.dead > 60) PX.text(ctx, 'SIGNAL LOST', 240, 128, { s: 2, c: '#ec5c4a', o: '#0a0e2c', a: 'c' }); }
  };
  /* everything drawn over the HUD: minimap, boss bar, toast, item banner, fades */
  H.overlay = function (ctx, g, time) {
    const Mo = G.input.mouse;
    if (G.settings.mouseAim && Mo.on && !g.banner && !g.trans && !g.getAnim && !g.saveAnim && g.P.mode !== 'ball' && !G.input.stick) {   /* aiming reticle */
      const x = Math.round(Mo.x), y = Math.round(Mo.y), pulse = Math.floor(time * 4) & 1;
      ctx.fillStyle = '#0a0e2c'; for (const [dx, dy, w, h] of [[-6, -1, 4, 3], [3, -1, 4, 3], [-1, -6, 3, 4], [-1, 3, 3, 4]]) ctx.fillRect(x + dx - 1, y + dy - 1, w + 2, h + 2);
      ctx.fillStyle = pulse ? '#ffffff' : '#86f0f2'; for (const [dx, dy, w, h] of [[-6, 0, 4, 1], [3, 0, 4, 1], [0, -6, 1, 4], [0, 3, 1, 4]]) ctx.fillRect(x + dx, y + dy, w, h);
      ctx.fillStyle = '#ec5c4a'; ctx.fillRect(x, y, 1, 1);
    }
    if (G.map) G.map.mini(ctx, g, time);
    const b = g.boss;
    if (b && b.state !== 'wait') {
      const w = 220, x = 130, y = 250; ctx.fillStyle = 'rgba(10,14,44,0.7)'; ctx.fillRect(x - 3, y - 12, w + 6, 20); txt(ctx, b.name, 240, y - 10, '#ffb89c', 'c');
      ctx.fillStyle = '#2a0812'; ctx.fillRect(x, y, w, 5); ctx.fillStyle = b.state === 'stun' ? '#f2ffff' : '#ec5c4a'; ctx.fillRect(x, y, Math.round(w * Math.max(0, b.hp) / b.hpMax), 5);
    }
    if (g.escape) {
      const t = Math.max(0, Math.ceil(g.escape.t / 60)), mm = String(Math.floor(t / 60)).padStart(2, '0'), ss = String(t % 60).padStart(2, '0'), urgent = t < 30 && Math.floor(time * 3) % 2;
      ctx.fillStyle = 'rgba(40,6,12,0.75)'; ctx.fillRect(180, 4, 120, 26); PX.text(ctx, 'ESCAPE', 240, 7, { s: 1, c: '#ff80c8', o: '#0a0e2c', a: 'c' }); PX.text(ctx, mm + ':' + ss, 240, 17, { s: 2, c: urgent ? '#ffffff' : '#ffd0f0', o: '#400818', a: 'c' });
    }
    if (g.toast) { const a = g.toast.t < 10 ? g.toast.t / 10 : g.toast.t > 130 ? (150 - g.toast.t) / 20 : 1; ctx.globalAlpha = Math.max(0, a); ctx.fillStyle = 'rgba(10,14,44,0.8)'; ctx.fillRect(160, 58, 160, 16); txt(ctx, g.toast.txt, 240, 63, '#f2ffff', 'c'); ctx.globalAlpha = 1; }
    if (g.banner) {
      const bn = g.banner, k = Math.min(1, bn.t / 12), h = Math.round(86 * k), y = 98 + (86 - h) / 2;
      ctx.fillStyle = 'rgba(8,10,34,0.92)'; ctx.fillRect(70, y, 340, h); ctx.fillStyle = '#5688dc'; ctx.fillRect(70, y, 340, 1); ctx.fillRect(70, y + h - 1, 340, 1);
      if (k >= 1) {
        if (bn.type) { const dfn = G.world.ITEMS[bn.type], im = dfn.tank ? G.sprites.tank[dfn.tank][(Math.floor(time * 3)) & 1] : G.sprites.icon[bn.type]; ctx.imageSmoothingEnabled = false; for (const bx of [86, 354]) ctx.drawImage(im, bx, 112, im.width * 2, im.height * 2); }
        txt(ctx, 'ITEM ACQUIRED', 240, 106, '#86f0f2', 'c'); PX.text(ctx, bn.name, 240, 122, { s: 2, c: '#fff2a8', o: '#2e1a0c', a: 'c' });
        bn.lines.forEach((l, i) => txt(ctx, l, 240, 148 + i * 11, '#dde7fb', 'c'));
        if (bn.t > 50 && Math.floor(time * 2) % 2) txt(ctx, 'PRESS JUMP', 240, 172, '#8ea2d2', 'c');
      }
    }
    if (g.room.scanOn) { PX.text(ctx, 'SCAN', 206, 24, { s: 1, c: Math.floor(time * 2) & 1 ? '#f2ffff' : '#86f0f2', o: '#0a0e2c' }); }
    if (g.room.scanOn) { ctx.fillStyle = 'rgba(40,180,200,0.10)'; ctx.fillRect(0, 0, 480, 270); for (let y = (Math.floor(time * 40) % 4); y < 270; y += 4) { ctx.fillStyle = 'rgba(134,240,242,0.06)'; ctx.fillRect(0, y, 480, 1); } }
    if (g.P.hurt > 0 && !G.settings.reduced) { ctx.fillStyle = 'rgba(255,50,50,' + (0.16 * g.P.hurt / 14).toFixed(3) + ')'; ctx.fillRect(0, 0, 480, 270); }
    let f = 0; if (g.fade) f = g.fade.dir < 0 ? g.fade.t / g.fade.len : 1 - g.fade.t / g.fade.len;
    if (g.trans) f = g.trans.phase === 'out' ? Math.min(1, g.trans.t / 10) : 1 - Math.min(1, g.trans.t / 10);
    if (f > 0) { ctx.fillStyle = 'rgba(5,7,26,' + f + ')'; ctx.fillRect(0, 0, 480, 270); }
  };
})((window.SGS = window.SGS || {}));
