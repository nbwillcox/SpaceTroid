/* Game state and the per-step simulation: room loading, entity updates, hazards, camera. */
(function (G) {
  'use strict';
  const RM = G.room, PH = G.phys, P = G.player, Game = {};
  G.game = Game;
  Game.abilAll = function () { return { morph: true, bombs: true, missiles: true, supers: true, spacejump: true, dash: true, charge: false, beams: { ice: false, wave: false, plasma: false }, hasIce: true, hasWave: true, hasPlasma: true }; };
  Game.new = function (abil) {
    Game.abil = abil || Game.abilAll();
    Game.P = P.create(0, 0); Game.cam = { x: 0, y: 0 }; Game.shake = 0; Game.hitStop = 0; Game.time = 0;
    Game.P.tanks = 2; Game.P.en = P.enMax(Game.P); Game.P.superMax = 5; Game.P.supers = 3; Game.P.missileMax = 20; Game.P.missiles = 10; Game.P.bombMax = 10; Game.P.bombs = 6;
  };
  Game.load = function (id, sx, sy) {
    const def = G.rooms[id], room = RM.build(def), p = Game.P;
    Game.room = room; Game.shots = []; Game.bombs = []; Game.foes = []; Game.items = []; Game.spores = []; G.fx.reset();
    let start = null;
    for (const s of room.spawns) {
      if (s.ch === 'P') start = s;
      else if (s.ch === 'c') G.enemies.spawn(Game, 'crawler', s.x, s.y, -1);
      else if (s.ch === 'm') G.enemies.spawn(Game, 'moth', s.x, s.y - 8, -1);
      else if (s.ch === 'o') G.enemies.spawn(Game, 'pod', s.x, s.y, -1);
    }
    p.x = sx !== undefined ? sx : start ? start.x : 40; p.y = sy !== undefined ? sy : start ? start.y : 40;
    p.vx = p.vy = 0; p.dead = 0; p.inv = 0; p.hurt = 0; p.mode = 'stand'; p.w = 14; p.h = 42; p.ground = false; p.charge = 0;
    Game.roomId = id; Game.startPos = { x: p.x, y: p.y };
    G.render.bake(room); G.render.camera(Game, true);
  };
  Game.respawn = function () { const p = Game.P; p.en = P.enMax(p); p.missiles = p.missileMax; p.bombs = p.bombMax; Game.load(Game.roomId, Game.startPos.x, Game.startPos.y); };
  Game.step = function () {
    if (Game.hitStop > 0) { Game.hitStop--; return; }
    const p = Game.P, room = Game.room;
    Game.time++; Game.shake = Math.max(0, Game.shake - 0.5);
    P.update(Game); G.weapons.update(Game); G.enemies.update(Game); G.fx.update();
    if (!p.dead && p.inv === 0 && PH.boxTiles(room, p.x - p.w / 2, p.y - 6, p.x + p.w / 2, p.y - 0.01, 8)) { if (P.hurt(Game, p, 14, p.x + (Math.random() - 0.5))) { G.audio.sfx('hurt'); p.vy = -4.5; } }
    G.render.camera(Game, false);
    if (p.dead > 150) Game.respawn();
  };
})((window.SGS = window.SGS || {}));
