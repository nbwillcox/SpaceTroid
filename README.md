# SpaceTroid

A free, original, non-commercial exploration platformer in hand-authored hi-bit pixel art (480x270): five zones, upgrades that open the map, bosses and an escape. **Work in progress.**

The art is authored as palette-indexed character grids (see `tools/hero_gen.py` and `js/art/`), compiled to canvases at start-up; there are no image files. Preview the current art at `sheet.html`.

## License and attribution

Licensed under [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/): free to play, share and remix **non-commercially**, as long as you give credit and **link back to this repository**: https://github.com/nbwillcox/SpaceTroid

This is an original game inspired by classic exploration platformers. It uses no assets, names or code from any existing game.

## Controls (engine test chamber)

| Action | Keyboard | Gamepad |
|---|---|---|
| Move | Arrows or WASD | Stick / d-pad |
| Aim | Mouse (while you use it), or Up / Up + direction | Up / Up + direction |
| Jump (hold for height, again in air = space jump) | Space, Z or K | A |
| Fire (hold = auto-fire; infinite) | Left click, X or J | X / right trigger |
| Missile / super missile (limited; R swaps) | Right click, C or L | B / Y |
| Dash | Shift or V | right bumper |
| Aim lock | E | left bumper |
| Crouch, then Down again = morph ball (Fire lays a limited bomb) | S / Down | stick down |
| Down + Jump on a ledge | drops through | |
| Beam toggles | 1 / 2 / 3 | |
