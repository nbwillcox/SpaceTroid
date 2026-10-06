/* The hero: movement state machine (stand / crouch / morph ball), jump + space jump + dash, aim, damage. Positions: x = centre, y = feet. */
(function (G) {
  'use strict';
  const PH = G.phys, U = G.U, E = 0.001;
  const P = {};
  G.player = P;
  const SZ = { stand: [14, 42], crouch: [14, 26], ball: [12, 12] };
  const K = { walk: 1.7, run: 2.5, acc: 0.22, dec: 0.38, airAcc: 0.16, airDec: 0.04, g: 0.3, fall: 6.6, jump: 6.1, cut: 2.2, airJump: 5.0, dash: 4.4, ball: 1.9 };
  P.K = K;
  P.create = function (x, y) {
    return { x, y, w: 14, h: 42, vx: 0, vy: 0, ground: false, face: 1, mode: 'stand', anim: 0, aim: 'fwd', coyote: 0, jbuf: 0, airJumps: 1, dash: 0, dashCd: 0, dashAir: true, inv: 0, hurt: 0, en: 99, tanks: 0, missiles: 5, missileMax: 5, supers: 0, superMax: 0, sel: 0, charge: 0, fireCd: 0, held: 0, bombCd: 0, crouchT: 0, dead: 0, spin: 0, drop: false, landT: 0, suit: 'cobalt' };
  };
  P.enMax = (p) => 99 + 100 * p.tanks;
  P.fits = (g, p, mode) => { const [w, h] = SZ[mode]; return !PH.boxSolid(g.room, p.x - w / 2, p.y - h, p.x + w / 2, p.y - E); };
  P.setMode = function (g, p, mode) {
    if (p.mode === mode) return true;
    if (!P.fits(g, p, mode)) return false;
    p.mode = mode; p.w = SZ[mode][0]; p.h = SZ[mode][1]; p.crouchT = 0;
    return true;
  };
  P.muzzle = function (p) {
    const f = p.face, c = p.mode === 'crouch', a = p.aim;
    if (a === 'up') return { x: p.x + 3 * f, y: p.y - (c ? 30 : 46) };
    if (a === 'diagUp') return { x: p.x + 14 * f, y: p.y - (c ? 24 : 38) };
    if (a === 'diagDown') return { x: p.x + 14 * f, y: p.y - 15 };
    return { x: p.x + 17 * f, y: p.y - (c ? 15 : 26) };
  };
  P.aimVec = function (p) {
    const f = p.face, r = Math.SQRT1_2;
    return p.aim === 'up' ? { x: 0, y: -1 } : p.aim === 'diagUp' ? { x: f * r, y: -r } : p.aim === 'diagDown' ? { x: f * r, y: r } : { x: f, y: 0 };
  };
  P.hurt = function (g, p, dmg, fromX) {
    if (p.inv > 0 || p.dead) return false;
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
    if (p.mode === 'ball') return H['ball' + (((Math.floor(p.anim * 1.2) * p.face) % 4 + 4) % 4)];
    if (p.mode === 'crouch') return H.crouch;
    const up = p.aim === 'up' || p.aim === 'diagUp';
    if (!p.ground) return up ? H.jumpUp : p.vy < 0 || p.dash > 0 ? H.jump : H.fall;
    if (Math.abs(p.vx) > 0.25) return up ? H.runUp : H['run' + (Math.floor(p.anim) & 7)];
    return p.aim === 'up' ? H.aimUp : p.aim === 'diagUp' ? H.aimDiagUp : p.aim === 'diagDown' ? H.aimDiagDown : H.idle;
  };
})((window.SGS = window.SGS || {}));
