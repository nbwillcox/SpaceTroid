/* Per-step hero update: input -> mode changes, aim, run/jump/dash, collision, then weapons. */
(function (G) {
  'use strict';
  const P = G.player, PH = G.phys, K = P.K, E = 0.001;
  const approach = (v, t, r) => (v < t ? Math.min(t, v + r) : Math.max(t, v - r));
  function aimFrom(g, p, I) {
    const S = G.settings, M = G.input.mouse;
    if (S.mouseAim && M.on && g.cam && !I.u && !(I.aim && I.d) && (M.fire || performance.now() - M.t < 2500)) {
      const ox = M.x + g.cam.x - p.x, oy = M.y + g.cam.y - (p.y - 28), ang = Math.atan2(-oy, Math.abs(ox));
      if (Math.abs(ox) > 3) p.face = ox > 0 ? 1 : -1;
      return ang > 1.15 ? 'up' : ang > 0.4 ? 'diagUp' : ang < -0.4 ? 'diagDown' : 'fwd';
    }
    if (I.u) return (I.l || I.r) ? 'diagUp' : 'up';
    if (I.d && !p.ground && (I.l || I.r)) return 'diagDown';
    if (I.aim && I.d) return 'diagDown';
    return 'fwd';
  }
  P.update = function (g) {
    const p = g.P, I = G.input.held, D = G.input.down, room = g.room, A = g.abil;
    if (p.dead) { p.dead++; return; }
    p.inv = Math.max(0, p.inv - 1); p.hurt = Math.max(0, p.hurt - 1); p.fireCd = Math.max(0, p.fireCd - 1); p.bombCd = Math.max(0, p.bombCd - 1); p.dashCd = Math.max(0, p.dashCd - 1); p.landT = Math.max(0, p.landT - 1); p.spin = Math.max(0, p.spin - 1);
    const lock = p.hurt > 0;
    const dir = lock ? 0 : (I.r ? 1 : 0) - (I.l ? 1 : 0);
    if (D.jump) p.jbuf = 7; else p.jbuf = Math.max(0, p.jbuf - 1);
    if (p.ground) { p.coyote = 5; p.airJumps = A.spacejump ? 1 : 0; p.dashAir = true; } else p.coyote = Math.max(0, p.coyote - 1);
    /* ---- mode changes: Down crouches, Down again morphs, Up / jump / moving stands ---- */
    p.crouchT++;
    if (!lock && p.mode !== 'ball') {
      if (p.mode === 'stand' && p.ground && D.d && !I.aim) P.setMode(g, p, 'crouch');
      else if (p.mode === 'crouch' && D.d && p.crouchT > 6 && A.morph) P.setMode(g, p, 'ball');
      else if (p.mode === 'crouch' && (D.u || p.jbuf > 0 || dir || !p.ground)) P.setMode(g, p, 'stand');
    } else if (!lock && p.mode === 'ball' && (D.u || (p.jbuf > 0 && p.ground)) && P.fits(g, p, 'stand')) { P.setMode(g, p, 'stand'); p.jbuf = 0; }
    const ball = p.mode === 'ball';
    /* ---- aim + facing ---- */
    p.aim = ball ? 'fwd' : aimFrom(g, p, I);
    if (dir && !(I.aim && !ball)) p.face = dir; else if (I.aim && !ball && (I.l || I.r)) p.face = I.r ? 1 : -1;
    /* ---- horizontal ---- */
    const moving = dir && !(I.aim && !ball);
    const sprint = I.dash && p.ground && p.mode === 'stand';   /* holding Shift always sprints; the tap-dash burst is the gated upgrade */
    const top = ball ? K.ball : sprint ? K.run : K.walk;
    const slick = p.ground && G.room.at(room, Math.floor(p.x / 16), Math.floor((p.y + 1) / 16)) === 10;   /* ice floor: slow to start, slow to stop */
    if (p.dash > 0) { p.dash--; p.vx = p.face * K.dash; p.vy = 0; if (!p.dash) p.dashCd = 22; }
    else if (moving) p.vx = approach(p.vx, dir * top, p.ground ? (Math.sign(p.vx) === -dir ? K.dec : K.acc) * (slick ? 0.3 : 1) : (Math.abs(p.vx) > top && Math.sign(p.vx) === dir ? 0.02 : K.airAcc));
    else p.vx = approach(p.vx, 0, p.ground ? K.dec * (slick ? 0.12 : 1) : K.airDec);
    if (A.dash && D.dash && p.dashCd === 0 && p.mode === 'stand' && !lock && p.dash === 0 && !I.d && (p.ground || p.dashAir)) { p.dash = 11; if (!p.ground) p.dashAir = false; G.fx.puff(p.x - p.face * 6, p.y - 4, 4); }
    /* ---- jump (coyote + buffer), space jump, variable height, drop through ledges ---- */
    if (!lock && p.mode === 'stand' && p.jbuf > 0) {
      if (p.dash > 0 && (p.coyote > 0 || (p.airJumps > 0 && A.spacejump))) { p.vx = p.face * K.dash; p.dash = 0; p.dashCd = 10; }
      if (p.ground && I.d && PH.support(room, p, p.y - E, p.y + 1, true) === null) { p.drop = true; p.ground = false; p.y += 1; p.jbuf = 0; p.coyote = 0; }
      else if (p.coyote > 0) {
        if (p.dash > 0) { p.vx = p.face * K.dash; p.dash = 0; p.dashCd = 10; }
        p.vy = -K.jump; p.jbuf = 0; p.coyote = 0; p.ground = false; G.audio.sfx('jump'); p.jumping = true;
        p.spinning = (Math.abs(p.vx) > 0.8 || dir !== 0) && !I.u && !I.fire; p.spinT = 0; p.noSpin = false;
      }
      else if (!p.ground && p.airJumps > 0 && A.spacejump) { p.vy = -K.airJump; p.airJumps--; p.jbuf = 0; p.spin = 16; p.jumping = true; if (!p.noSpin) { p.spinning = true; p.spinT = 0; } G.fx.ring(p.x, p.y - 16); G.audio.sfx('spacejump'); }
    }
    if (p.ground || p.vy >= 0) p.jumping = false;
    if (!I.jump && p.jumping && p.vy < -K.cut && !p.dash && !lock) p.vy = -K.cut;
    if (p.ground || ball || lock || p.mode !== 'stand') { p.spinning = false; p.noSpin = false; }
    else if (p.spinning && (I.fire || I.u || D.missile)) { p.spinning = false; p.noSpin = true; }
    if (p.spinning) p.spinT++;
    /* ---- gravity + collision ---- */
    if (!p.dash) p.vy = Math.min(K.fall, p.vy + K.g);
    const wasAir = !p.ground, vyBefore = p.vy;
    PH.moveX(room, p, p.vx);
    p.ground = p.ground && PH.onGround(room, p, p.drop);
    PH.moveY(room, p, p.vy, p.drop);
    if (p.ground && wasAir && vyBefore > 2) { p.landT = 6; G.fx.puff(p.x, p.y, 3); }
    if (p.ground || (p.drop && PH.support(room, p, p.y - 10, p.y + 2, false) === null && p.vy > 1)) p.drop = false;
    p.anim += Math.abs(p.vx) * (ball ? 0.16 : 0.12);
    G.weapons.playerFire(g, p, I, D);
  };
})((window.SGS = window.SGS || {}));
