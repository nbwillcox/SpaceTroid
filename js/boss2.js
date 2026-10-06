/* Zone 2 boss AI + drawing: the Rimewing Sovereign (flying ice moth). Hover and fire shard fans, telegraph, dive to the floor, stunned with the core exposed. Also routes boss update / draw by kind. */
(function (G) {
  'use strict';
  const U = G.U, B = G.bosses, FLOOR_Y = 240 - 47;
  B.update = function (g) { const b = g.boss; if (b && b.kind === 'moth') B.updateMoth(g); else if (b && b.kind === 'wyrm') B.updateWyrm(g); else if (b && b.kind === 'jelly') B.updateJelly(g); else if (b && b.kind === 'heart') { B.updateHeart(g); B.updateRocks(g); } else B.updateBeetle(g); };
  B.draw = function (ctx, g) { B.drawRocks(ctx, g); const b = g.boss; if (!b) return; if (b.kind === 'moth') B.drawMoth(ctx, g); else if (b.kind === 'wyrm') B.drawWyrm(ctx, g); else if (b.kind === 'jelly') B.drawJelly(ctx, g); else if (b.kind === 'heart') B.drawHeart(ctx, g); else B.drawBeetle(ctx, g); };
  function fan(g, b, n, spd) {
    const p = g.P, a0 = Math.atan2((p.y - 20) - (b.y + 10), p.x - b.x), spread = 0.26;
    for (let i = 0; i < n; i++) { const a = a0 + (i - (n - 1) / 2) * spread; g.spores.push({ kind: 'shard', x: b.x, y: b.y + 14, vx: Math.cos(a) * spd, vy: Math.sin(a) * spd, t: 0 }); }
    G.audio.sfx('spit');
  }
  B.updateMoth = function (g) {
    const b = g.boss, p = g.P, lo = 104, hi = g.room.pw - 104;
    b.t++; b.flash = Math.max(0, b.flash - 1); b.anim += 0.35;
    if (b.state === 'wait') { if (p.x > 150) { b.state = 'intro'; b.t = 0; G.world.sealDoors(g); } }
    else if (b.state === 'intro') { b.x = U.clamp(p.x, lo, hi); b.y = U.lerp(b.y, 70, 0.04); g.shake = Math.max(g.shake, 1.5); if (b.t > 100) { b.state = 'hover'; b.t = 0; b.volleys = 0; } }
    else if (b.state === 'hover') {
      const tx = U.clamp(p.x + Math.sin(b.t * 0.03) * 110, lo, hi);
      b.x += U.clamp((tx - b.x) * 0.03, -2.2, 2.2); b.y = 70 + Math.sin(b.t * 0.06) * 10;
      if (b.t > 90 - b.phase * 8) { b.t = 0; if (b.volleys >= 2) { b.state = 'tele'; b.volleys = 0; } else { b.state = 'shoot'; b.volleys++; } }
    } else if (b.state === 'shoot') { if (b.t === 24) fan(g, b, b.phase === 3 ? 7 : 5, 2.3 + b.phase * 0.2); if (b.t > 46) { b.state = 'hover'; b.t = 0; } }
    else if (b.state === 'tele') {
      b.y = U.lerp(b.y, 40, 0.08); if (b.t < 30) b.tx = U.clamp(p.x, lo, hi); b.x += (b.tx - b.x) * 0.1;
      if (b.t % 10 === 0) G.fx.sparkBurst(b.x, b.y + 20, '#d4f0fa', 4);
      if (b.t > 40) { b.state = 'dive'; b.t = 0; b.vy = 3; G.audio.sfx('missile'); }
    } else if (b.state === 'dive') {
      b.vy = Math.min(8.5, b.vy + 0.35); b.y += b.vy; b.x += (b.tx - b.x) * 0.2;
      if (b.y >= FLOOR_Y) {
        b.y = FLOOR_Y; b.state = 'stun'; b.t = 0; g.shake = 12; G.audio.sfx('boom');
        G.fx.debris(b.x - 20, 236, ['#dff4fc', '#a8d4ee', '#6e9fd0']); G.fx.debris(b.x + 20, 236, ['#dff4fc', '#a8d4ee', '#6e9fd0']);
        if (b.phase >= 2) B.rocks(g, b.phase === 3 ? 6 : 4);
        B.dropItems(g);
      }
    } else if (b.state === 'stun') {
      if (b.phase === 3 && b.t % 80 === 0) B.rocks(g, 2);
      if (b.t > (b.phase === 3 ? 160 : 190)) { b.state = 'rise'; b.t = 0; }
    } else if (b.state === 'rise') { b.y = U.lerp(b.y, 70, 0.07); if (b.t > 40) { b.state = b.phase === 3 && Math.random() < 0.4 ? 'tele' : 'hover'; b.t = 0; } }
    else if (b.state === 'dying') {
      if (b.t % 6 === 0) G.fx.boom(b.x + (Math.random() - 0.5) * 100, b.y + (Math.random() - 0.5) * 80, 9);
      g.shake = 5; if (b.t === 140) B.finish(g, b);
    }
    if (!g.boss) { B.updateRocks(g); return; }
    if (!p.dead && b.state !== 'wait' && !b.dead && Math.abs(p.x - b.x) < (p.w + 56) / 2 && p.y > b.y - 40 && p.y - p.h < b.y + 44) { if (G.player.hurt(g, p, b.state === 'dive' ? 24 : 14, b.x)) G.audio.sfx('hurt'); }
    if (!b.dead) for (const s of g.shots) {
      if (s.dead || Math.abs(s.x - b.x) > 36 || Math.abs(s.y - b.y) > 50) continue;
      const hitCore = B.vulnerable(b) && B.inCore(b, s.x, s.y);
      if (s.kind === 'missile' || s.kind === 'super') { s.dead = true; G.fx.boom(s.x, s.y, 10); if (hitCore) B.damage(g, b, s.dmg); else G.audio.sfx('hit'); }
      else if (hitCore) { B.damage(g, b, s.dmg); if (!s.pierce) s.dead = true; G.fx.sparkBurst(s.x, s.y, '#f2ffff', 5); }
      else if (!s.hit.has(b)) { s.hit.add(b); if (!s.pierce) s.dead = true; G.fx.sparkBurst(s.x, s.y, '#fff', 3); G.audio.sfx('hit'); }
    }
    B.updateRocks(g);
  };
  B.drawMoth = function (ctx, g) {
    const b = g.boss, S = G.sprites.boss2; let c;
    if (b.state === 'shoot') c = S.shoot[(b.t >> 2) & 1]; else if (b.state === 'dive') c = S.dive; else if (b.state === 'stun') c = S.stun[(b.t >> 3) & 1];
    else if (b.state === 'dying') c = S.dead; else c = S.fly[Math.floor(b.anim) & 3];
    const x = Math.round(b.x - 70), y = Math.round(b.y - 50);
    ctx.drawImage(c, x + (b.state === 'dying' ? Math.round((Math.random() - 0.5) * 3) : 0), y);
    if (b.flash > 0) { ctx.globalAlpha = 0.6; ctx.drawImage(G.sprites.whiteOf(c), x, y); ctx.globalAlpha = 1; }
  };
})((window.SGS = window.SGS || {}));
