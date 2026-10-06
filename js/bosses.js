/* Zone 1 boss: the Mossback Warden. Pattern: walk, spore volley, telegraphed charge into the wall, stun (core exposed, only then vulnerable), rocks fall in later phases. */
(function (G) {
  'use strict';
  const U = G.U, B = {};
  G.bosses = B;
  const PAD = 46;
  B.setup = function (g, room) {
    g.rocks = [];
    if (room.id !== 'arena' || g.prog.flags.boss1) return;
    const s = room.spawns.find((q) => q.ch === 'K');
    g.boss = { x: s.x, y: s.y, w: 88, h: 56, hp: 110, hpMax: 110, state: 'wait', t: 0, face: -1, vx: 0, anim: 0, flash: 0, phase: 1, dead: false };
    room.spawns = room.spawns.filter((q) => q.ch !== 'K');
  };
  const core = (b) => ({ x: b.x - b.face * 30, y: b.y - 52 });
  const vulnerable = (b) => b.state === 'stun';
  const inCore = (b, x, y) => { const c = core(b); return Math.abs(x - c.x) < 30 && y > b.y - 76 && y < b.y - 28; };
  B.damage = function (g, b, dmg) {
    if (!vulnerable(b) || b.dead) return false;
    b.hp -= dmg; b.flash = 4; G.audio.sfx('hit');
    if (b.hp <= 65 && b.phase < 2) b.phase = 2;
    if (b.hp <= 30 && b.phase < 3) b.phase = 3;
    if (b.hp <= 0) { b.dead = true; b.state = 'dying'; b.t = 0; G.audio.sfx('boom'); g.shake = 10; }
    return true;
  };
  B.blast = function (g, x, y, r, kind) {
    const b = g.boss; if (!b || b.dead || !vulnerable(b)) return;
    const c = core(b);
    if (U.dist2(x, y, c.x, c.y) < (r + 26) * (r + 26)) B.damage(g, b, kind === 'super' ? 24 : kind === 'bomb2' ? 20 : kind === 'bomb' ? 4 : 8);
  };
  function rocks(g, n) { for (let i = 0; i < n; i++) g.rocks.push({ x: 40 + Math.random() * (g.room.pw - 80), y: 20 - Math.random() * 60, vy: 0, t: 0 }); }
  function volley(g, b) {
    const n = b.phase >= 2 ? 5 : 3;
    for (let i = 0; i < n; i++) g.spores.push({ x: b.x + b.face * 50, y: b.y - 54, vx: b.face * (1 + i * 0.75) + (Math.random() - 0.5) * 0.4, vy: -4.6 - Math.random(), t: 0 });
    G.audio.sfx('spit'); G.fx.puff(b.x + b.face * 50, b.y - 54, 5);
  }
  function dropItems(g) { for (let i = 0; i < 2; i++) g.items.push({ kind: i ? 'missile' : 'en', x: 120 + Math.random() * (g.room.pw - 240), y: 40, vy: 0, t: 0, life: 700 }); }
  function finish(g, b) {
    g.prog.flags.boss1 = true; g.boss = null; G.world.openAll(g);
    g.toast = { txt: 'WARDEN DEFEATED', t: 0 }; G.audio.sfx('save');
    for (let i = 0; i < 3; i++) g.items.push({ kind: i === 1 ? 'missile' : 'en', x: b.x + (i - 1) * 24, y: b.y - 40, vy: -2, t: 0, life: 900 });
  }
  function updateRocks(g) {
    const p = g.P;
    for (const r of g.rocks || []) {
      r.t++; r.vy = Math.min(7, r.vy + 0.25); r.y += r.vy;
      if (!p.dead && Math.abs(p.x - r.x) < p.w / 2 + 6 && r.y > p.y - p.h && r.y - 12 < p.y) { r.dead = true; G.fx.debris(r.x, r.y, ['#52627a', '#7f8c96']); if (G.player.hurt(g, p, 12, r.x)) G.audio.sfx('hurt'); }
      if (G.phys.boxSolid(g.room, r.x - 6, r.y - 12, r.x + 6, r.y)) { r.dead = true; G.fx.debris(r.x, r.y, ['#52627a', '#7f8c96', '#33405e']); G.audio.sfx('break'); }
    }
    if (g.rocks) g.rocks = g.rocks.filter((r) => !r.dead);
  }
  B.updateRocks = updateRocks; B.dropItems = dropItems; B.volley = volley; B.rocks = rocks; B.finish = finish; B.core = core; B.inCore = inCore; B.vulnerable = vulnerable; B.PAD = PAD;
})((window.SGS = window.SGS || {}));
