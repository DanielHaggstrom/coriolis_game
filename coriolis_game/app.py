"""Pygame runtime for the Coriolis Game project."""

from __future__ import annotations

import math

import pygame

from coriolis_game.physics import (
    Projectile,
    apply_coriolis_and_centrifugal,
    calculate_speed_ratio,
    calculate_velocity,
    hit_cylinder_boundary,
    inside_cylinder,
)
from coriolis_game.settings import (
    BLACK,
    BLUE,
    CYLINDER_CENTER,
    CYLINDER_RADIUS,
    CYLINDER_THICKNESS,
    DEFAULT_OMEGA,
    FPS,
    GREEN,
    MAX_DRAG_DISTANCE,
    MAX_OMEGA,
    MAX_PROJECTILES,
    MIN_OMEGA,
    PROJECTILE_RADIUS,
    RED,
    SLIDER_WIDTH,
    SLIDER_X,
    SLIDER_Y,
    VELOCITY_SCALE,
    WHITE,
    WINDOW_SIZE,
    WINDOW_TITLE,
)


class Slider:
    """Simple horizontal slider used to adjust the angular velocity."""

    def __init__(self, x: int, y: int, width: int, min_value: float, max_value: float, value: float) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.min_value = min_value
        self.max_value = max_value
        self.value = value
        self.knob_radius = 10
        self.knob_x = self._value_to_x(value)
        self.dragging = False

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        pygame.draw.line(surface, BLACK, (self.x, self.y), (self.x + self.width, self.y), 5)
        pygame.draw.circle(surface, RED, (int(self.knob_x), self.y), self.knob_radius)
        label = font.render(f"Omega: {self.value:.2f}", True, BLACK)
        surface.blit(label, (self.x + self.width + 20, self.y - 12))

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_over_knob(event.pos):
            self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.update_value(event.pos[0])

    def is_over_knob(self, position: tuple[int, int]) -> bool:
        return abs(position[0] - self.knob_x) <= self.knob_radius and abs(position[1] - self.y) <= self.knob_radius

    def update_value(self, mouse_x: int) -> None:
        self.knob_x = min(max(self.x, mouse_x), self.x + self.width)
        slider_fraction = (self.knob_x - self.x) / self.width
        self.value = self.min_value + slider_fraction * (self.max_value - self.min_value)

    def _value_to_x(self, value: float) -> float:
        slider_fraction = (value - self.min_value) / (self.max_value - self.min_value)
        return self.x + slider_fraction * self.width


