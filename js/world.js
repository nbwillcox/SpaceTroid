/* World logic: doors (blue / red / green / boss), room transitions, item pickups, save pads and map terminals, plus map-cell helpers. */
(function (G) {
  'use strict';
  const RM = G.room, T = 16, W = {};
  G.world = W;
  W.ITEMS = {
    morph: { name: 'MORPH BALL', ramp: 'teal', lines: ['Curl into a ball to roll through tunnels.', 'Crouch, then press Down again.'], apply: (g) => { g.abil.morph = true; } },
    missile: { name: 'MISSILES', ramp: 'crimson', lines: ['Opens red doors and breaks missile blocks.', 'Right click or C to fire.'], apply: (g) => { g.abil.missiles = true; g.P.missileMax = Math.max(g.P.missileMax, 5); g.P.missiles = g.P.missileMax; } },
    bombs: { name: 'BOMBS', ramp: 'gold', lines: ['In ball form, Fire lays a bomb.', 'Bombs break bomb blocks and bounce you up.'], apply: (g) => { g.abil.bombs = true; } },
    charge: { name: 'CHARGE BEAM', ramp: 'cobalt', lines: ['Hold Fire to charge a heavy shot.', 'Release at full charge.'], apply: (g) => { g.abil.charge = true; } },
    energyTank: { name: 'ENERGY TANK', tank: 'energy', lines: ['Maximum energy +100.'], apply: (g) => { g.P.tanks++; g.P.en = G.player.enMax(g.P); } },
    missileTank: { name: 'MISSILE EXPANSION', tank: 'missile', lines: ['Missile capacity +5.'], apply: (g) => { g.P.missileMax += 5; g.P.missiles = Math.min(g.P.missileMax, g.P.missiles + 5); } },
  };
  W.itemTotal = function () { let n = 0; for (const id in G.rooms) n += (G.rooms[id].items || []).length; return n; };
  /* map cells (30 x 17 tiles each) a room covers */
  W.cells = function (def) { const cw = Math.ceil(def.map[0].length / 30), ch = Math.ceil(def.map.length / 17), out = []; for (let y = 0; y < ch; y++) for (let x = 0; x < cw; x++) out.push([def.mx + x, def.my + y]); return out; };
  const dkey = (room, d) => room.id + ':' + d.id;
  W.setup = function (g, room) {
    const def = room.def;
    g.doors = (def.doors || []).map((d) => {
      const o = Object.assign({ h: 3, state: 'closed', t: 0, idle: 0, tx: d.side === 'L' ? 0 : room.w - 1 }, d);
      if (o.color === 'open') o.state = 'open';
      if (g.prog.doors[dkey(room, d)]) o.unlocked = true;
      W.applyDoor(room, o);
      return o;
    });
    g.pickups = (def.items || []).filter((it) => !g.prog.items[it.id]).map((it) => Object.assign({}, it, { x: it.tx * T + 8, y: it.ty * T + 16, t: Math.floor(Math.random() * 60) }));
    g.stations = (def.stations || []).map((s) => ({ type: s.type, x: s.tx * T + 8, y: s.ty * T + 16, t: 0 }));
    room.decor = (def.decor || []).map((d) => ({ img: G.sprites.wreck, x: d.x, y: d.y }));
    g.prog.visited[room.id] = true;
  };
  W.applyDoor = function (room, d) { const k = d.state === 'open' ? 0 : 9; for (let i = 0; i < d.h; i++) RM.set(room, d.tx, d.ty + i, k); };
  const canOpen = (g, d, kind) => d.unlocked || d.color === 'blue' || (d.color === 'red' && (kind === 'missile' || kind === 'super')) || (d.color === 'green' && kind === 'super');
  W.shotDoor = function (g, tx, ty, kind) {
    const d = g.doors.find((q) => q.tx === tx && ty >= q.ty && ty < q.ty + q.h);
    if (!d || d.state !== 'closed' || d.color === 'open' || d.sealed) return;
    if (d.color === 'boss' || !canOpen(g, d, kind)) { G.fx.sparkBurst(tx * T + 8, ty * T + 8, '#fff', 3); G.audio.sfx('hit'); return; }
    d.state = 'opening'; d.t = 0; G.audio.sfx('door');
    if (d.color !== 'blue' && !d.unlocked) { d.unlocked = true; g.prog.doors[dkey(g.room, d)] = true; }
  };
  /* boss fight: lock every door, then free them */
  W.sealDoors = function (g) { for (const d of g.doors) { d.sealed = true; if (d.state !== 'closed') { d.state = 'closed'; W.applyDoor(g.room, d); } } };
  W.openAll = function (g) { for (const d of g.doors) { d.sealed = false; if (d.color === 'boss') d.color = 'blue'; if (d.state === 'closed') { d.state = 'opening'; d.t = 0; } } };
  W.bossOpen = function (g) { for (const d of g.doors) if (d.color === 'boss' && g.prog.flags.boss1) { d.color = 'blue'; } };
  W.update = function (g) {
    const p = g.P, room = g.room;
    for (const d of g.doors) {
      const cx = d.tx * T + 8, near = Math.abs(p.x - cx) < 60 && p.y > d.ty * T - 16 && p.y < (d.ty + d.h) * T + 40;
      if (d.state === 'opening') { d.t++; if (d.t >= 12) { d.state = 'open'; d.idle = 0; W.applyDoor(room, d); } }
      else if (d.state === 'open' && d.color !== 'open') {
        d.idle = near ? 0 : d.idle + 1;
        if (d.idle > 140 && Math.abs(p.x - cx) > 26 && !g.boss) { d.state = 'closing'; d.t = 0; W.applyDoor(room, Object.assign({}, d, { state: 'closed' })); }
      } else if (d.state === 'closing') { d.t++; if (d.t >= 10) d.state = 'closed'; }
      if (!g.trans && d.to && d.state === 'open' && !p.dead) {
        const inRows = p.y > d.ty * T + 1 && p.y <= (d.ty + d.h) * T + 2;
        if (inRows && ((d.side === 'L' && p.x < 12 && p.vx <= 0) || (d.side === 'R' && p.x > room.pw - 12 && p.vx >= 0))) g.trans = { t: 0, to: d.to, door: d.door, phase: 'out' };
      }
    }
    for (const it of g.pickups) {
      it.t++;
      if (!p.dead && Math.abs(p.x - it.x) < p.w / 2 + 8 && p.y > it.y - 24 && p.y - p.h < it.y) { it.got = true; W.collect(g, it); }
    }
    g.pickups = g.pickups.filter((i) => !i.got);
    g.near = null;
    for (const s of g.stations) {
      s.t++;
      const near = Math.abs(p.x - s.x) < 14 && Math.abs(p.y - s.y) < 4 && p.ground && p.mode === 'stand';
      if (near) { g.near = s; if (G.input.down.u && !g.banner) W.useStation(g, s); }
    }
  };
  W.useStation = function (g, s) {
    const p = g.P;
    if (s.type === 'lift') { G.main.ending(g); return; }
    if (s.type === 'save') {
      p.en = G.player.enMax(p); p.missiles = p.missileMax; p.sbombs = p.sbombMax; p.supers = p.superMax;
      const rec = G.save.snapshot(g, { x: s.x, y: s.y }); g.prog.saves = rec.saves; g.saveRec = rec;
      if (g.slot !== null && g.slot !== undefined) G.save.write(g.slot, rec);
      g.toast = { txt: 'PROGRESS SAVED', t: 0 }; G.audio.sfx('save'); G.fx.ring(s.x, s.y - 10);
    } else {
      for (const id in G.rooms) if (G.rooms[id].zone === g.room.zone) g.prog.mapped[id] = true;
      g.toast = { txt: 'MAP DATA DOWNLOADED', t: 0 }; G.audio.sfx('save');
    }
  };
  W.collect = function (g, it) {
    const def = W.ITEMS[it.type]; g.prog.items[it.id] = true; def.apply(g); G.audio.sfx('pickup');
    g.banner = { name: def.name, lines: def.lines, t: 0 }; G.fx.boom(it.x, it.y - 8, 10);
  };
  W.drawBack = function (ctx, g, time) {
    for (const s of g.stations) { const img = s.type === 'map' ? G.sprites.term[Math.floor(time * 2) & 1] : G.sprites.pad[Math.floor(time * 3) & 1]; ctx.drawImage(img, Math.round(s.x - img.width / 2), Math.round(s.y - img.height)); }
  };
  W.drawFront = function (ctx, g, time) {
    const S = G.sprites;
    for (const d of g.doors) {
      if (d.color === 'open') continue;
      const set = S.door[d.unlocked && d.color !== 'blue' && d.color !== 'boss' ? 'blue' : d.color] || S.door.blue;
      let f = 0;
      if (d.state === 'opening') f = Math.min(4, Math.floor(d.t / 3)); else if (d.state === 'open') f = 4; else if (d.state === 'closing') f = Math.max(0, 4 - Math.floor(d.t / 2.5));
      ctx.drawImage(set[f], d.tx * T, d.ty * T + (d.h - 3) * T);
    }
    for (const it of g.pickups) {
      const def = W.ITEMS[it.type], bob = Math.round(Math.sin(it.t * 0.08) * 2), x = Math.round(it.x), y = Math.round(it.y);
      if (def.tank) ctx.drawImage(S.tank[def.tank][(it.t >> 4) & 1], x - 7, y - 16 + bob);
      else { ctx.fillStyle = 'rgba(255,255,255,0.12)'; ctx.fillRect(x - 11, y - 24 + bob, 22, 22); ctx.drawImage(S.orb[def.ramp][(it.t >> 3) % 3], x - 8, y - 22 + bob); if ((it.t >> 2) % 6 === 0) { ctx.fillStyle = '#fff'; ctx.fillRect(x + 8, y - 24 + bob, 1, 1); } }
    }
    if (g.near) G.px.text(ctx, { save: 'UP: SAVE', map: 'UP: MAP', lift: 'UP: DESCEND' }[g.near.type], Math.round(g.near.x), Math.round(g.near.y - 62), { s: 1, c: '#f2ffff', o: '#0a0e2c', a: 'c' });
  };
})((window.SGS = window.SGS || {}));
