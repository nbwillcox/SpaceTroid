/* Music sequencer (playback). Needs js/music.js. */
(function (G) {
  'use strict';
  const MU = G.music, T = MU.themes, SC = MU.scales;
  const mid = (root, sc, deg) => { const s = SC[sc], oct = Math.floor(deg / s.length); return root + s[((deg % s.length) + s.length) % s.length] + 12 * oct; };
  const hz = (m) => 440 * Math.pow(2, (m - 69) / 12);
  function note(ctx, dst, type, f, t, dur, vol) {
    const o = ctx.createOscillator(), g = ctx.createGain(); o.type = type; o.frequency.value = f;
    g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(vol, t + 0.012); g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
    o.connect(g); g.connect(dst); o.start(t); o.stop(t + dur + 0.05);
  }
  function drum(ctx, dst, kind, t) {
    if (kind === 'k') { const o = ctx.createOscillator(), g = ctx.createGain(); o.frequency.setValueAtTime(140, t); o.frequency.exponentialRampToValueAtTime(40, t + 0.12); g.gain.setValueAtTime(0.16, t); g.gain.exponentialRampToValueAtTime(0.001, t + 0.14); o.connect(g); g.connect(dst); o.start(t); o.stop(t + 0.16); }
    else if (kind === 'h') { const n = Math.floor(ctx.sampleRate * 0.04), b = ctx.createBuffer(1, n, ctx.sampleRate), d = b.getChannelData(0); for (let i = 0; i < n; i++) d[i] = (Math.random() * 2 - 1) * (1 - i / n); const s = ctx.createBufferSource(), f = ctx.createBiquadFilter(), g = ctx.createGain(); s.buffer = b; f.type = 'highpass'; f.frequency.value = 6000; g.gain.value = 0.05; s.connect(f); f.connect(g); g.connect(dst); s.start(t); }
  }
  function tick() {
    const ctx = G.audio.ctx, th = T[MU.cur]; if (!ctx || !th || !MU.gain) return;
    MU.gain.gain.value = G.settings.music * 0.9;
    const spb = 60 / th.bpm / 4;
    while (MU.next < ctx.currentTime + 0.18) {
      const s = MU.step % 16, bar = Math.floor(MU.step / 16) % 4, t = MU.next;
      const b = th.bass[s]; if (b !== null) note(ctx, MU.gain, th.bw, hz(mid(th.root - 12, th.sc, b + th.pad[bar])), t, spb * 3.2, 0.09);
      const a = th.arp[s]; if (a !== null) note(ctx, MU.gain, th.aw, hz(mid(th.root + 12, th.sc, a + th.pad[bar])), t, spb * 1.8, th.av);
      if (s === 0) for (const k of [0, 2, 4]) note(ctx, MU.gain, th.pw, hz(mid(th.root, th.sc, th.pad[bar] + k)), t, spb * 15, 0.022);
      const d = th.drums[s]; if (d !== '.') drum(ctx, MU.gain, d, t);
      MU.next += spb; MU.step++;
    }
  }
  MU.play = function (name) {
    if (MU.cur === name) return;
    const A = G.audio; if (!A.ctx) { MU.pending = name; return; }
    MU.cur = name; MU.step = 0;
    if (!MU.gain) { MU.gain = A.ctx.createGain(); MU.gain.connect(A.ctx.destination); }
    MU.next = A.ctx.currentTime + 0.05;
    if (!MU.timer) MU.timer = setInterval(tick, 40);
  };
  MU.stop = function () { MU.cur = null; };
  const unlock = () => { if (MU.pending) { const n = MU.pending; MU.pending = null; MU.cur = null; MU.play(n); } };
  window.addEventListener('keydown', () => setTimeout(unlock, 80)); window.addEventListener('pointerdown', () => setTimeout(unlock, 80));
  MU.forRoom = function (g) { if (g.boss && g.boss.state !== 'wait' && !g.boss.dead) MU.play('boss'); else if (g.escape) MU.play('escape'); else MU.play('z' + (g.room.zone || 1)); };
})((window.SGS = window.SGS || {}));
