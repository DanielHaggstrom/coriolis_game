"""Pure physics helpers for the rotating-cylinder simulation."""

from __future__ import annotations

from dataclasses import dataclass
import math

Point = tuple[float, float]
Vector = tuple[float, float]


@dataclass(slots=True)
class Projectile:
    """Mutable projectile state used by the runtime loop."""

    position: list[float]
    velocity: list[float]

    @classmethod
    def from_launch(cls, position: Point, velocity: Vector) -> "Projectile":
        return cls(
            position=[float(position[0]), float(position[1])],
            velocity=[float(velocity[0]), float(velocity[1])],
        )


def calculate_velocity(
    start_pos: Point,
    end_pos: Point,
    *,
    max_drag_distance: float,
    velocity_scale: float,
) -> Vector:
    """Calculate a capped launch velocity from the mouse drag vector."""

    dx = start_pos[0] - end_pos[0]
    dy = start_pos[1] - end_pos[1]
    drag_distance = math.hypot(dx, dy)

    if drag_distance > max_drag_distance and drag_distance > 0:
        scale = max_drag_distance / drag_distance
        dx *= scale
        dy *= scale

    return (dx / velocity_scale, dy / velocity_scale)


def apply_coriolis_and_centrifugal(
    projectile: Projectile,
    *,
    omega: float,
    cylinder_center: Point,
) -> None:
    """Mutate projectile velocity by applying the rotating-frame forces."""

    vx, vy = projectile.velocity
    x, y = projectile.position
    relative_x = x - cylinder_center[0]
    relative_y = y - cylinder_center[1]

    coriolis_force_x = 2 * omega * vy
    coriolis_force_y = -2 * omega * vx
    centrifugal_force_x = omega**2 * relative_x
    centrifugal_force_y = omega**2 * relative_y

    projectile.velocity[0] += coriolis_force_x + centrifugal_force_x
    projectile.velocity[1] += coriolis_force_y + centrifugal_force_y


def inside_cylinder(position: Point, *, cylinder_center: Point, radius: float) -> bool:
    """Return whether a point lies within the cylinder radius."""

    dx = position[0] - cylinder_center[0]
    dy = position[1] - cylinder_center[1]
    return math.hypot(dx, dy) <= radius


def hit_cylinder_boundary(
    position: Point,
    *,
    cylinder_center: Point,
    radius: float,
    thickness: float,
) -> bool:
    """Return whether a point lies inside the boundary ring."""

    dx = position[0] - cylinder_center[0]
    dy = position[1] - cylinder_center[1]
    distance = math.hypot(dx, dy)
    return radius - thickness / 2 <= distance <= radius + thickness / 2


def calculate_speed_ratio(
    position: Point,
    velocity: Vector,
    *,
    cylinder_center: Point,
    omega: float,
) -> float:
    """Return launch speed divided by the surface speed at the launch point."""

    distance_to_center = math.hypot(
        position[0] - cylinder_center[0],
        position[1] - cylinder_center[1],
    )
    rotating_speed = omega * distance_to_center
    launch_speed = math.hypot(velocity[0], velocity[1])

    if rotating_speed == 0:
        return float("inf")

    return launch_speed / rotating_speed
