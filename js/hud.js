/* Heads-up display: energy + tanks, missile / super counts, charge bar. */
(function (G) {
  'use strict';
  const PX = G.px, H = {};
  G.hud = H;
  const txt = (ctx, s, x, y, c, a) => PX.text(ctx, s, x, y, { s: 1, c: c || '#e8f0ff', o: '#0a0e2c', a });
  H.draw = function (ctx, g, time) {
    const p = g.P, max = G.player.enMax(p), full = Math.floor(p.en / 100), rest = Math.ceil(p.en % 100);
    ctx.fillStyle = 'rgba(10,14,44,0.55)'; ctx.fillRect(4, 4, 92, 30);
    txt(ctx, 'EN', 8, 8, '#86f0f2'); txt(ctx, String(Math.max(0, p.en > 0 && p.en < 1 ? 1 : Math.ceil(p.en))).padStart(3, '0'), 24, 8, p.en < 30 && Math.floor(time * 4) % 2 ? '#ec5c4a' : '#ffffff');
    for (let i = 0; i < p.tanks; i++) { ctx.fillStyle = i < full ? '#2cbad8' : '#1b2c66'; ctx.fillRect(8 + i * 7, 18, 5, 5); ctx.fillStyle = i < full ? '#f2ffff' : '#2b4fa4'; ctx.fillRect(8 + i * 7, 18, 5, 1); }
    ctx.fillStyle = '#10142e'; ctx.fillRect(8, 26, 84, 3); ctx.fillStyle = p.en / max < 0.3 ? '#ec5c4a' : '#4cd2b8'; ctx.fillRect(8, 26, Math.round(84 * Math.min(1, p.en / Math.max(1, max))), 3);
    if (g.abil.missiles) { const sel = p.sel === 0; ctx.fillStyle = sel ? '#efba42' : '#3a3550'; ctx.fillRect(100, 5, 36, 14); ctx.fillStyle = '#10142e'; ctx.fillRect(101, 6, 34, 12); ctx.fillStyle = '#ec5c4a'; ctx.fillRect(104, 9, 7, 3); ctx.fillRect(111, 10, 2, 1); ctx.fillStyle = '#e8ecf8'; ctx.fillRect(104, 12, 7, 2); txt(ctx, String(p.missiles).padStart(2, '0'), 117, 9, sel ? '#fff2a8' : '#98a6ca'); }
    if (g.abil.supers) { const sel = p.sel === 1; ctx.fillStyle = sel ? '#6cf08a' : '#3a3550'; ctx.fillRect(138, 5, 30, 14); ctx.fillStyle = '#10142e'; ctx.fillRect(139, 6, 28, 12); ctx.fillStyle = '#2a8a4a'; ctx.fillRect(142, 9, 7, 3); ctx.fillStyle = '#6cf08a'; ctx.fillRect(142, 12, 7, 2); txt(ctx, String(p.supers).padStart(2, '0'), 152, 9, sel ? '#d8ffe0' : '#98a6ca'); }
    if (p.charge > 0) { ctx.fillStyle = '#10142e'; ctx.fillRect(100, 22, 40, 5); ctx.fillStyle = p.charge >= 50 ? '#ffffff' : '#ffd24a'; ctx.fillRect(101, 23, Math.round(38 * p.charge / 60), 3); }
    const B = g.abil.beams; let x = 102; for (const [k, c, n] of [['ice', '#7ad8ff', 'I'], ['wave', '#b878ff', 'W'], ['plasma', '#ff7a2a', 'P']]) if (g.abil['has' + n.replace('I', 'Ice').replace('W', 'Wave').replace('P', 'Plasma')]) { ctx.fillStyle = B[k] ? c : '#2a3050'; ctx.fillRect(x, 31, 6, 3); x += 8; }
    if (p.dead > 30) { ctx.fillStyle = 'rgba(10,14,44,' + Math.min(0.8, (p.dead - 30) / 60) + ')'; ctx.fillRect(0, 0, 480, 270); if (p.dead > 60) PX.text(ctx, 'SIGNAL LOST', 240, 128, { s: 2, c: '#ec5c4a', o: '#0a0e2c', a: 'c' }); }
  };
})((window.SGS = window.SGS || {}));
