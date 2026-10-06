/* Canvas menus (drawing). */
(function (G) {
  'use strict';
  const PX = G.px, U = G.ui;
  const txt = (ctx, s, x, y, c, a, sz) => PX.text(ctx, s, x, y, { s: sz || 1, c: c || '#dde7fb', o: '#0a0e2c', a });
  const fmtTime = (t) => { t = Math.floor(t); return String(Math.floor(t / 3600)).padStart(2, '0') + ':' + String(Math.floor(t / 60) % 60).padStart(2, '0'); };
  function menu(ctx, list, y0, gap, big) {
    list.forEach((it, i) => {
      const on = i === U.sel, y = y0 + i * gap, sz = big ? 2 : 1, c = it.off ? '#364488' : on ? '#fff2a8' : '#a6ccff';
      txt(ctx, it.t, 240, y, c, 'c', sz);
      if (on && !it.off) { ctx.fillStyle = '#fff2a8'; ctx.fillRect(240 - Math.round(PX.textW(it.t, sz) / 2) - 12, y + (big ? 4 : 1), 5, 5); }
    });
  }
  function titleBg(ctx, time) {
    const bg = G.sprites.bg1, o = -Math.floor(time * 6) % 480, o2 = -Math.floor(time * 18) % 480;
    ctx.drawImage(bg.far, o, 0); ctx.drawImage(bg.far, o + 480, 0); ctx.drawImage(bg.mid, o2, 0); ctx.drawImage(bg.mid, o2 + 480, 0);
    ctx.fillStyle = 'rgba(6,8,26,0.35)'; ctx.fillRect(0, 0, 480, 270);
    ctx.drawImage(G.sprites.hero.cobalt.idle.r, 72, 224 - 44);
  }
  function slots(ctx) {
    txt(ctx, U.slotMode === 'cont' ? 'CONTINUE' : 'CHOOSE A SLOT', 240, 50, '#a6ccff', 'c', 2);
    U.items.slots().forEach((it, i) => {
      const y = 96 + i * 36, on = i === U.sel;
      if (it.k === 'back') { txt(ctx, 'BACK', 240, y + 6, on ? '#fff2a8' : '#8ea2d2', 'c'); return; }
      ctx.fillStyle = on ? '#2b4fa4' : '#141a46'; ctx.fillRect(80, y, 320, 30); ctx.fillStyle = on ? '#a6ccff' : '#364488'; ctx.fillRect(80, y, 320, 1); ctx.fillRect(80, y + 29, 320, 1);
      txt(ctx, 'SLOT ' + (it.n + 1), 90, y + 5, '#fff2a8');
      if (it.rec) { const sm = G.save.summary(it.rec); txt(ctx, sm.place.toUpperCase(), 90, y + 17, '#dde7fb'); txt(ctx, sm.pct + '%   ' + sm.tanks + ' TANKS   ' + fmtTime(sm.time), 390, y + 17, '#a6ccff', 'r'); }
      else txt(ctx, 'EMPTY', 90, y + 17, '#566cac');
    });
    if (U.confirm) { ctx.fillStyle = 'rgba(5,7,26,0.9)'; ctx.fillRect(100, 100, 280, 70); txt(ctx, 'OVERWRITE THIS SAVE?', 240, 112, '#ffb89c', 'c'); txt(ctx, 'NO', 200, 140, !U.confirm.yes ? '#fff2a8' : '#8ea2d2', 'c'); txt(ctx, 'YES', 280, 140, U.confirm.yes ? '#fff2a8' : '#8ea2d2', 'c'); }
  }
  function ending(ctx, time, g) {
    ctx.fillStyle = '#05071a'; ctx.fillRect(0, 0, 480, 270);
    txt(ctx, 'ZONE ' + g.room.zone + ' COMPLETE', 240, 60, '#fff2a8', 'c', 3); txt(ctx, g.room.zone === 1 ? 'THE LIFT DESCENDS INTO THE CRYO VAULTS...' : 'HEAT RISES FROM BELOW. THE MAGMA FORGE AWAITS...', 240, 100, '#a6ccff', 'c');
    const n = Object.keys(g.prog.items).length, tot = G.world.itemTotal();
    txt(ctx, 'ITEMS  ' + n + ' / ' + tot + '  (' + Math.round(100 * n / tot) + '%)', 240, 140, '#dde7fb', 'c'); txt(ctx, 'TIME  ' + fmtTime(g.playTime), 240, 156, '#dde7fb', 'c');
    txt(ctx, 'TO BE CONTINUED', 240, 196, '#ec5c4a', 'c', 2);
    if (Math.floor(time * 2) % 2) txt(ctx, 'PRESS JUMP', 240, 240, '#8ea2d2', 'c');
  }
  U.draw = function (ctx, time, g) {
    const m = U.mode;
    if (m === 'title' || m === 'slots' || (m === 'options' && U.from === 'title')) titleBg(ctx, time);
    else if (m !== 'end') { ctx.fillStyle = 'rgba(6,8,26,0.84)'; ctx.fillRect(0, 0, 480, 270); }
    if (m === 'title') {
      PX.text(ctx, 'SPACETROID', 240, 48, { s: 5, c: '#fff2a8', o: '#2e1a0c', a: 'c' }); txt(ctx, 'A FREE PIXEL EXPLORATION ADVENTURE', 240, 98, '#a6ccff', 'c');
      menu(ctx, U.items.title(), 128, 26, true); txt(ctx, 'CC BY-NC 4.0  -  GITHUB.COM/NBWILLCOX/SPACETROID', 240, 254, '#8ea2d2', 'c');
    } else if (m === 'slots') slots(ctx);
    else if (m === 'options') { txt(ctx, 'OPTIONS', 240, 40, '#a6ccff', 'c', 2); menu(ctx, U.items.options(), 90, 22, false); txt(ctx, 'LEFT / RIGHT CHANGES A VALUE', 240, 248, '#8ea2d2', 'c'); }
    else if (m === 'pause') { txt(ctx, 'PAUSED', 240, 66, '#a6ccff', 'c', 3); menu(ctx, U.items.pause(), 118, 28, true); }
    else if (m === 'end') ending(ctx, time, g);
  };
})((window.SGS = window.SGS || {}));
