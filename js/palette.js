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
  /* letter -> hex for sprite grids ('.' is transparent) */
  P.keys = function (armor) {
    const R = P.ramps, A = R[armor || 'cobalt'], k = {};
    k.o = A[0]; k['1'] = A[1]; k['2'] = A[2]; k['3'] = A[3]; k['4'] = A[4];
    k.s = R.gold[0]; k.k = R.gold[1]; k.y = R.gold[2]; k.Y = R.gold[3]; k.w = R.gold[4];
    k.x = R.visor[1]; k.v = R.visor[2]; k.V = R.visor[3]; k.W = R.visor[4]; k.q = R.visor[0];
    k.U = R.under[1]; k.u = R.under[2]; k.n = R.under[3]; k.N = R.under[4]; k.b = R.under[0];
    k.z = R.metal[0]; k.M = R.metal[1]; k.m = R.metal[2]; k.l = R.metal[3]; k.L = R.metal[4];
    k.d = R.energy[0]; k.g = R.energy[1]; k.e = R.energy[2]; k.E = R.energy[3]; k.h = R.energy[4];
    return k;
  };
})((window.SGS = window.SGS || {}));
