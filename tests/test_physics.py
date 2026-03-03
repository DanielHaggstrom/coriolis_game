import math
import unittest

from coriolis_game.physics import (
    Projectile,
    apply_coriolis_and_centrifugal,
    calculate_speed_ratio,
    calculate_velocity,
    hit_cylinder_boundary,
    inside_cylinder,
)


class PhysicsTests(unittest.TestCase):
    def test_calculate_velocity_caps_drag_distance(self) -> None:
        velocity = calculate_velocity(
            (0.0, 0.0),
            (-300.0, 0.0),
            max_drag_distance=150.0,
            velocity_scale=10.0,
        )

        self.assertEqual(velocity, (15.0, 0.0))

    def test_apply_coriolis_and_centrifugal_updates_velocity(self) -> None:
        projectile = Projectile(position=[700.0, 400.0], velocity=[5.0, -2.0])

        apply_coriolis_and_centrifugal(
            projectile,
            omega=0.1,
            cylinder_center=(600.0, 400.0),
        )

        self.assertAlmostEqual(projectile.velocity[0], 5.6)
        self.assertAlmostEqual(projectile.velocity[1], -3.0)

    def test_inside_cylinder_checks_radius(self) -> None:
        self.assertTrue(inside_cylinder((650.0, 400.0), cylinder_center=(600.0, 400.0), radius=60.0))
        self.assertFalse(inside_cylinder((700.0, 400.0), cylinder_center=(600.0, 400.0), radius=60.0))

    def test_hit_cylinder_boundary_detects_ring(self) -> None:
        self.assertTrue(
            hit_cylinder_boundary(
                (890.0, 400.0),
                cylinder_center=(600.0, 400.0),
                radius=300.0,
                thickness=20.0,
            )
        )
        self.assertFalse(
            hit_cylinder_boundary(
                (850.0, 400.0),
                cylinder_center=(600.0, 400.0),
                radius=300.0,
                thickness=20.0,
            )
        )

    def test_speed_ratio_is_infinite_when_rotation_speed_is_zero(self) -> None:
        ratio = calculate_speed_ratio(
            (600.0, 400.0),
            (4.0, 3.0),
            cylinder_center=(600.0, 400.0),
            omega=0.2,
        )

        self.assertTrue(math.isinf(ratio))


if __name__ == "__main__":
    unittest.main()