class CoriolisGame:
    """Runtime container for simulation state and drawing code."""

    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption(WINDOW_TITLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.omega_slider = Slider(SLIDER_X, SLIDER_Y, SLIDER_WIDTH, MIN_OMEGA, MAX_OMEGA, DEFAULT_OMEGA)
        self.projectiles: list[Projectile] = []
        self.launch_origin: tuple[int, int] | None = None

    def run(self) -> int:
        try:
            running = True
            while running:
                running = self.handle_events()
                self.update_projectiles()
                self.draw()
                pygame.display.flip()
                self.clock.tick(FPS)

            return 0
        finally:
            pygame.quit()

    def handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            self.omega_slider.handle_event(event)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if inside_cylinder(event.pos, cylinder_center=CYLINDER_CENTER, radius=CYLINDER_RADIUS):
                    self.launch_origin = event.pos
                else:
                    self.launch_origin = None

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.launch_origin is not None:
                    velocity = calculate_velocity(
                        self.launch_origin,
                        event.pos,
                        max_drag_distance=MAX_DRAG_DISTANCE,
                        velocity_scale=VELOCITY_SCALE,
                    )
                    self.projectiles.append(Projectile.from_launch(self.launch_origin, velocity))
                    if len(self.projectiles) > MAX_PROJECTILES:
                        self.projectiles.pop(0)

                self.launch_origin = None

        return True

    def update_projectiles(self) -> None:
        omega = self.omega_slider.value
        remaining_projectiles: list[Projectile] = []

        for projectile in self.projectiles:
            if hit_cylinder_boundary(
                tuple(projectile.position),
                cylinder_center=CYLINDER_CENTER,
                radius=CYLINDER_RADIUS,
                thickness=CYLINDER_THICKNESS,
            ):
                projectile.velocity[0] = 0.0
                projectile.velocity[1] = 0.0
                remaining_projectiles.append(projectile)
                continue

            apply_coriolis_and_centrifugal(
                projectile,
                omega=omega,
                cylinder_center=CYLINDER_CENTER,
            )
            projectile.position[0] += projectile.velocity[0]
            projectile.position[1] += projectile.velocity[1]

            if inside_cylinder(
                tuple(projectile.position),
                cylinder_center=CYLINDER_CENTER,
                radius=CYLINDER_RADIUS,
            ):
                remaining_projectiles.append(projectile)

        self.projectiles = remaining_projectiles

    def draw(self) -> None:
        self.screen.fill(WHITE)
        self.draw_cylinder_and_crosshairs()
        self.draw_rotation_arrows()

        if self.launch_origin is not None:
            preview_velocity = calculate_velocity(
                self.launch_origin,
                pygame.mouse.get_pos(),
                max_drag_distance=MAX_DRAG_DISTANCE,
                velocity_scale=VELOCITY_SCALE,
            )
            preview_end_pos = (
                self.launch_origin[0] - preview_velocity[0] * VELOCITY_SCALE,
                self.launch_origin[1] - preview_velocity[1] * VELOCITY_SCALE,
            )
            pygame.draw.line(self.screen, RED, self.launch_origin, preview_end_pos, 2)
            self.draw_speed_box(self.launch_origin, preview_velocity)

        for projectile in self.projectiles:
            pygame.draw.circle(
                self.screen,
                BLUE,
                (int(projectile.position[0]), int(projectile.position[1])),
                PROJECTILE_RADIUS,
            )

        self.omega_slider.draw(self.screen, self.font)

    def draw_cylinder_and_crosshairs(self) -> None:
        pygame.draw.circle(
            self.screen,
            BLACK,
            CYLINDER_CENTER,
            CYLINDER_RADIUS + CYLINDER_THICKNESS // 2,
            CYLINDER_THICKNESS,
        )
        pygame.draw.line(
            self.screen,
            BLACK,
            (CYLINDER_CENTER[0] - 10, CYLINDER_CENTER[1]),
            (CYLINDER_CENTER[0] + 10, CYLINDER_CENTER[1]),
            2,
        )
        pygame.draw.line(
            self.screen,
            BLACK,
            (CYLINDER_CENTER[0], CYLINDER_CENTER[1] - 10),
            (CYLINDER_CENTER[0], CYLINDER_CENTER[1] + 10),
            2,
        )

    def draw_speed_box(self, start_pos: tuple[int, int], velocity: tuple[float, float]) -> None:
        speed_ratio = calculate_speed_ratio(
            start_pos,
            velocity,
            cylinder_center=CYLINDER_CENTER,
            omega=self.omega_slider.value,
        )
        label = self.font.render(f"Speed Ratio: {speed_ratio:.2f}", True, BLACK)
        box_width, box_height = label.get_size()
        box_x = start_pos[0] + 10
        box_y = start_pos[1] - box_height - 10
        pygame.draw.rect(self.screen, GREEN, (box_x, box_y, box_width + 10, box_height + 10))
        self.screen.blit(label, (box_x + 5, box_y + 5))

    def draw_rotation_arrows(self) -> None:
        arrow_length = 30
        arrow_angle = 20
        num_arrows = 8

        for index in range(num_arrows):
            angle = (2 * math.pi / num_arrows) * index
            start_pos = (
                CYLINDER_CENTER[0] + (CYLINDER_RADIUS + CYLINDER_THICKNESS // 2 + 10) * math.cos(angle),
                CYLINDER_CENTER[1] + (CYLINDER_RADIUS + CYLINDER_THICKNESS // 2 + 10) * math.sin(angle),
            )
            direction_angle = angle + math.pi / 2
            end_pos = (
                start_pos[0] + arrow_length * math.cos(direction_angle),
                start_pos[1] + arrow_length * math.sin(direction_angle),
            )
            pygame.draw.line(self.screen, BLACK, start_pos, end_pos, 2)

            left_wing = (
                end_pos[0] - arrow_length / 2 * math.cos(direction_angle - math.radians(arrow_angle)),
                end_pos[1] - arrow_length / 2 * math.sin(direction_angle - math.radians(arrow_angle)),
            )
            right_wing = (
                end_pos[0] - arrow_length / 2 * math.cos(direction_angle + math.radians(arrow_angle)),
                end_pos[1] - arrow_length / 2 * math.sin(direction_angle + math.radians(arrow_angle)),
            )
            pygame.draw.line(self.screen, BLACK, end_pos, left_wing, 2)
            pygame.draw.line(self.screen, BLACK, end_pos, right_wing, 2)


def main() -> int:
    """Launch the pygame application."""

    game = CoriolisGame()
    return game.run()
