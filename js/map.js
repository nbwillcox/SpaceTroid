/* World map screen and the HUD minimap. Rooms cover 30x17-tile cells; visited rooms are lit, map-station rooms are outlined, doors and uncollected items are marked. */
(function (G) {
  'use strict';
  const PX = G.px, M = {};
  G.map = M;
  const DOOR = { blue: '#4cb0ff', red: '#ec5c4a', green: '#4cd2b8', boss: '#efba42', open: '#8ea2d2' };
  const zoneCol = ['#2b4fa4', '#2b4fa4'];
  const known = (g, id) => g.prog.visited[id] || g.prog.mapped[id];
  /* draw all known rooms at cell size cw x ch with origin (ox, oy); returns nothing */
  M.drawWorld = function (ctx, g, ox, oy, cw, ch, time, detail) {
    const cells = new Map();
    for (const id in G.rooms) { const d = G.rooms[id]; if (!known(g, id)) continue; for (const [x, y] of G.world.cells(d)) cells.set(x + ',' + y, id); }
    for (const [k, id] of cells) {
      const [x, y] = k.split(',').map(Number), vis = g.prog.visited[id], px = ox + x * cw, py = oy + y * ch;
      ctx.fillStyle = vis ? (id === g.roomId ? '#5688dc' : '#2b4fa4') : '#1b2c66'; ctx.fillRect(px, py, cw, ch);
      ctx.fillStyle = vis ? '#a6ccff' : '#2b4fa4';
      const same = (dx, dy) => cells.get((x + dx) + ',' + (y + dy)) === id;
      if (!same(0, -1)) ctx.fillRect(px, py, cw, 1); if (!same(0, 1)) ctx.fillRect(px, py + ch - 1, cw, 1);
      if (!same(-1, 0)) ctx.fillRect(px, py, 1, ch); if (!same(1, 0)) ctx.fillRect(px + cw - 1, py, 1, ch);
    }
    if (!detail) return;
    for (const id in G.rooms) {
      if (!known(g, id)) continue;
      const d = G.rooms[id], w = Math.ceil(d.map[0].length / 30) * cw, h = Math.ceil(d.map.length / 17) * ch, rx = ox + d.mx * cw, ry = oy + d.my * ch;
      for (const dr of d.doors || []) {
        if (dr.color === 'open') continue;
        const live = g.roomId === id && g.doors ? g.doors.find((q) => q.id === dr.id) : null;
        const col = dr.color === 'boss' && g.prog.flags.boss1 ? DOOR.blue : (g.prog.doors[id + ':' + dr.id] && dr.color !== 'boss' ? DOOR.blue : DOOR[dr.color]);
        const yy = ry + Math.round((dr.ty + 1) / d.map.length * h) - 2, xx = dr.side === 'L' ? rx - 1 : rx + w - 2;
        ctx.fillStyle = col; ctx.fillRect(xx, yy, 3, 5);
      }
      for (const it of d.items || []) if (!g.prog.items[it.id] && g.prog.mapped[id]) { ctx.fillStyle = Math.floor(time * 3) & 1 ? '#fff2a8' : '#efba42'; ctx.fillRect(rx + Math.round(it.tx / d.map[0].length * w) - 1, ry + Math.round(it.ty / d.map.length * h) - 1, 3, 3); }
      for (const s of d.stations || []) { ctx.fillStyle = s.type === 'save' ? '#86f0f2' : s.type === 'map' ? '#b878ff' : '#fff'; ctx.fillRect(rx + Math.round(s.tx / d.map[0].length * w) - 2, ry + Math.round(s.ty / d.map.length * h) - 2, 4, 4); }
    }
    const p = g.P, rd = g.room.def, cx = ox + (rd.mx + p.x / 16 / 30) * cw, cy = oy + (rd.my + (p.y - 8) / 16 / 17) * ch;
    if (Math.floor(time * 4) & 1) { ctx.fillStyle = '#fff'; ctx.fillRect(Math.round(cx) - 2, Math.round(cy) - 2, 5, 5); ctx.fillStyle = '#ec5c4a'; ctx.fillRect(Math.round(cx) - 1, Math.round(cy) - 1, 3, 3); }
  };
  M.drawScreen = function (ctx, g, time) {
    ctx.fillStyle = 'rgba(6,8,26,0.94)'; ctx.fillRect(0, 0, 480, 270);
    PX.text(ctx, 'MAP', 240, 14, { s: 2, c: '#a6ccff', o: '#0a0e2c', a: 'c' });
    const cw = 26, ch = 20, ox = Math.round((480 - 17 * cw) / 2), oy = 60;
    ctx.fillStyle = '#10142e'; ctx.fillRect(ox - 4, oy - 4, 17 * cw + 8, 3 * ch + 8);
    M.drawWorld(ctx, g, ox, oy, cw, ch, time, true);
    const n = Object.keys(g.prog.items).length, tot = G.world.itemTotal();
    PX.text(ctx, 'ITEMS ' + n + '/' + tot, 240, 150, { s: 1, c: '#efba42', o: '#0a0e2c', a: 'c' });
    const lg = [['BLUE', DOOR.blue, 'SHOT'], ['RED', DOOR.red, 'MISSILE'], ['GREEN', DOOR.green, 'SUPER'], ['GOLD', DOOR.boss, 'BOSS KEY']];
    lg.forEach((l, i) => { ctx.fillStyle = l[1]; ctx.fillRect(98 + i * 78, 175, 5, 8); PX.text(ctx, l[2], 108 + i * 78, 176, { s: 1, c: '#c8d4f0', o: '#0a0e2c' }); });
    ctx.fillStyle = '#86f0f2'; ctx.fillRect(110, 198, 4, 4); PX.text(ctx, 'SAVE', 120, 197, { s: 1, c: '#c8d4f0', o: '#0a0e2c' });
    ctx.fillStyle = '#b878ff'; ctx.fillRect(170, 198, 4, 4); PX.text(ctx, 'MAP', 180, 197, { s: 1, c: '#c8d4f0', o: '#0a0e2c' });
    ctx.fillStyle = '#efba42'; ctx.fillRect(220, 198, 3, 3); PX.text(ctx, 'ITEM (MAPPED ROOMS)', 230, 197, { s: 1, c: '#c8d4f0', o: '#0a0e2c' });
    PX.text(ctx, 'M OR ESC: CLOSE', 240, 246, { s: 1, c: '#8ea2d2', o: '#0a0e2c', a: 'c' });
  };
  /* minimap in the top-right corner: a window of cells around the current one */
  M.mini = function (ctx, g, time) {
    const rd = g.room.def, p = g.P, cx = Math.floor(rd.mx + p.x / 16 / 30), cy = Math.floor(rd.my + p.y / 16 / 17), cw = 9, ch = 7, W = 7, H = 5, ox = 480 - 4 - W * cw, oy = 4;
    ctx.fillStyle = 'rgba(10,14,44,0.6)'; ctx.fillRect(ox - 2, oy - 2, W * cw + 4, H * ch + 4);
    ctx.save(); ctx.beginPath(); ctx.rect(ox, oy, W * cw, H * ch); ctx.clip();
    M.drawWorld(ctx, g, ox - (cx - 3) * cw, oy - (cy - 2) * ch, cw, ch, time, false);
    if (Math.floor(time * 3) & 1) { ctx.fillStyle = '#fff'; ctx.fillRect(ox + 3 * cw + 3, oy + 2 * ch + 2, 3, 3); }
    ctx.restore();
  };
})((window.SGS = window.SGS || {}));
