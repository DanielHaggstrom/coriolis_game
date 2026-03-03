"""Application settings shared across the project."""

from typing import Final

WINDOW_WIDTH: Final = 1200
WINDOW_HEIGHT: Final = 800
WINDOW_SIZE: Final = (WINDOW_WIDTH, WINDOW_HEIGHT)
WINDOW_TITLE: Final = "Projectile Launcher in Rotating Cylinder"
FPS: Final = 60

WHITE: Final = (255, 255, 255)
BLACK: Final = (0, 0, 0)
RED: Final = (255, 0, 0)
BLUE: Final = (0, 0, 255)
GREEN: Final = (0, 255, 0)

CYLINDER_RADIUS: Final = 300
CYLINDER_THICKNESS: Final = 20
CYLINDER_CENTER: Final = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)

DEFAULT_OMEGA: Final = 0.1
MIN_OMEGA: Final = 0.0
MAX_OMEGA: Final = 0.5

MAX_DRAG_DISTANCE: Final = 150.0
VELOCITY_SCALE: Final = 10.0
MAX_PROJECTILES: Final = 5
PROJECTILE_RADIUS: Final = 5

SLIDER_X: Final = 50
SLIDER_Y: Final = WINDOW_HEIGHT - 50
SLIDER_WIDTH: Final = 300
