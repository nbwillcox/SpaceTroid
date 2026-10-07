/* Compiles every art grid into canvases once at start-up: hero frames (+ mirrored copies), ball, tiles, enemies. */
(function (G) {
  'use strict';
  const A = G.art, S = {};
  G.sprites = S;
  const flipC = (c) => { const o = document.createElement('canvas'); o.width = c.width; o.height = c.height; const x = o.getContext('2d'); x.translate(c.width, 0); x.scale(-1, 1); x.drawImage(c, 0, 0); return o; };
  const both = (rows, armor, name) => { const s = A.make(rows, armor, name); return { r: s.c, l: flipC(s.c), w: s.w, h: s.h }; };
  S.flipC = flipC;
  /* layered hero: torso (per aim angle and lean) over legs (per pose), composed once per distinct combination and cached */
  const h2 = { grids: new Map(), frames: new Map() };
  const gridCanvas = (suit, kind, key) => { const k = suit + kind + key; let c = h2.grids.get(k); if (!c) { c = A.make(A.hero2[kind][key], suit, 'h2' + k).c; h2.grids.set(k, c); } return c; };
  S.heroFront = function (suit) {                                              /* the front-facing pose used while saving */
    const k = suit + '|front'; let f = h2.frames.get(k);
    if (!f) { const c = A.make(A.hero2.front, suit, 'h2front' + suit).c; f = { r: c, l: c, w: 34, h: 47, ay: 46 }; h2.frames.set(k, f); }
    return f;
  };
  S.heroLayered = function (suit, ang, lean, legs, dy) {
    const k = suit + '|' + ang + '|' + lean + '|' + legs + '|' + dy; let f = h2.frames.get(k);
    if (!f) {
      const c = document.createElement('canvas'); c.width = 34; c.height = 47; const x = c.getContext('2d'); x.imageSmoothingEnabled = false;
      const lg = gridCanvas(suit, 'legs', legs);
      x.drawImage(lg, 0, 0, 34, 1, 0, 2 + 24, 34, 1);            /* a skirt row under the belt so an upward bob never leaves a seam */
      x.drawImage(lg, 0, 2 + 25);
      x.drawImage(gridCanvas(suit, 'top', ang + '_' + lean), 0, 2 + dy);
      f = { r: c, l: flipC(c), w: 34, h: 47, ay: 46 }; h2.frames.set(k, f);
    }
    return f;
  };
  S.build = function () {
    S.hero = {}; S.heroAx = 17; S.heroAy = 44;
    const hp = Object.assign({}, A.heroParts, A.ballParts);
    for (const suit of ['cobalt', 'crimson', 'teal']) {
      const o = {}; for (const k in hp) o[k] = both(hp[k], suit, k);
      S.hero[suit] = o;
    }
    const Z = A.zone1, M = A.zone1misc, D = A.zone1deco;
    /* one tileset per zone: the same hand-drawn grids, compiled with that zone's palette (plus zone-specific extras) */
    const tileset = (key, zone) => {
      const mk = (r, n) => A.make(r, key, n).c, t = { edge: {}, diag: {}, slopeR: mk(M.slopeR, 'sr'), slopeL: mk(M.slopeL, 'sl'), spikes: mk(M.spikes, 'sp'), shot: mk(M.blockShot, 'bs'), bomb: mk(M.blockBomb, 'bb'), missile: mk(M.blockMissile, 'bm') };
      for (const m in Z.edge) t.edge[m] = Z.edge[m].map((g, i) => mk(g, 'e' + m + '_' + i));
      for (const d in Z.diag) t.diag[d] = mk(Z.diag[d], 'd' + d);
      t.wall = D.bgWall.map((g, i) => mk(g, 'w' + i)); t.ledge = mk(D.ledge, 'ledge');
      const deco = { rune: D.rune.map((g, i) => mk(g, 'r' + i)), vine: D.vine.map((g, i) => mk(g, 'v' + i)), tuft: mk(D.tuft, 'tuft'), fern: mk(D.fern, 'fern'), rubble: mk(D.rubble, 'rub'), pillar: mk(D.pillar, 'pil') };
      t.wave = mk(A.zone3.wave, 'wave'); t.dashblock = mk(A.zone3.dashblock, 'dblk');
      t.deco = deco; t.top = [[deco.tuft, 3, 7], [deco.fern, 0, 11], [deco.rubble, 0, 7]]; t.hang = deco.vine.map((v) => [v, 4]);
      if (zone === 2) {
        const Z2 = A.zone2; t.ice = mk(Z2.ice, 'ice');
        const cr = Z2.crystal.map((g, i) => mk(g, 'cr' + i)); t.top = [[cr[0], 0, cr[0].height - 1], [cr[1], 4, cr[1].height - 1], [deco.rubble, 0, 7], [deco.tuft, 3, 7]];
        t.hang = Z2.icicle.map((g, i) => { const c = mk(g, 'ic' + i); return [c, 4]; });
      }
      if (zone === 3) { const Z3 = A.zone3; t.lava = Z3.lava.map((g, i) => mk(g, 'lv' + i)); t.lavaTop = Z3.lavaTop.map((g, i) => mk(g, 'lt' + i)); }
      return t;
    };
    S.tilesets = { 1: tileset('world', 1), 2: tileset('world2', 2), 3: tileset('world3', 3), 4: tileset('world4', 4), 5: tileset('world5', 5) }; S.tile = S.tilesets[1].tile || S.tilesets[1]; S.deco = S.tilesets[1].deco;
    S.bg1 = A.buildZone1Bg();                                                  /* only the title screen still uses a parallax backdrop; rooms are black space + back wall */
    const F = A.zone1foes;
    const F2 = A.zone2foes;
    const F3 = A.zone3foes, glow = (rows) => rows.map((r) => r.replace(/[Eeh]/g, (c) => ({ E: 'Y', e: 'y', h: 'w' })[c]));
    const F4 = A.zone4foes;
    const F5 = A.zone5foes, hglow = (rows) => rows.map((r) => r.replace(/[Eeh]/g, (c) => ({ E: 'D', e: 'C', h: 'F' })[c]));
    S.foe = { hmoth: A.zone1foes.moth.map((g) => both(hglow(g), 'visor', 'hmo')), guard: A.zone1foes.crawler.map((g) => both(g, 'visor', 'gua')), hpod: A.zone1foes.pod.map((g) => both(g, 'visor', 'hpo')), egg: F5.egg.map((g) => both(g, 'visor', 'egg')), jelly: F4.jelly.map((g) => both(g, 'teal', 'jel')), drone: A.zone1foes.crawler.map((g) => both(g, 'cobalt', 'drn')), rturret: F2.turret.map((g) => both(g, 'cobalt', 'rtu')), arc: [], cinder: A.zone1foes.crawler.map((g) => both(g, 'gold', 'cin')), hopper: F2.frostling.map((g) => both(glow(g), 'crimson', 'hop')), ember: F2.turret.map((g) => both(glow(g), 'crimson', 'emb')), magmite: F3.magmite.map((g) => both(g, 'crimson', 'mag')), wisp: F2.wisp.map((g) => both(g, 'teal', 'wi')), frostling: F2.frostling.map((g) => both(g, 'teal', 'fr')), turret: F2.turret.map((g) => both(g, 'teal', 'tu')), icicle: [both(A.zone2.icicle[2], 'world2', 'ici')], crawler: F.crawler.map((g) => both(g, 'crimson', 'cr')), moth: F.moth.map((g) => both(g, 'crimson', 'mo')), pod: F.pod.map((g) => both(g, 'crimson', 'pod')) };
    const W1 = A.world1, mkc = (rows, ramp, n) => A.make(rows, ramp, n).c;
    S.door = { blue: W1.door.map((g, i) => mkc(g, 'cobalt', 'db' + i)), red: W1.door.map((g, i) => mkc(g, 'crimson', 'dr' + i)), green: W1.door.map((g, i) => mkc(g, 'teal', 'dg' + i)), boss: W1.door.map((g, i) => mkc(g, 'gold', 'dB' + i)) };
    S.orb = {}; for (const r of ['cobalt', 'crimson', 'teal', 'gold', 'visor']) S.orb[r] = W1.orb.map((g, i) => mkc(g, r, 'orb' + r + i));
    S.tank = { energy: W1.tankEnergy.map((g) => mkc(g, 'cobalt', 'te')), missile: W1.tankMissile.map((g) => mkc(g, 'cobalt', 'tm')), super: W1.tankSuper.map((g) => mkc(g, 'cobalt', 'ts')) };
    const IT = A.items;                                                    /* item art: icons (the object itself), tank pickups, drop icons, shrine statues */
    S.icon = {}; for (const k in IT.icons) S.icon[k] = mkc(IT.icons[k], IT.ramps[k], 'ic' + k);
    S.tank = { energy: IT.tanks.energy.map((g) => mkc(g, 'cobalt', 'te')), missile: IT.tanks.missile.map((g) => mkc(g, 'crimson', 'tm')), super: IT.tanks.super.map((g) => mkc(g, 'teal', 'ts')) };
    S.drop = {}; for (const k in IT.drops) S.drop[k] = IT.drops[k].map((g, i) => mkc(g, IT.dropRamps[k], 'dr' + k + i));
    S.statue = { big: {}, small: {} }; for (let z = 1; z <= 5; z++) { S.statue.big[z] = mkc(IT.statue.big, z === 1 ? 'world' : 'world' + z, 'stb' + z); S.statue.small[z] = mkc(IT.statue.small, z === 1 ? 'world' : 'world' + z, 'sts' + z); }
    const BO = A.bosses, B1 = BO.beetle, bb = (g) => both(g, 'crimson', 'boss');
    S.boss = { walk: B1.walk.map(bb), rear: bb(B1.rear), tele: B1.tele.map(bb), charge: B1.charge.map(bb), stun: B1.stun.map(bb) };
    const B2 = BO.moth, b2 = (g) => A.make(g, 'teal', 'boss2').c;
    S.boss2 = { fly: B2.fly.map(b2), shoot: B2.shoot.map(b2), dive: b2(B2.dive), stun: B2.stun.map(b2), dead: b2(B2.dead) };
    const whites = new Map();
    S.whiteOf = (c) => { let w = whites.get(c); if (!w) { w = document.createElement('canvas'); w.width = c.width; w.height = c.height; const x = w.getContext('2d'); x.drawImage(c, 0, 0); x.globalCompositeOperation = 'source-in'; x.fillStyle = '#fff'; x.fillRect(0, 0, w.width, w.height); whites.set(c, w); } return w; };
    const BW = BO.wyrm; S.wyrm = { head: BW.head.map((g) => both(g, 'crimson', 'wh')), neck: A.make(BW.neck, 'crimson', 'wn').c, splash: BW.splash.map((g) => A.make(g, 'crimson', 'ws').c) };
    S.jellyBoss = BO.jelly.bell.map((g) => A.make(g, 'teal', 'bell').c);
    const BH = BO.heart; S.heart = { body: BH.heart.map((g) => A.make(g, 'visor', 'heart').c), node: BH.node.map((g) => A.make(g, 'visor', 'node').c) };
    S.pad = W1.pad.map((g) => mkc(g, 'cobalt', 'pad')); S.term = W1.terminal.map((g) => mkc(g, 'cobalt', 'term')); S.wreck = mkc(W1.wreck, 'cobalt', 'wreck');
  };
})((window.SGS = window.SGS || {}));
