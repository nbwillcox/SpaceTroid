/* Game state and the per-step simulation: starting / loading, room entry, transitions, entity updates, hazards, camera, death. */
(function (G) {
  'use strict';
  const RM = G.room, PH = G.phys, P = G.player, Game = {};
  G.game = Game;
  const clone = (o) => JSON.parse(JSON.stringify(o));
  Game.abilAll = function () { const a = G.save.fresh().abil; for (const k in a) if (typeof a[k] === 'boolean') a[k] = true; a.beams = { ice: false, wave: false, plasma: false }; return a; };
  /* start (or continue) a game from a save record; rec = null starts a fresh one */
  Game.begin = function (slot, rec, debugAll) {
    rec = rec ? clone(rec) : G.save.fresh();
    Game.slot = slot; Game.baseRec = clone(rec);
    Game.prog = { items: rec.items, doors: rec.doors, flags: rec.flags, visited: rec.visited, mapped: rec.mapped, saves: rec.saves || 0 };
    Game.abil = debugAll ? Game.abilAll() : rec.abil;
    const p = Game.P = P.create(0, 0), h = rec.hero;
    p.tanks = h.tanks; p.missileMax = debugAll ? 20 : h.missileMax; p.missiles = debugAll ? 20 : h.missiles; p.sbombMax = debugAll ? 5 : h.sbombMax; p.sbombs = debugAll ? 5 : h.sbombs; p.superMax = h.superMax; p.supers = h.supers;
    p.en = P.enMax(p); if (Game.abil.suitHeat) p.suit = 'crimson';
    Game.cam = { x: 0, y: 0 }; Game.shake = 0; Game.hitStop = 0; Game.time = 0; Game.playTime = rec.time || 0; Game.saveRec = null; Game.banner = null; Game.toast = null; Game.trans = null; Game.boss = null;
    Game.enterRoom(rec.room, null, rec.x, rec.y);
    Game.fade = { dir: -1, t: 14, len: 14 };
  };
  Game.enterRoom = function (id, doorId, sx, sy) {
    const def = G.rooms[id], room = RM.build(def), p = Game.P;
    Game.room = room; Game.roomId = id; Game.shots = []; Game.bombs = []; Game.foes = []; Game.items = []; Game.spores = []; Game.boss = null; G.fx.reset();
    G.world.setup(Game, room);
    if (doorId) { const dd = Game.doors.find((q) => q.id === doorId); if (dd && !dd.sealed) { dd.state = 'open'; dd.idle = 0; G.world.applyDoor(room, dd); } }
    let start = null;
    for (const s of room.spawns) {
      if (s.ch === 'P') start = s;
      else if (s.ch === 'c') G.enemies.spawn(Game, 'crawler', s.x, s.y, -1);
      else if (s.ch === 'm') G.enemies.spawn(Game, 'moth', s.x, s.y - 8, -1);
      else if (s.ch === 'o') G.enemies.spawn(Game, 'pod', s.x, s.y, -1);
      else if (s.ch === 'f') G.enemies.spawn(Game, 'frostling', s.x, s.y, -1);
      else if (s.ch === 'q') G.enemies.spawn(Game, 'wisp', s.x, s.y - 8, -1);
      else if (s.ch === 't') G.enemies.spawn(Game, 'turret', s.x, s.y, -1);
      else if (s.ch === 'v') G.enemies.spawn(Game, 'icicle', s.x, s.ty * 16 + 22, -1);
    }
    p.vx = p.vy = 0; p.dead = 0; p.inv = 0; p.hurt = 0; p.charge = 0; p.dash = 0; p.spinning = false; p.drop = false;
    const setMode = (m) => { p.mode = m; p.w = m === 'ball' ? 16 : 14; p.h = m === 'ball' ? 15 : 42; };
    setMode('stand');
    if (doorId) {
      const d = def.doors.find((q) => q.id === doorId), h = d.h || 3;
      p.x = d.side === 'L' ? 30 : room.pw - 30; p.y = (d.ty + h) * 16; p.face = d.side === 'L' ? 1 : -1;
      if (h === 1) setMode('ball');
    } else if (sx !== undefined && sx !== null) { p.x = sx; p.y = sy; }
    else if (start) { p.x = start.x; p.y = start.y; } else { p.x = 40; p.y = 40; }
    p.ground = false;
    G.render.bake(room); G.render.camera(Game, true);
    if (G.bosses) G.bosses.setup(Game, room);
  };
  Game.respawn = function () {
    const rec = Game.slot !== null && Game.slot !== undefined && G.save.read(Game.slot) || Game.saveRec || Game.baseRec;
    const dbg = Game.debugAll; Game.begin(Game.slot, rec, false); if (dbg) Game.debugAll = true;
  };
  Game.finishTrans = function () {
    const t = Game.trans; Game.enterRoom(t.to, t.door); t.phase = 'in'; t.t = 0;
  };
  Game.step = function () {
    const p = Game.P, room = Game.room, D = G.input.down;
    if (Game.toast) { Game.toast.t++; if (Game.toast.t > 150) Game.toast = null; }
    if (Game.fade) { Game.fade.t--; if (Game.fade.t <= 0) Game.fade = null; }
    if (Game.banner) { Game.banner.t++; G.fx.update(); if (Game.banner.t > 50 && (D.jump || D.fire || D.start || D.pause)) { Game.banner = null; G.input.clear(); } return; }
    if (Game.trans) {
      const t = Game.trans; t.t++;
      if (t.phase === 'out' && t.t >= 10) Game.finishTrans(); else if (t.phase === 'in' && t.t >= 10) Game.trans = null;
      return;
    }
    if (Game.hitStop > 0) { Game.hitStop--; return; }
    Game.time++; Game.playTime += 1 / 60; Game.shake = Math.max(0, Game.shake - 0.5);
    P.update(Game); G.weapons.update(Game); G.enemies.update(Game); if (G.bosses) G.bosses.update(Game); G.world.update(Game); G.fx.update();
    if (!p.dead && p.inv === 0 && PH.boxTiles(room, p.x - p.w / 2, p.y - 6, p.x + p.w / 2, p.y - 0.01, 8)) { if (P.hurt(Game, p, 14, p.x + (Math.random() - 0.5))) { G.audio.sfx('hurt'); p.vy = -4.5; } }
    G.render.camera(Game, false);
    if (p.dead > 150) Game.respawn();
  };
})((window.SGS = window.SGS || {}));
