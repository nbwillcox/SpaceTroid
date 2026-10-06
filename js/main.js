/* Boot, integer-scale letterboxing and the fixed 60 Hz loop. */
(function (G) {
  'use strict';
  const M = { time: 0, paused: false }, I = G.input, Game = G.game;
  G.main = M;
  const canvas = document.getElementById('game'), ctx = canvas.getContext('2d'), params = new URLSearchParams(location.search);
  canvas.width = 480; canvas.height = 270; ctx.imageSmoothingEnabled = false;
  function resize() {
    const w = window.innerWidth, h = window.innerHeight, k = Math.min(w / 480, h / 270), sc = k >= 1 ? Math.floor(k) : k, st = canvas.style;
    st.width = Math.round(480 * sc) + 'px'; st.height = Math.round(270 * sc) + 'px';
  }
  window.addEventListener('resize', resize); resize();
  G.sprites.build();
  Game.new(); Game.load(params.get('room') || 'sandbox');
  if (params.get('abil') === 'none') { for (const k of ['morph', 'bombs', 'missiles', 'supers', 'spacejump', 'dash', 'charge']) Game.abil[k] = false; }
  M.render = function () { G.render.draw(ctx, Game, Game.time / 60); G.hud.draw(ctx, Game, Game.time / 60); };
  let last = 0, acc = 0;
  function frame(now) {
    requestAnimationFrame(frame);
    let dt = (now - last) / 1000; last = now; if (!(dt > 0)) dt = 1 / 60; if (dt > 0.1) dt = 0.1;
    if (!M.paused) { acc += dt; while (acc >= 1 / 60) { I.poll(); Game.step(); acc -= 1 / 60; } }
    M.render();
  }
  document.addEventListener('visibilitychange', () => { if (document.hidden) I.clear(); });
  /* test hook: advance n steps with held keys, then draw (the pane does not run rAF while hidden) */
  M.run = function (n, held) { for (let i = 0; i < n; i++) { const nk = Object.assign({}, held || {}); for (const a in nk) if (!I.k[a]) I.lt[a] = true; I.k = nk; I.poll(); Game.step(); } M.render(); };
  requestAnimationFrame(frame);
})((window.SGS = window.SGS || {}));
