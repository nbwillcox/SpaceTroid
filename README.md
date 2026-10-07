# SpaceTroid

A free, original, non-commercial exploration platformer in hand-authored hi-bit pixel art (480x270): five zones, upgrades that open the map, bosses and an escape. **Work in progress: all five zones (Crash Site, Cryo Vaults, Magma Forge, Drowned Reactor and Hive Core) are playable from the title screen: 92 rooms (including two-level caverns and 23 tiny item shrines), doors, save points, a serpentine world map with elevators, items, five bosses, a timed escape and three endings.**

The art is authored as palette-indexed character grids (see `tools/hero_gen.py` and `js/art/`), compiled to canvases at start-up; there are no image files. Preview the current art at `sheet.html`. Rooms are authored with a small terrain kit (`tools/room_kit.py`, one `tools/zoneN_gen.py` per zone, `tools/build_world.py` writes and places them) that carves caves from solid rock; each room's back wall is dressed with its own seeded mix of pillars, beams, panels, pipes, veins and glows (`js/walldeco.js`), and each zone has its own ambient particles (`js/atmos.js`).

## License and attribution

Licensed under [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/): free to play, share and remix **non-commercially**, as long as you give credit and **link back to this repository**: https://github.com/nbwillcox/SpaceTroid

This is an original game inspired by classic exploration platformers. It uses no assets, names or code from any existing game.

## Controls (engine test chamber)

| Action | Keyboard | Gamepad |
|---|---|---|
| Move | Arrows or WASD | Stick / d-pad |
| Aim | Mouse (free 360-degree aim with a reticle), or Up / Up + direction | Right stick (360 degrees), or d-pad Up |
| Jump (hold for height, again in air = space jump) | Space, Z or K | A |
| Fire (hold = auto-fire; infinite) | Left click, X or J | X / right trigger |
| Missile / super missile (limited; R swaps) | Right click, C or L | B / Y |
| Dash | Shift or V | right bumper |
| Aim lock | E | left bumper |
| Crouch, then Down again = morph ball (Fire lays a limited bomb) | S / Down | stick down |
| Down + Jump on a ledge | drops through | |
| Beam toggles | 1 / 2 / 3 | |

## More controls

| Action | Keyboard |
|---|---|
| Map | M or Tab |
| Pause | P or Esc |
| Save / use map terminal | stand on the pad and press Up |
| Menus | Up / Down, Left / Right to change values, Jump or Enter to select |

Doors: **blue** opens with any shot, **red** needs a missile, **green** a super missile, **gold** opens when the zone boss is beaten.

## Progress notes

Zone 1 gives you the morph ball, missiles and bombs (and the charge beam after its boss). Zone 2 adds ice floors, falling icicles, frost wisps you can freeze into stepping stones with the ice beam, and the heat suit. Zone 3 adds lava (wadeable with the heat suit), moving platforms, dash blocks and wave-crystal blocks, space jump, dash boots and the wave beam. Zone 4 floods the map: water, crushing pressure without the aqua suit, grapple anchors, electric arcs, the grapple beam and super missiles. Zone 5 adds hidden scan blocks (toggle the scan visor with F), the plasma beam, a three-phase final boss and a collapsing-base escape. The ending changes with how many items you found (under 50%, 50-89%, 90% and up).

The world is a serpentine: zone 1 runs east, its lift drops to zone 2, which runs west, and so on; the map screen draws the elevator shafts. Every zone also has side rooms and caverns under the floor that lead to extra tanks, sealed by shot blocks, bomb blocks, dash blocks, scan blocks or a grapple climb. Every item lives in its own shrine: the fourteen ability unlocks sit in the hands of big guardian statues, the thirty expansions on small ones, and picking one up plays a fanfare and a raised-arm victory pose. Pickups look like what they are (missiles, bombs, Mega Man style E-tanks) and so do enemy drops.

Extra controls: **Q** grapple (near a ceiling anchor), **F** toggle the scan visor.
