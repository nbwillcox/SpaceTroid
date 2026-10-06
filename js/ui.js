/* Canvas menus (logic): title, save slots, options, pause, end screen. Up/Down move, Left/Right change values, Jump / Fire / Enter select, Esc / P go back. */
(function (G) {
  'use strict';
  const S = G.settings, U = { mode: 'title', sel: 0, from: 'title', confirm: null, slotMode: 'new' };
  G.ui = U;
  const bar = (v) => '[' + '#'.repeat(Math.round(v * 10)) + '-'.repeat(10 - Math.round(v * 10)) + ']';
  const anySave = () => [0, 1, 2].some((n) => G.save.read(n));
  U.items = {
    title: () => [{ k: 'new', t: 'NEW GAME' }, { k: 'cont', t: 'CONTINUE', off: !anySave() }, { k: 'opt', t: 'OPTIONS' }],
    pause: () => [{ k: 'resume', t: 'RESUME' }, { k: 'map', t: 'MAP' }, { k: 'opt', t: 'OPTIONS' }, { k: 'quit', t: 'QUIT TO TITLE' }],
    options: () => [{ k: 'sfx', t: 'SOUND VOLUME  ' + bar(S.sfx) }, { k: 'music', t: 'MUSIC VOLUME  ' + bar(S.music) }, { k: 'mouse', t: 'MOUSE AIM  ' + (S.mouseAim ? 'ON' : 'OFF') }, { k: 'shake', t: 'SCREEN SHAKE  ' + (S.shake ? 'ON' : 'OFF') }, { k: 'reduced', t: 'REDUCED EFFECTS  ' + (S.reduced ? 'ON' : 'OFF') }, { k: 'pad', t: 'GAMEPAD  ' + (S.gamepad ? 'ON' : 'OFF') }, { k: 'back', t: 'BACK' }],
    slots: () => [0, 1, 2].map((n) => ({ k: 'slot', n, rec: G.save.read(n) })).concat([{ k: 'back', t: 'BACK' }]),
  };
  U.open = function (mode, from) {
    U.mode = mode; U.sel = 0; U.confirm = null; if (from) U.from = from;
    if (mode === 'slots' && U.slotMode === 'cont') U.sel = Math.max(0, [0, 1, 2].findIndex((n) => G.save.read(n)));
  };
  U.back = function () { if (U.mode === 'options') U.open(U.from === 'pause' ? 'pause' : 'title'); else if (U.mode === 'slots') U.open('title'); };
  U.update = function () {
    const D = G.input.down, M = G.main, list = U.items[U.mode] ? U.items[U.mode]() : [], go = D.jump || D.fire || D.start;
    if (U.mode === 'end') { if (go || D.pause) M.toTitle(); return; }
    if (U.confirm) {
      if (D.l || D.r || D.u || D.d) U.confirm.yes = !U.confirm.yes;
      if (go) { if (U.confirm.yes) M.startSlot(U.confirm.n, true); U.confirm = null; } else if (D.pause) U.confirm = null;
      return;
    }
    if (D.d) U.sel = (U.sel + 1) % list.length;
    if (D.u) U.sel = (U.sel + list.length - 1) % list.length;
    const it = list[U.sel]; if (!it) return;
    if (U.mode === 'options' && (D.l || D.r)) {
      const d = D.r ? 0.1 : -0.1, cl = (v) => Math.max(0, Math.min(1, Math.round((v + d) * 10) / 10));
      if (it.k === 'sfx') { S.sfx = cl(S.sfx); G.audio.sfx('pickup'); } else if (it.k === 'music') S.music = cl(S.music);
      else if (it.k === 'mouse') S.mouseAim = !S.mouseAim; else if (it.k === 'shake') S.shake = !S.shake; else if (it.k === 'reduced') S.reduced = !S.reduced; else if (it.k === 'pad') S.gamepad = !S.gamepad;
      S.save();
    }
    if (D.pause && U.mode !== 'title') { if (U.mode === 'pause') M.resume(); else U.back(); return; }
    if (!go || it.off) return;
    switch (it.k) {
      case 'new': U.slotMode = 'new'; U.open('slots'); break;
      case 'cont': U.slotMode = 'cont'; U.open('slots'); break;
      case 'opt': U.open('options', U.mode); break;
      case 'slot': if (U.slotMode === 'cont') { if (it.rec) M.startSlot(it.n, false); } else if (it.rec) U.confirm = { n: it.n, yes: false }; else M.startSlot(it.n, true); break;
      case 'resume': M.resume(); break;
      case 'map': M.openMap(); break;
      case 'quit': M.toTitle(); break;
      case 'mouse': S.mouseAim = !S.mouseAim; S.save(); break;
      case 'shake': S.shake = !S.shake; S.save(); break;
      case 'reduced': S.reduced = !S.reduced; S.save(); break;
      case 'pad': S.gamepad = !S.gamepad; S.save(); break;
      case 'back': U.back(); break;
      default: break;
    }
  };
})((window.SGS = window.SGS || {}));
