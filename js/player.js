/* The hero: movement state machine (stand / crouch / morph ball), jump + space jump + dash, aim, damage. Positions: x = centre, y = feet. */
(function (G) {
  'use strict';
  const PH = G.phys, U = G.U, E = 0.001;
  const P = {};
  G.player = P;
  const SZ = { stand: [14, 42], crouch: [14, 26], ball: [16, 15] };
  const K = { walk: 1.7, run: 2.5, acc: 0.22, dec: 0.38, airAcc: 0.16, airDec: 0.04, g: 0.3, fall: 6.6, jump: 6.1, cut: 2.2, airJump: 5.0, dash: 4.4, ball: 1.9 };
  P.K = K;
  P.create = function (x, y) {
    return { x, y, w: 14, h: 42, vx: 0, vy: 0, ground: false, face: 1, mode: 'stand', anim: 0, aim: 'fwd', coyote: 0, jbuf: 0, airJumps: 1, dash: 0, dashCd: 0, dashAir: true, inv: 0, hurt: 0, en: 99, tanks: 0, missiles: 5, missileMax: 5, sbombs: 0, sbombMax: 0, supers: 0, superMax: 0, sel: 0, charge: 0, fireCd: 0, held: 0, bombCd: 0, crouchT: 0, dead: 0, spin: 0, drop: false, landT: 0, suit: 'cobalt' };
  };
  P.enMax = (p) => 99 + 100 * p.tanks;
  P.fits = (g, p, mode) => { const [w, h] = SZ[mode]; return !PH.boxSolid(g.room, p.x - w / 2, p.y - h, p.x + w / 2, p.y - E); };
  P.setMode = function (g, p, mode) {
    if (p.mode === mode) return true;
    if (!P.fits(g, p, mode)) {
      /* squeezed against a wall (a 16px ball beside a 14px body): slide up to 4px sideways to find room */
      const x0 = p.x; let ok = false;
      for (const d of [1, -1, 2, -2, 3, -3, 4, -4]) { p.x = x0 + d; if (P.fits(g, p, mode) && !PH.boxSolid(g.room, p.x - SZ[p.mode][0] / 2, p.y - SZ[p.mode][1], p.x + SZ[p.mode][0] / 2, p.y - E)) { ok = true; break; } p.x = x0; }
      if (!ok) { p.x = x0; return false; }
    }
    p.mode = mode; p.w = SZ[mode][0]; p.h = SZ[mode][1]; p.crouchT = 0;
    return true;
  };
  /* pose: which painted frame the hero shows right now (shared by drawing and the muzzle position); e = aim elevation in degrees (up positive) */
  const AIM = [['aim_90', 90], ['aim_70', 70], ['aim_45', 45], ['aim_20', 20], ['aim_0', 0], ['aim_m20', -20], ['aim_m45', -45], ['aim_m75', -75]];
  const CROUCH = [['crouch_up', 90], ['crouch_45', 45], ['crouch_0', 0], ['crouch_down', -30]];
  const nearest = (list, e) => { let n = list[0][0], bd = 1e9; for (const [k, a] of list) { const d = Math.abs(a - e); if (d < bd) { bd = d; n = k; } } return n; };
  P.elev = function (p) {
    let e = p.aim === 'up' ? 90 : p.aim === 'diagUp' ? 45 : p.aim === 'diagDown' ? -45 : 0;
    if (p.aimAng !== null && p.aimAng !== undefined) e = Math.atan2(-Math.sin(p.aimAng), Math.abs(Math.cos(p.aimAng))) * 180 / Math.PI;
    return e;
  };
  P.pose = function (p) {
    if (G.game && G.game.getAnim) return { n: 'itemget', dy: 0 };                                      /* victory stance: cannon arm raised */
    const e = P.elev(p), sp = Math.abs(p.vx), t = G.game ? G.game.time : 0;
    if (p.mode === 'crouch') return { n: nearest(CROUCH, e), dy: 0 };
    if (p.hurt > 0 && !p.dead) return { n: p.ground ? 'skid' : 'fall', dy: 0 };                         /* knocked back: leaning away from the hit */
    if (!p.ground) return { n: p.vy < 0 && e >= 30 && e <= 75 ? 'jump' : e > -30 && e < 25 ? 'fall' : nearest(AIM, e), dy: 0 };
    if (p.landT > 2) return { n: 'land', dy: 0 };
    if (sp > 0.25) {
      if (Math.sign(p.vx) !== p.face && sp > 1.0) return { n: 'skid', dy: 0 };
      const i = Math.floor(p.anim * 1.6) % 8;
      return Math.abs(e) <= 30 ? { n: 'run' + i, dy: 0 } : { n: nearest(AIM, e), dy: (i & 2) ? -1 : 0 };
    }
    return { n: nearest(AIM, e), dy: (Math.floor(t / 40) & 1) ? 1 : 0 };
  };
  P.muzzle = function (p) {
    const f = p.face;
    if (p.mode === 'ball') return { x: p.x + 17 * f, y: p.y - 8 };
    if (p.spinning && !p.ground) return { x: p.x + 14 * f, y: p.y - 22 };
    const q = P.pose(p), fr = G.sprites.hero[p.suit || 'cobalt'][q.n];
    return { x: p.x + f * fr.tx, y: p.y + fr.ty + q.dy };
  };
  P.aimVec = function (p) {
    if (p.aimAng !== null && p.aimAng !== undefined) return { x: Math.cos(p.aimAng), y: Math.sin(p.aimAng) };
    const f = p.face, r = Math.SQRT1_2;
    return p.aim === 'up' ? { x: 0, y: -1 } : p.aim === 'diagUp' ? { x: f * r, y: -r } : p.aim === 'diagDown' ? { x: f * r, y: r } : { x: f, y: 0 };
  };
  P.hurt = function (g, p, dmg, fromX) {
    if (p.inv > 0 || p.dead) return false;
    if (G.settings.hard) dmg = Math.round(dmg * 1.6);
    p.en -= dmg; p.inv = 75; p.hurt = 14; p.charge = 0;
    const d = p.x >= fromX ? 1 : -1;
    p.vx = 2.4 * d; p.vy = -3; p.ground = false; p.dash = 0;
    g.shake = Math.max(g.shake, 5); g.hitStop = 5;
    if (p.en <= 0) { p.en = 0; p.dead = 1; p.vx = 0; }
    return true;
  };
  /* which sprite frame to draw */
  P.frame = function (p) {
    const H = G.sprites.hero[p.suit || 'cobalt'];
    if (G.game && G.game.getAnim) return H.itemget;
    if (p.mode === 'ball') return H['ball' + ((Math.floor(p.ballRot || 0) % 4 + 4) % 4)];          /* spins the way it rolls (the sprite is never mirrored) */
    if (p.spinning && !p.ground) return H['spin' + (Math.floor(p.spinT / 2.4) & 7)];
    if (G.game && G.game.saveAnim) return H.front;
    return H[P.pose(p).n];
  };
})((window.SGS = window.SGS || {}));
