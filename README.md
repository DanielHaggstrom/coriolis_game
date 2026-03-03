# Coriolis Game

Coriolis Game is a small pygame simulation that lets you launch projectiles inside a rotating cylinder and observe how Coriolis and centrifugal terms bend their paths in a rotating reference frame.

## Status

The project has been cleaned up into a small Python package with:

- a stable pygame entrypoint
- isolated physics helpers with automated tests
- packaging metadata for installation
- clearer documentation and license attribution

## Requirements

- Python 3.10 or newer
- `pygame` 2.6 or newer

## Installation

```powershell
py -3 -m pip install .
```

## Run

```powershell
py -3 main.py
```

You can also run the installed console script:

```powershell
coriolis-game
```

## Controls

- Left click and drag inside the cylinder to launch a projectile.
- Drag the slider at the bottom of the window to change the angular velocity.
- Close the window to exit.

## Development

Run the unit tests:

```powershell
py -3 -m unittest discover -s tests -v
```

Validate the source tree:

```powershell
py -3 -m py_compile main.py coriolis_game\\app.py coriolis_game\\physics.py coriolis_game\\settings.py
```

## Project Layout

- `main.py`: local entrypoint for running from the repository root
- `coriolis_game/app.py`: pygame runtime and drawing code
- `coriolis_game/physics.py`: pure simulation helpers
- `coriolis_game/settings.py`: shared constants
- `tests/test_physics.py`: regression coverage for the physics layer

## License

Copyright (C) 2024-2026 Daniel Häggström.

This project is distributed under the GNU General Public License v3. See `LICENSE` and `NOTICE` for details.
