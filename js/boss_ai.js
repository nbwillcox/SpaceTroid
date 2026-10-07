/* Warden AI + drawing (state machine). Needs js/bosses.js. */
(function (G) {
  'use strict';
  const U = G.U, B = G.bosses;
  B.updateBeetle = function (g) {
    const b = g.boss, p = g.P;
    if (!b) { B.updateRocks(g); return; }
    b.t++; b.flash = Math.max(0, b.flash - 1); b.anim += 0.1;
    const lo = B.PAD + 14, hi = g.room.pw - B.PAD - 14, sp = [0, 0.55, 0.75, 0.95][b.phase];
    const faceP = () => { b.face = p.x >= b.x ? 1 : -1; };
    if (b.state === 'wait') { if (p.x > 150) { b.state = 'intro'; b.t = 0; G.world.sealDoors(g); } }
    else if (b.state === 'intro') { faceP(); g.shake = Math.max(g.shake, 2); if (b.t === 20) G.audio.sfx('boom'); if (b.t > 90) { b.state = 'walk'; b.t = 0; } }
    else if (b.state === 'walk') {
      faceP(); b.x = U.clamp(b.x + b.face * sp, lo, hi);
      if (b.t > 120 - b.phase * 15) { const far = Math.abs(p.x - b.x) > 200; b.state = Math.random() < (far ? 0.7 : 0.4) ? 'tele' : 'volley'; b.t = 0; }
    } else if (b.state === 'volley') { if (b.t === 24) B.volley(g, b); if (b.t > 52) { b.state = 'walk'; b.t = 0; } }
    else if (b.state === 'tele') {
      faceP(); if (b.t % 12 === 0) G.fx.puff(b.x - b.face * 40, b.y, 3);
      if (b.t > 48) { b.state = 'charge'; b.t = 0; b.vx = b.face * [0, 3.6, 4.1, 4.8][b.phase]; G.audio.sfx('missile'); }
    } else if (b.state === 'charge') {
      b.x += b.vx; if (b.t % 4 === 0) G.fx.puff(b.x - Math.sign(b.vx) * 40, b.y, 2);
      if (b.x <= lo || b.x >= hi) {
        b.x = U.clamp(b.x, lo, hi); b.state = 'stun'; b.t = 0; b.vx = 0; g.shake = 12; G.audio.sfx('boom');
        G.fx.debris(b.x + b.face * 44, b.y - 30, ['#52627a', '#7f8c96', '#33405e']);
        if (b.phase >= 2) B.rocks(g, b.phase === 3 ? 6 : 4);
        B.dropItems(g);
      }
    } else if (b.state === 'stun') {
      if (b.phase === 3 && b.t % 70 === 0) B.rocks(g, 2);
      if (b.t > (b.phase === 3 ? 160 : 190)) { b.state = b.phase === 3 && Math.random() < 0.5 ? 'tele' : 'walk'; b.t = 0; }
    } else if (b.state === 'dying') {
      if (b.t % 6 === 0) G.fx.boom(b.x + (Math.random() - 0.5) * 90, b.y - 10 - Math.random() * 50, 9);
      g.shake = 5; if (b.t === 140) B.finish(g, b);
    }
    if (!g.boss) { B.updateRocks(g); return; }
    if (!p.dead && b.state !== 'wait' && !b.dead && Math.abs(p.x - b.x) < (p.w + b.w) / 2 - 4 && p.y > b.y - b.h + 12 && p.y - p.h < b.y - 4) { if (G.player.hurt(g, p, b.state === 'charge' ? 24 : 15, b.x)) G.audio.sfx('hurt'); }
    if (!b.dead) for (const s of g.shots) {
      if (s.dead) continue;
      const near = Math.abs(s.x - b.x) < b.w / 2 + 4 && s.y > b.y - b.h - 20 && s.y < b.y;
      if (!near) continue;
      const hitCore = B.vulnerable(b) && B.inCore(b, s.x, s.y);
      if (s.kind === 'missile' || s.kind === 'super') { s.dead = true; G.fx.boom(s.x, s.y, 10); if (hitCore) B.damage(g, b, s.dmg); else G.audio.sfx('hit'); }
      else if (hitCore) { B.damage(g, b, s.dmg); if (!s.pierce) s.dead = true; G.fx.sparkBurst(s.x, s.y, '#f2ffff', 5); }
      else if (!s.hit.has(b)) { s.hit.add(b); if (!s.pierce) s.dead = true; G.fx.sparkBurst(s.x, s.y, '#fff', 3); G.audio.sfx('hit'); }
    }
    B.updateRocks(g);
  };
  const whites = new Map();
  const whiteOf = (c) => { let w = whites.get(c); if (!w) { w = document.createElement('canvas'); w.width = c.width; w.height = c.height; const x = w.getContext('2d'); x.drawImage(c, 0, 0); x.globalCompositeOperation = 'source-in'; x.fillStyle = '#fff'; x.fillRect(0, 0, w.width, w.height); whites.set(c, w); } return w; };
  B.drawRocks = function (ctx, g) {
    for (const r of g.rocks || []) {
      const x = Math.round(r.x), y = Math.round(r.y);
      if (r.ice) { ctx.fillStyle = '#6e9fd0'; ctx.fillRect(x - 3, y - 14, 6, 10); ctx.fillRect(x - 2, y - 4, 4, 4); ctx.fillStyle = '#dff4fc'; ctx.fillRect(x - 3, y - 14, 2, 10); ctx.fillStyle = '#3a64a0'; ctx.fillRect(x + 1, y - 12, 2, 8); ctx.fillRect(x - 1, y, 2, 3); continue; }
      ctx.fillStyle = '#33405e'; ctx.fillRect(x - 6, y - 12, 12, 12); ctx.fillStyle = '#7f8c96'; ctx.fillRect(x - 5, y - 11, 5, 3); ctx.fillStyle = '#1f2744'; ctx.fillRect(x + 2, y - 5, 4, 5);
    }
  };
  B.drawBeetle = function (ctx, g) {
    const b = g.boss; if (!b) return;
    const SP = G.sprites.boss; let fr;
    if (b.state === 'wait' || b.state === 'walk') fr = SP.walk[Math.floor(b.anim * 1.4) & 3];
    else if (b.state === 'intro' || b.state === 'volley') fr = SP.rear;
    else if (b.state === 'tele') fr = SP.tele[(b.t >> 2) & 1];
    else if (b.state === 'charge') fr = SP.charge[(b.t >> 2) & 1];
    else fr = SP.stun[(b.t >> 3) & 1];
    const c = b.face >= 0 ? fr.r : fr.l, ax = b.face >= 0 ? fr.ax : fr.w - 1 - fr.ax, x = Math.round(b.x - ax), y = Math.round(b.y - fr.ay);
    ctx.drawImage(c, x + (b.state === 'dying' ? Math.round((Math.random() - 0.5) * 3) : 0), y);
    if (b.flash > 0) { ctx.globalAlpha = 0.6; ctx.drawImage(whiteOf(c), x, y); ctx.globalAlpha = 1; }
  };
})((window.SGS = window.SGS || {}));
