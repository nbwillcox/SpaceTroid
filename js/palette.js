/* The master palette: 5-step ramps (dark -> light) with hue-shifted shadows (cool) and highlights (warm), plus the letter keys used by every hand-authored sprite grid. */
(function (G) {
  'use strict';
  const P = {};
  G.pal = P;
  P.ramps = {
    cobalt: ['#10142e', '#1b2c66', '#2b4fa4', '#5688dc', '#a6ccff'],
    crimson: ['#2a0812', '#6a1224', '#b02a34', '#ec5c4a', '#ffb89c'],
    teal: ['#062a2e', '#0e5a62', '#1a948c', '#4cd2b8', '#b8ffe6'],
    gold: ['#2e1a0c', '#6b3d14', '#b87c1e', '#efba42', '#fff2a8'],
    visor: ['#2a0832', '#7a1472', '#d42c98', '#ff7ac6', '#ffe2f4'],
    under: ['#0a0c1c', '#181c36', '#2a3158', '#444f82', '#6672a8'],
    metal: ['#14172c', '#2e3452', '#5a658a', '#98a6ca', '#dde7fb'],
    energy: ['#06304c', '#146e94', '#2cbad8', '#86f0f2', '#f2ffff'],
  };
  /* zone-1 world ramps (Crash Site): cool violet stone, warm-lit moss, earth, dusk-fog sky */
  P.ramps.stone = ['#10142a', '#1f2744', '#33405e', '#52627a', '#7f8c96', '#b4b8ae'];
  P.ramps.moss = ['#0a2216', '#124028', '#1f6a34', '#4a9a3c', '#8cc84e', '#d4ee86'];
  P.ramps.earth = ['#1c1220', '#38202a', '#5c3a34', '#8a5a40', '#b88454'];
  P.ramps.fog = ['#0a0e2c', '#141a46', '#222c68', '#364488', '#566cac', '#8ea2d2'];
  P.ramps.dusk = ['#ffd9a0', '#f4a67c', '#d8688a'];
  /* world letters: stone 0-5, moss A-F, earth p q r t u, fog H I J K Q R, dusk W X Z, plus the sprite letters (gold, energy, metal, ...) */
  P.worldKeys = function () {
    const R = P.ramps, k = P.keys('cobalt');
    'ABCDEF'.split('').forEach((c, i) => { k[c] = R.moss[i]; });
    '012345'.split('').forEach((c, i) => { k[c] = R.stone[i]; });
    'pqrtu'.split('').forEach((c, i) => { k[c] = R.earth[i]; });
    'HIJKQR'.split('').forEach((c, i) => { k[c] = R.fog[i]; });
    k.W = R.dusk[0]; k.X = R.dusk[1]; k.Z = R.dusk[2];
    return k;
  };
  /* letter -> hex for sprite grids ('.' is transparent) */
  P.keys = function (armor) {
    if (armor === 'world') return P.worldKeys();
    const R = P.ramps, A = R[armor || 'cobalt'], k = {};
    k.o = A[0]; k['1'] = A[1]; k['2'] = A[2]; k['3'] = A[3]; k['4'] = A[4];
    k.s = R.gold[0]; k.k = R.gold[1]; k.y = R.gold[2]; k.Y = R.gold[3]; k.w = R.gold[4];
    k.x = R.visor[1]; k.v = R.visor[2]; k.V = R.visor[3]; k.W = R.visor[4]; k.q = R.visor[0];
    k.U = R.under[1]; k.u = R.under[2]; k.n = R.under[3]; k.N = R.under[4]; k.b = R.under[0];
    k.z = R.metal[0]; k.M = R.metal[1]; k.m = R.metal[2]; k.l = R.metal[3]; k.L = R.metal[4];
    k.d = R.energy[0]; k.g = R.energy[1]; k.e = R.energy[2]; k.E = R.energy[3]; k.h = R.energy[4];
    'ABCDEF'.split('').forEach((c, i) => { k[c] = R.moss[i]; });
    return k;
  };
})((window.SGS = window.SGS || {}));
