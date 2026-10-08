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
    iceBeam: { name: 'ICE BEAM', ramp: 'cobalt', lines: ['Freezes enemies solid for a while.', 'Frozen enemies make stepping stones. Toggle: 1'], apply: (g) => { g.abil.hasIce = true; g.abil.beams.ice = true; } },
    heatSuit: { name: 'HEAT SUIT', ramp: 'crimson', lines: ['Shrugs off extreme heat.', 'Magma will hurt far less.'], apply: (g) => { g.abil.suitHeat = true; g.P.suit = 'crimson'; } },
    spaceJump: { name: 'SPACE JUMP', ramp: 'teal', lines: ['Press Jump again in mid-air to flip higher.', 'Chain it to climb tall shafts.'], apply: (g) => { g.abil.spacejump = true; } },
    dashBoots: { name: 'DASH BOOTS', ramp: 'gold', lines: ['Tap Shift for a burst of speed.', 'Dash into cracked blocks; jump out of a dash to leap far.'], apply: (g) => { g.abil.dash = true; } },
    waveBeam: { name: 'WAVE BEAM', ramp: 'visor', lines: ['Shots ripple through walls and shatter crystal blocks.', 'Toggle: 2'], apply: (g) => { g.abil.hasWave = true; g.abil.beams.wave = true; } },
    aquaSuit: { name: 'AQUA SUIT', ramp: 'cobalt', lines: ['Swim and move freely underwater.', 'Water no longer drags you down.'], apply: (g) => { g.abil.suitAqua = true; g.P.suit = 'teal'; } },
    grapple: { name: 'GRAPPLE BEAM', ramp: 'gold', lines: ['Hold Q near a ceiling anchor to be reeled in.', 'Jump to leap from it.'], apply: (g) => { g.abil.grapple = true; } },
    superMissile: { name: 'SUPER MISSILES', ramp: 'teal', lines: ['Opens green doors; hits much harder.', 'R swaps between missile types.'], apply: (g) => { g.abil.supers = true; g.P.superMax = Math.max(g.P.superMax, 5); g.P.supers = g.P.superMax; } },
    superTank: { name: 'SUPER MISSILE EXPANSION', tank: 'super', lines: ['Super missile capacity +5.'], apply: (g) => { g.P.superMax += 5; g.P.supers = Math.min(g.P.superMax, g.P.supers + 5); } },
    scanVisor: { name: 'SCAN VISOR', ramp: 'teal', lines: ['Press F to switch the scan visor on or off.', 'While it is on, hidden blocks appear and turn solid.'], apply: (g) => { g.abil.scan = true; } },
    plasmaBeam: { name: 'PLASMA BEAM', ramp: 'crimson', lines: ['Burning shots pierce through enemies.', 'Toggle: 3'], apply: (g) => { g.abil.hasPlasma = true; g.abil.beams.plasma = true; } },
    energyTank: { name: 'ENERGY TANK', tank: 'energy', lines: ['Maximum energy +100.'], apply: (g) => { g.P.tanks++; g.P.en = G.player.enMax(g.P); } },
    missileTank: { name: 'MISSILE EXPANSION', tank: 'missile', lines: ['Missile capacity +5.'], apply: (g) => { g.P.missileMax += 5; g.P.missiles = Math.min(g.P.missileMax, g.P.missiles + 5); } },
  };
  W.itemTotal = function () { let n = 0; for (const id in G.rooms) n += (G.rooms[id].items || []).length; return n; };
  /* map cells (30 x 17 tiles each) a room covers */
  W.cells = function (def) { if (def.parent) return []; const cw = Math.ceil(def.map[0].length / 30), ch = Math.ceil(def.map.length / 17), out = []; for (let y = 0; y < ch; y++) for (let x = 0; x < cw; x++) out.push([def.mx + x, def.my + y]); return out; };
  const dkey = (room, d) => room.id + ':' + d.id;
  /* the gold exit door of a boss arena stays locked only until that arena's boss has been beaten (rooms are rebuilt on every visit, so the flag is checked on entry) */
  W.BOSS_FLAG = { arena: 'boss1', arena2: 'boss2', arena3: 'boss3', arena4: 'boss4', heartroom: 'boss5' };
  W.bossBeaten = (g, roomId) => !!(W.BOSS_FLAG[roomId] && g.prog.flags[W.BOSS_FLAG[roomId]]);
  W.setup = function (g, room) {
    const def = room.def;
    g.doors = (def.doors || []).map((d) => {
      const o = Object.assign({ h: 3, state: 'closed', t: 0, idle: 0, tx: d.side === 'L' ? 0 : room.w - 1 }, d);
      if (o.color === 'open') o.state = 'open';
      if (o.color === 'boss' && W.bossBeaten(g, room.id)) o.color = 'blue';
      if (g.prog.doors[dkey(room, d)]) o.unlocked = true;
      W.applyDoor(room, o);
      return o;
    });
    g.pickups = (def.items || []).filter((it) => !g.prog.items[it.id]).map((it) => Object.assign({}, it, { x: it.tx * T + 8, y: it.ty * T + 16 + (it.dy || 0), t: Math.floor(Math.random() * 60) }));
    g.stations = (def.stations || []).map((s) => ({ type: s.type, to: s.to, x: s.tx * T + 8, y: s.ty * T + 16, t: 0 }));
    room.decor = (def.decor || []).map((d) => {
      if (d.kind === 'statue') { const img = G.sprites.statue[d.size][room.zone || 1]; return { img, x: Math.round(d.x - img.width / 2), y: Math.round(d.y - img.height), statue: d.size, cx: d.x, fy: d.y }; }
      return { img: G.sprites.wreck, x: d.x, y: d.y };
    });
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
  W.update = function (g) {
    const p = g.P, room = g.room;
    if (g.doorGrace > 0) g.doorGrace--;
    for (const d of g.doors) {
      const cx = d.tx * T + 8, near = Math.abs(p.x - cx) < 60 && p.y > d.ty * T - 16 && p.y < (d.ty + d.h) * T + 40;
      if (d.state === 'opening') { d.t++; if (d.t >= 12) { d.state = 'open'; d.idle = 0; W.applyDoor(room, d); } }
      else if (d.state === 'open' && d.color !== 'open') {
        d.idle = near ? 0 : d.idle + 1;
        if (d.idle > 140 && Math.abs(p.x - cx) > 26 && !g.boss) { d.state = 'closing'; d.t = 0; W.applyDoor(room, Object.assign({}, d, { state: 'closed' })); }
      } else if (d.state === 'closing') { d.t++; if (d.t >= 10) d.state = 'closed'; }
      if (!g.trans && d.to && d.state === 'open' && !p.dead) {
        const inRows = p.y > d.ty * T + 1 && p.y <= (d.ty + d.h) * T + 2;
        if (d.side === 'I') { if (inRows && !g.doorGrace && Math.abs(p.x - cx) < 7 && p.vx * d.out < 0) g.trans = { t: 0, to: d.to, door: d.door, phase: 'out' }; }   /* a doorway inside the room (item shrines): walk into it */
        else if (inRows && ((d.side === 'L' && p.x < 12 && p.vx <= 0) || (d.side === 'R' && p.x > room.pw - 12 && p.vx >= 0))) g.trans = { t: 0, to: d.to, door: d.door, phase: 'out' };
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
    if (s.type === 'lift') { if (s.to) g.trans = { t: 0, to: s.to, door: null, phase: 'out' }; else G.main.ending(g); return; }
    if (s.type === 'save') { if (!g.saveAnim) g.saveAnim = { t: 0, x: s.x, y: s.y, s, face: p.face }; return; }
    for (const id in G.rooms) if (G.rooms[id].zone === g.room.zone) g.prog.mapped[id] = true;
    g.toast = { txt: 'MAP DATA DOWNLOADED', t: 0 }; G.audio.sfx('save');
  };
  /* save pad sequence: the hero turns to face front, a column of light rises from the pad, the progress is written at its peak, then the light fades and play resumes */
  W.saveDo = function (g, s) {
    const p = g.P;
    p.en = G.player.enMax(p); p.missiles = p.missileMax; p.sbombs = p.sbombMax; p.supers = p.superMax;
    const rec = G.save.snapshot(g, { x: s.x, y: s.y }); g.prog.saves = rec.saves; g.saveRec = rec;
    if (g.slot !== null && g.slot !== undefined) G.save.write(g.slot, rec);
    g.toast = { txt: 'PROGRESS SAVED', t: 0 }; G.audio.sfx('save'); G.fx.ring(s.x, s.y - 10); G.fx.ring(s.x, s.y - 30);
  };
  W.saveAnimStep = function (g) {
    const a = g.saveAnim, p = g.P; a.t++;
    p.x += (a.x - p.x) * 0.3; p.vx = 0; p.vy = 0; p.dash = 0;
    if (a.t === 1) G.audio.sfx('chargeStart');
    if (a.t === 40) W.saveDo(g, a.s);
    if (a.t >= 84) g.saveAnim = null;
  };
  /* picking up an item: the world holds still, the hero raises an arm, a fanfare plays and the item floats up in a burst of light; then the text panel opens */
  W.collect = function (g, it) {
    const def = W.ITEMS[it.type]; g.prog.items[it.id] = true; def.apply(g);
    g.getAnim = { t: 0, it: { type: it.type, x: it.x, y: it.y }, def, big: !def.tank };
    if (G.music && G.music.fanfare) G.music.fanfare(!def.tank); else G.audio.sfx('pickup');
    G.fx.boom(it.x, it.y - 8, def.tank ? 8 : 14);
  };
  W.getAnimStep = function (g) {
    const a = g.getAnim, p = g.P; a.t++;
    p.vx = 0; p.vy = 0; p.dash = 0; p.aim = 'up'; p.aimAng = null; p.charge = 0;
    if (a.t % 5 === 0 && a.t < (a.big ? 130 : 56)) { const m = G.player.muzzle(p); G.fx.spark(m.x + (Math.random() - 0.5) * 10, m.y - 6 - Math.random() * 14, a.big ? '#fff2a8' : '#cfeeff'); }
    if (a.t >= (a.big ? 168 : 78)) { g.getAnim = null; g.banner = { name: a.def.name, lines: a.def.lines, t: 0, type: a.it.type }; }
  };
  /* stepped glow disc behind an item (rows of 1px, so it stays pixel-art) */
  W.glow = function (ctx, x, y, r, col, a) { ctx.fillStyle = 'rgba(' + col + ',' + a + ')'; for (let dy = -r; dy <= r; dy++) { const dx = Math.floor(Math.sqrt(r * r - dy * dy)); ctx.fillRect(x - dx, y + dy, dx * 2 + 1, 1); } };
  /* an item as it lies in a shrine: abilities are the object itself in a pulsing aura, expansions are tanks (energy E-tank, missile, super) */
  W.drawItem = function (ctx, type, x, y, t, bob) {
    const S = G.sprites, def = W.ITEMS[type], pulse = 0.5 + 0.5 * Math.sin(t * 0.09);
    if (def.tank) {
      W.glow(ctx, x, y - 12 + bob, 13, '200,240,255', (0.05 + pulse * 0.05).toFixed(3));
      ctx.drawImage(S.tank[def.tank][(t >> 4) & 1], x - 10, y - 22 + bob);
    } else {
      const col = def.glow || '255,244,190';
      W.glow(ctx, x, y - 13 + bob, 17, col, (0.05 + pulse * 0.05).toFixed(3)); W.glow(ctx, x, y - 13 + bob, 12, col, (0.08 + pulse * 0.08).toFixed(3));
      ctx.drawImage(S.icon[type], x - 10, y - 23 + bob);
      if ((t >> 2) % 7 === 0) { ctx.fillStyle = '#fff'; ctx.fillRect(x + 8, y - 24 + bob, 1, 1); ctx.fillRect(x - 9, y - 6 + bob, 1, 1); }
    }
  };
  W.drawBack = function (ctx, g, time) {
    for (const d of g.doors) {                                              /* doorways inside the room (they lead to item shrines): a dark arch with pulsing runes */
      if (d.side !== 'I') continue;
      const x = d.tx * T, y = d.ty * T, h = d.h * T, pulse = 0.5 + 0.5 * Math.sin(time * 3 + d.tx);
      if (d.h === 1) { ctx.fillStyle = 'rgba(6,8,24,0.8)'; ctx.fillRect(x + 1, y + 1, 14, 15); ctx.fillStyle = 'rgba(134,240,242,' + (0.35 + pulse * 0.4).toFixed(2) + ')'; ctx.fillRect(x, y, 16, 1); ctx.fillRect(x, y, 1, 16); ctx.fillRect(x + 15, y, 1, 16); continue; }
      ctx.fillStyle = 'rgba(6,8,24,0.85)'; ctx.fillRect(x + 1, y + 2, 14, h - 2);
      ctx.fillStyle = '#6a7ca8'; ctx.fillRect(x - 3, y - 2, 22, 4); ctx.fillRect(x - 1, y, 3, h); ctx.fillRect(x + 14, y, 3, h);
      ctx.fillStyle = '#a8bce0'; ctx.fillRect(x - 3, y - 2, 22, 1); ctx.fillRect(x - 1, y, 1, h);
      ctx.fillStyle = '#3a4a78'; ctx.fillRect(x + 16, y, 1, h); ctx.fillRect(x - 3, y + 1, 22, 1);
      ctx.fillStyle = 'rgba(134,240,242,' + (0.45 + pulse * 0.5).toFixed(2) + ')'; ctx.fillRect(x + 2, y - 1, 2, 2); ctx.fillRect(x + 7, y - 1, 2, 2); ctx.fillRect(x + 12, y - 1, 2, 2);
      for (let k = 1; k < d.h; k++) { ctx.fillRect(x - 1, y + k * 16 - 4, 1, 3); ctx.fillRect(x + 16, y + k * 16 - 4, 1, 3); }
    }
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
    for (const it of g.pickups) W.drawItem(ctx, it.type, Math.round(it.x), Math.round(it.y), it.t, Math.round(Math.sin(it.t * 0.08) * 2));
    if (g.near && !g.saveAnim) G.px.text(ctx, { save: 'UP: SAVE', map: 'UP: MAP', lift: 'UP: DESCEND' }[g.near.type], Math.round(g.near.x), Math.round(g.near.y - 62), { s: 1, c: '#f2ffff', o: '#0a0e2c', a: 'c' });
  };
})((window.SGS = window.SGS || {}));
