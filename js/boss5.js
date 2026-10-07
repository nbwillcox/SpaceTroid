/* Final boss: the Hive Core. Phase 1: four shield nodes fire spore orbs; destroy them all. Phase 2: the heart opens (only then vulnerable) and sends shockwaves along the floor. Phase 3: faster, with ceiling tendril strikes and hatching drones. Its death starts the escape. */
(function (G) {
  'use strict';
  const U = G.U, B = G.bosses;
  const FLOOR = 240;
  function orb(g, from, p, spd) { const a = Math.atan2((p.y - 24) - from.y, p.x - from.x); g.spores.push({ kind: 'shard', x: from.x, y: from.y, vx: Math.cos(a) * spd, vy: Math.sin(a) * spd, t: 0 }); }
  B.setupHeart = function (g, room) {
    const s = room.spawns.find((q) => q.ch === 'K'), cx = s.x;
    g.boss = { kind: 'heart', flag: 'boss5', name: 'HIVE CORE', x: cx, y: 96, w: 110, h: 110, hp: 150, hpMax: 150, state: 'wait', t: 0, face: 1, anim: 0, flash: 0, phase: 1, dead: false, open: false,
      nodes: [[-170, 40], [170, 40], [-110, -34], [110, -34]].map(([dx, dy]) => ({ x: cx + dx, y: 100 + dy + 30, hp: 14, alive: true, flash: 0, t: Math.floor(Math.random() * 60) })) };
    g.waves = []; g.strikes = [];
  };
  B.updateHeart = function (g) {
    const b = g.boss, p = g.P; b.t++; b.flash = Math.max(0, b.flash - 1); b.anim += 0.08;
    if (b.state === 'wait') { if (p.x > 150) { b.state = 'fight'; b.t = 0; G.world.sealDoors(g); g.shake = 6; G.audio.sfx('boom'); } }
    else if (b.state === 'fight') {
      if (b.phase === 1) {
        for (const n of b.nodes) { if (!n.alive) continue; n.t++; n.flash = Math.max(0, n.flash - 1); if (n.t % 110 === 70) { orb(g, n, p, 1.9); G.audio.sfx('spit'); } }
        if (b.nodes.every((n) => !n.alive)) { b.phase = 2; b.t = 0; b.open = false; g.shake = 10; G.audio.sfx('boom'); G.fx.boom(b.x, b.y, 18); }
      } else {
        const cyc = b.t % (b.phase === 3 ? 150 : 200); b.open = cyc > 40 && cyc < (b.phase === 3 ? 130 : 170);
        if (b.t % (b.phase === 3 ? 90 : 130) === 60) { const sp = b.phase === 3 ? 2.8 : 2.2; g.waves.push({ x: b.x - 20, y: FLOOR, vx: -sp }, { x: b.x + 20, y: FLOOR, vx: sp }); G.audio.sfx('boom'); G.fx.debris(b.x, FLOOR - 4, ['#b05c90', '#80386a']); }
        if (b.open && b.t % 40 === 20) orb(g, { x: b.x, y: b.y + 30 }, p, 2 + b.phase * 0.2);
        if (b.phase === 3) {
          if (b.t % 120 === 40) g.strikes.push({ x: p.x, t: 0 });
          if (b.t % 300 === 150) { const h = G.enemies.spawn(g, 'hmoth', b.x + (Math.random() < 0.5 ? -120 : 120), 120, -1); G.fx.sparkBurst(h.x, h.y, '#f4ffc0', 8); }
        }
      }
    } else if (b.state === 'dying') {
      if (b.t % 5 === 0) G.fx.boom(b.x + (Math.random() - 0.5) * 120, b.y + (Math.random() - 0.5) * 100, 10);
      g.shake = 7; if (b.t === 160) B.finish(g, b);
    }
    if (!g.boss) return;
    for (const w of g.waves) { w.x += w.vx; if (Math.abs(p.x - w.x) < p.w / 2 + 8 && p.y > w.y - 12 && p.y - p.h < w.y && !p.dead) { if (G.player.hurt(g, p, 14, w.x)) G.audio.sfx('hurt'); } if (G.phys.boxSolid(g.room, w.x - 2, w.y - 4, w.x + 2, w.y - 1)) w.dead = true; }
    g.waves = g.waves.filter((w) => !w.dead);
    for (const s of g.strikes) { s.t++; if (s.t === 40) { G.audio.sfx('boom'); g.shake = Math.max(g.shake, 5); } if (s.t >= 40 && s.t < 56 && !p.dead && Math.abs(p.x - s.x) < p.w / 2 + 9) { if (G.player.hurt(g, p, 20, s.x)) G.audio.sfx('hurt'); } }
    g.strikes = g.strikes.filter((s) => s.t < 60);
    if (!p.dead && b.state === 'fight' && Math.abs(p.x - b.x) < (p.w + 90) / 2 && p.y > b.y - 50 && p.y - p.h < b.y + 50) { if (G.player.hurt(g, p, 16, b.x)) G.audio.sfx('hurt'); }
    for (const s of g.shots) {
      if (s.dead) continue;
      if (b.phase === 1) { for (const n of b.nodes) if (n.alive && Math.abs(s.x - n.x) < 20 && Math.abs(s.y - n.y) < 20) { const dmg = s.dmg; n.hp -= dmg; n.flash = 4; s.dead = !s.pierce || s.kind === 'missile'; G.fx.sparkBurst(s.x, s.y, '#f4ffc0', 4); G.audio.sfx('hit'); if (s.kind === 'missile' || s.kind === 'super') G.fx.boom(s.x, s.y, 10); if (n.hp <= 0) { n.alive = false; G.fx.boom(n.x, n.y, 14); G.audio.sfx('die'); g.shake = 6; } break; } }
      else if (Math.abs(s.x - b.x) < 58 && Math.abs(s.y - b.y) < 58) {
        if (b.open) { B.damage(g, b, s.dmg); if (!s.pierce || s.kind === 'missile') s.dead = true; if (s.kind === 'missile' || s.kind === 'super') G.fx.boom(s.x, s.y, 10); G.fx.sparkBurst(s.x, s.y, '#f4ffc0', 5); }
        else { s.dead = true; G.fx.sparkBurst(s.x, s.y, '#fff', 3); }
      }
    }
  };
  B.drawHeart = function (ctx, g) {
    const b = g.boss, S = G.sprites.heart, t = b.anim, pulse = 1 + Math.round(Math.sin(t * 2.2) * 1.5);
    for (const n of b.nodes) { if (!n.alive) continue; ctx.drawImage(S.node[n.flash > 0 ? 1 : 0], Math.round(n.x) - S.node[0].ax, Math.round(n.y) - S.node[0].ay); ctx.strokeStyle = 'rgba(244,255,192,0.5)'; ctx.lineWidth = 1; ctx.beginPath(); ctx.moveTo(Math.round(n.x), Math.round(n.y)); ctx.lineTo(Math.round(b.x), Math.round(b.y)); ctx.stroke(); }
    const fr = S.body[b.open ? ((Math.floor(t * 3) & 1) ? 2 : 1) : 0], x = Math.round(b.x) - fr.ax, y = Math.round(b.y) - fr.ay + (pulse > 1 ? 1 : 0);
    ctx.drawImage(fr, x, y);
    if (b.flash > 0) { ctx.globalAlpha = 0.6; ctx.drawImage(G.sprites.whiteOf(fr), x, y); ctx.globalAlpha = 1; }
    for (const w of g.waves || []) { const wx = Math.round(w.x), wy = Math.round(w.y); ctx.fillStyle = '#ff80c8'; ctx.fillRect(wx - 7, wy - 9, 14, 9); ctx.fillStyle = '#ffd0f0'; ctx.fillRect(wx - 5, wy - 7, 10, 2); ctx.fillStyle = '#a860ff'; ctx.fillRect(wx - 9, wy - 3, 18, 3); }
    for (const st of g.strikes || []) { const x0 = Math.round(st.x); if (st.t < 40) { ctx.fillStyle = st.t % 6 < 3 ? 'rgba(255,128,200,0.55)' : 'rgba(255,208,240,0.35)'; ctx.fillRect(x0 - 1, 0, 2, 240); } else if (st.t < 56) { ctx.fillStyle = '#ffd0f0'; ctx.fillRect(x0 - 8, 0, 16, 240); ctx.fillStyle = '#ff80c8'; ctx.fillRect(x0 - 5, 0, 10, 240); ctx.fillStyle = '#fff'; ctx.fillRect(x0 - 2, 0, 4, 240); } }
  };
})((window.SGS = window.SGS || {}));
