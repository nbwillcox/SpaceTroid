/* Compiles every art grid into canvases once at start-up: hero frames (+ mirrored copies), ball, tiles, enemies. */
(function (G) {
  'use strict';
  const A = G.art, S = {};
  G.sprites = S;
  const flipC = (c) => { const o = document.createElement('canvas'); o.width = c.width; o.height = c.height; const x = o.getContext('2d'); x.translate(c.width, 0); x.scale(-1, 1); x.drawImage(c, 0, 0); return o; };
  const both = (rows, armor, name) => { const s = A.make(rows, armor, name); return { r: s.c, l: flipC(s.c), w: s.w, h: s.h }; };
  S.flipC = flipC;
  S.build = function () {
    S.hero = {}; S.heroAx = 17; S.heroAy = 44;
    const hp = Object.assign({}, A.heroParts, A.ballParts);
    for (const suit of ['cobalt', 'crimson', 'teal']) {
      const o = {}; for (const k in hp) o[k] = both(hp[k], suit, k);
      S.hero[suit] = o;
    }
    const Z = A.zone1, M = A.zone1misc, D = A.zone1deco, mk = (r, n) => A.make(r, 'world', n).c;
    S.tile = { edge: {}, diag: {}, slopeR: mk(M.slopeR, 'sr'), slopeL: mk(M.slopeL, 'sl'), spikes: mk(M.spikes, 'sp'), shot: mk(M.blockShot, 'bs'), bomb: mk(M.blockBomb, 'bb'), missile: mk(M.blockMissile, 'bm') };
    for (const m in Z.edge) S.tile.edge[m] = Z.edge[m].map((g, i) => mk(g, 'e' + m + '_' + i));
    for (const d in Z.diag) S.tile.diag[d] = mk(Z.diag[d], 'd' + d);
    S.tile.wall = D.bgWall.map((g, i) => mk(g, 'w' + i));
    S.tile.ledge = mk(D.ledge, 'ledge');
    S.deco = { rune: D.rune.map((g, i) => mk(g, 'r' + i)), vine: D.vine.map((g, i) => mk(g, 'v' + i)), tuft: mk(D.tuft, 'tuft'), fern: mk(D.fern, 'fern'), rubble: mk(D.rubble, 'rub'), pillar: mk(D.pillar, 'pil') };
    const F = A.zone1foes;
    S.foe = { crawler: F.crawler.map((g) => both(g, 'crimson', 'cr')), moth: F.moth.map((g) => both(g, 'crimson', 'mo')), pod: F.pod.map((g) => both(g, 'crimson', 'pod')) };
    S.bg1 = A.buildZone1Bg();
    const W1 = A.world1, mkc = (rows, ramp, n) => A.make(rows, ramp, n).c;
    S.door = { blue: W1.door.map((g, i) => mkc(g, 'cobalt', 'db' + i)), red: W1.door.map((g, i) => mkc(g, 'crimson', 'dr' + i)), green: W1.door.map((g, i) => mkc(g, 'teal', 'dg' + i)), boss: W1.door.map((g, i) => mkc(g, 'gold', 'dB' + i)) };
    S.orb = {}; for (const r of ['cobalt', 'crimson', 'teal', 'gold']) S.orb[r] = W1.orb.map((g, i) => mkc(g, r, 'orb' + r + i));
    S.tank = { energy: W1.tankEnergy.map((g) => mkc(g, 'cobalt', 'te')), missile: W1.tankMissile.map((g) => mkc(g, 'cobalt', 'tm')), super: W1.tankSuper.map((g) => mkc(g, 'cobalt', 'ts')) };
    const B1 = A.boss1, bb = (g) => both(g, 'crimson', 'boss');
    S.boss = { walk: B1.walk.map(bb), rear: bb(B1.rear), tele: B1.tele.map(bb), charge: B1.charge.map(bb), stun: B1.stun.map(bb) };
    S.pad = W1.pad.map((g) => mkc(g, 'cobalt', 'pad')); S.term = W1.terminal.map((g) => mkc(g, 'cobalt', 'term')); S.wreck = mkc(W1.wreck, 'cobalt', 'wreck');
  };
})((window.SGS = window.SGS || {}));
