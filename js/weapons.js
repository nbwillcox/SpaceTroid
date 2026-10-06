/* Beam shots (base / ice / wave / plasma, chargeable), missiles, super missiles, morph-ball bombs, and what they do to blocks and enemies. */
(function (G) {
  'use strict';
  const RM = G.room, PH = G.phys, P = G.player, U = G.U, T = 16;
  const W = {};
  G.weapons = W;
  W.beam = function (A) {
    const b = A.beams || {}, col = b.plasma ? ['#ff7a2a', '#fff6a0'] : b.wave ? ['#b878ff', '#f2e0ff'] : b.ice ? ['#7ad8ff', '#ffffff'] : ['#ffd24a', '#fff6a0'];
    return { dmg: 1 + (b.wave ? 1 : 0) + (b.plasma ? 2 : 0), ice: !!b.ice, wave: !!b.wave, pierce: !!b.plasma, col };
  };
  function shoot(g, p, charged) {
    const m = P.muzzle(p), v = P.aimVec(p), B = W.beam(g.abil), sp = charged ? 7 : 6;
    g.shots.push({ kind: 'beam', x: m.x, y: m.y, vx: v.x * sp, vy: v.y * sp, life: charged ? 46 : 36, dmg: B.dmg * (charged ? 4 : 1), r: charged ? 5 : 2, ice: B.ice, wave: B.wave, pierce: B.pierce || charged, col: B.col, big: charged, t: 0, hit: new Set() });
    G.fx.flash(m.x, m.y, B.col[1], charged ? 6 : 3);
    G.audio.sfx(charged ? 'charged' : 'shot');
  }
  function missile(g, p) {
    const sup = p.sel === 1 && g.abil.supers && p.supers > 0;
    if (sup) p.supers--; else if (p.missiles > 0 && g.abil.missiles) p.missiles--; else return;
    const m = P.muzzle(p), v = P.aimVec(p);
    g.shots.push({ kind: sup ? 'super' : 'missile', x: m.x, y: m.y, vx: v.x * 2, vy: v.y * 2, dx: v.x, dy: v.y, spd: 2, life: 120, dmg: sup ? 24 : 8, r: 3, t: 0, hit: new Set() });
    p.fireCd = 10; G.audio.sfx(sup ? 'super' : 'missile');
  }
  function bomb(g, p) {
    if (g.bombs.length >= 3) return;
    g.bombs.push({ x: p.x, y: p.y - 7, t: 0, fuse: 48 }); p.bombCd = 12; G.audio.sfx('bomb');
  }
  W.playerFire = function (g, p, I, D) {
    const A = g.abil;
    if (p.hurt > 0 || p.dead) { p.charge = 0; p.held = 0; return; }
    if (p.mode === 'ball') { if (D.fire && A.bombs && p.bombCd === 0) bomb(g, p); p.charge = 0; return; }
    if (D.fire && p.fireCd === 0) { shoot(g, p, false); p.fireCd = 8; p.held = 0; }
    if (I.fire) { p.held++; if (A.charge && p.held > 14) { p.charge = Math.min(60, p.held - 14); if (p.charge === 1) G.audio.sfx('chargeStart'); } }
    else { if (p.charge >= 50 && A.charge) { shoot(g, p, true); p.fireCd = 14; } p.charge = 0; p.held = 0; }
    if (D.missile && p.fireCd === 0 && p.mode !== 'ball') missile(g, p);
    if (D.swap && A.supers) p.sel = 1 - p.sel;
    if (D.b1) A.beams.ice = !A.beams.ice && A.hasIce; if (D.b2) A.beams.wave = !A.beams.wave && A.hasWave; if (D.b3) A.beams.plasma = !A.beams.plasma && A.hasPlasma;
  };
  W.breakAt = function (g, tx, ty, kind) {
    const k = RM.at(g.room, tx, ty);
    const ok = k === 5 || (k === 6 && (kind === 'bomb')) || (k === 7 && (kind === 'missile' || kind === 'super' || kind === 'bomb2'));
    if (!ok) return false;
    RM.set(g.room, tx, ty, 0); G.fx.debris(tx * T + 8, ty * T + 8, k === 5 ? ['#8a5a40', '#b88454', '#5c3a34'] : ['#52627a', '#7f8c96', '#33405e']); G.audio.sfx('break');
    return true;
  };
  function explode(g, x, y, r, dmg, kind) {
    G.fx.boom(x, y, r);
    for (let ty = Math.floor((y - r) / T); ty <= Math.floor((y + r) / T); ty++) for (let tx = Math.floor((x - r) / T); tx <= Math.floor((x + r) / T); tx++) if (U.dist2(tx * T + 8, ty * T + 8, x, y) <= (r + 6) * (r + 6)) W.breakAt(g, tx, ty, kind);
    for (const f of g.foes) if (!f.dead && U.dist2(f.x, f.y - f.h / 2, x, y) <= (r + f.w / 2) * (r + f.w / 2)) G.enemies.damage(g, f, dmg, kind);
    g.shake = Math.max(g.shake, r > 20 ? 3 : 1.5);
  }
  W.update = function (g) {
    const room = g.room, p = g.P;
    for (const s of g.shots) {
      s.t++;
      if (s.kind === 'missile' || s.kind === 'super') { s.spd = Math.min(s.kind === 'super' ? 5 : 5.5, s.spd + 0.18); s.vx = s.dx * s.spd; s.vy = s.dy * s.spd; if (s.t % 2 === 0) G.fx.spark(s.x - s.dx * 3, s.y - s.dy * 3, '#ffd2a0'); }
      if (s.wave) s.y += Math.sin(s.t * 0.7) * 1.4;
      s.x += s.vx; s.y += s.vy; s.life--;
      const tx = Math.floor(s.x / T), ty = Math.floor(s.y / T), k = RM.at(room, tx, ty);
      if (RM.isSolid(k) || ((k === 3 || k === 4) && s.y >= RM.surface(k, ty, Math.floor(s.x) - tx * T))) {
        const brk = W.breakAt(g, tx, ty, s.kind === 'beam' ? 'shot' : s.kind);
        if (k === 5 && s.kind === 'beam') { s.dead = true; G.fx.spark(s.x, s.y, '#fff'); }
        else if (s.wave && s.kind === 'beam') { /* wave passes walls */ }
        else { s.dead = true; if (s.kind === 'missile' || s.kind === 'super') explode(g, s.x - s.vx * 0.5, s.y - s.vy * 0.5, s.kind === 'super' ? 30 : 18, s.dmg * 0.4, s.kind); else G.fx.sparkBurst(s.x, s.y, s.col ? s.col[1] : '#fff', 4); }
        if (brk && s.kind === 'beam') s.dead = true;
      }
      if (s.life <= 0) s.dead = true;
      if (s.dead) continue;
      for (const f of g.foes) {
        if (f.dead || s.hit.has(f) || f.ghost) continue;
        if (Math.abs(s.x - f.x) < f.w / 2 + s.r && s.y > f.y - f.h - s.r && s.y < f.y + s.r) {
          s.hit.add(f); G.enemies.damage(g, f, s.dmg, s.kind, s);
          if (s.kind === 'missile' || s.kind === 'super') { s.dead = true; explode(g, s.x, s.y, s.kind === 'super' ? 30 : 18, 0, s.kind); }
          else if (!s.pierce) { s.dead = true; G.fx.sparkBurst(s.x, s.y, s.col[1], 5); }
          break;
        }
      }
    }
    g.shots = g.shots.filter((s) => !s.dead);
    for (const b of g.bombs) {
      b.t++;
      if (b.t >= b.fuse) {
        b.dead = true; explode(g, b.x, b.y, 26, 6, 'bomb');
        const dx = p.x - b.x, dy = (p.y - p.h / 2) - b.y;
        if (p.mode === 'ball' && dx * dx + dy * dy < 30 * 30) { p.vy = -4.6; p.vx += Math.sign(dx || 1) * 1.3; p.ground = false; }
        G.audio.sfx('boom');
      }
    }
    g.bombs = g.bombs.filter((b) => !b.dead);
  };
})((window.SGS = window.SGS || {}));
