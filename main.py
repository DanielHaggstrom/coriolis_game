import pygame
import math

# inicializar pygame
pygame.init()

# configuración de la pantalla
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Projectile Launcher in Rotating Cylinder")

# colores y constantes visuales
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# propiedades del cilindro
CYLINDER_RADIUS = 300
CYLINDER_THICKNESS = 20
CYLINDER_CENTER = (WIDTH // 2, HEIGHT // 2)
OMEGA = 0.1
MAX_DRAG_DISTANCE = 150
VELOCITY_SCALE = 10  # Adjustable speed scaling factor


# clase Slider para controlar la velocidad de rotación
class Slider:
    def __init__(self, x, y, w, min_val, max_val, start_val):
        self.x = x
        self.y = y
        self.w = w
        self.h = 20
        self.min_val = min_val
        self.max_val = max_val
        self.value = start_val
        self.slider_x = self.x + (self.value - self.min_val) / (self.max_val - self.min_val) * self.w
        self.dragging = False

    def draw(self, screen):
        pygame.draw.line(screen, BLACK, (self.x, self.y), (self.x + self.w, self.y), 5)
        pygame.draw.circle(screen, RED, (int(self.slider_x), self.y), 10)
        font = pygame.font.SysFont(None, 24)
        text = font.render(f'Omega: {self.value:.2f}', True, BLACK)
        screen.blit(text, (self.x + self.w + 20, self.y - 12))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_over_slider(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self.update_value(event.pos[0])

    def is_over_slider(self, pos):
        return abs(pos[0] - self.slider_x) <= 10 and abs(pos[1] - self.y) <= 10

    def update_value(self, mouse_x):
        self.slider_x = min(max(self.x, mouse_x), self.x + self.w)
        self.value = self.min_val + (self.slider_x - self.x) / self.w * (self.max_val - self.min_val)


# physics functions for projectiles
def calculate_velocity(start_pos, end_pos, velocity_scale=VELOCITY_SCALE):
    """Calculate the initial velocity based on the drag distance."""
    dx = start_pos[0] - end_pos[0]
    dy = start_pos[1] - end_pos[1]
    drag_distance = math.sqrt(dx ** 2 + dy ** 2)
    if drag_distance > MAX_DRAG_DISTANCE:
        scale = MAX_DRAG_DISTANCE / drag_distance
        dx *= scale
        dy *= scale
    velocity = (dx / velocity_scale, dy / velocity_scale)
    return velocity


def apply_coriolis_and_centrifugal(projectile, omega):
    """Apply Coriolis and centrifugal forces to the projectile."""
    vx, vy = projectile["velocity"]
    x, y = projectile["pos"]
    relative_x = x - CYLINDER_CENTER[0]
    relative_y = y - CYLINDER_CENTER[1]

    coriolis_force_x = 2 * omega * vy
    coriolis_force_y = -2 * omega * vx
    centrifugal_force_x = omega ** 2 * relative_x
    centrifugal_force_y = omega ** 2 * relative_y

    projectile["velocity"][0] += coriolis_force_x + centrifugal_force_x
    projectile["velocity"][1] += coriolis_force_y + centrifugal_force_y


def inside_cylinder(pos):
    """Check if a position is inside the cylinder."""
    dx = pos[0] - CYLINDER_CENTER[0]
    dy = pos[1] - CYLINDER_CENTER[1]
    distance = math.sqrt(dx ** 2 + dy ** 2)
    return distance <= CYLINDER_RADIUS


def hit_cylinder_boundary(pos):
    """Check if a position has hit the boundary of the cylinder."""
    dx = pos[0] - CYLINDER_CENTER[0]
    dy = pos[1] - CYLINDER_CENTER[1]
    distance = math.sqrt(dx ** 2 + dy ** 2)
    return CYLINDER_RADIUS - CYLINDER_THICKNESS / 2 <= distance <= CYLINDER_RADIUS + CYLINDER_THICKNESS / 2


# drawing functions for the game
def draw_cylinder_and_crosshairs():
    """Draw the cylinder and crosshairs at the center."""
    pygame.draw.circle(screen, BLACK, CYLINDER_CENTER, CYLINDER_RADIUS + CYLINDER_THICKNESS // 2, CYLINDER_THICKNESS)
    pygame.draw.line(screen, BLACK, (CYLINDER_CENTER[0] - 10, CYLINDER_CENTER[1]), (CYLINDER_CENTER[0] + 10, CYLINDER_CENTER[1]), 2)
    pygame.draw.line(screen, BLACK, (CYLINDER_CENTER[0], CYLINDER_CENTER[1] - 10), (CYLINDER_CENTER[0], CYLINDER_CENTER[1] + 10), 2)


def draw_speed_box(screen, start_pos, velocity, omega):
    """Draw a box showing the speed ratio."""
    vx, vy = velocity
    x, y = start_pos
    distance_to_center = math.sqrt((x - CYLINDER_CENTER[0]) ** 2 + (y - CYLINDER_CENTER[1]) ** 2)
    rotating_speed = omega * distance_to_center
    launch_speed = math.sqrt(vx ** 2 + vy ** 2)
    speed_ratio = launch_speed / rotating_speed if rotating_speed != 0 else float('inf')

    font = pygame.font.SysFont(None, 24)
    text = font.render(f'Speed Ratio: {speed_ratio:.2f}', True, BLACK)
    box_width, box_height = text.get_size()
    box_x = start_pos[0] + 10
    box_y = start_pos[1] - box_height - 10
    pygame.draw.rect(screen, GREEN, (box_x, box_y, box_width + 10, box_height + 10))
    screen.blit(text, (box_x + 5, box_y + 5))


def draw_rotation_arrows():
    """Draw arrows around the cylinder indicating the direction of rotation."""
    arrow_length = 30
    arrow_angle = 20
    num_arrows = 8

    for i in range(num_arrows):
        angle = (2 * math.pi / num_arrows) * i
        start_pos = (
            CYLINDER_CENTER[0] + (CYLINDER_RADIUS + CYLINDER_THICKNESS // 2 + 10) * math.cos(angle),
            CYLINDER_CENTER[1] + (CYLINDER_RADIUS + CYLINDER_THICKNESS // 2 + 10) * math.sin(angle),
        )
        direction_angle = angle + math.pi / 2
        end_pos = (
            start_pos[0] + arrow_length * math.cos(direction_angle),
            start_pos[1] + arrow_length * math.sin(direction_angle),
        )
        pygame.draw.line(screen, BLACK, start_pos, end_pos, 2)

        left_wing = (
            end_pos[0] - arrow_length / 2 * math.cos(direction_angle - math.radians(arrow_angle)),
            end_pos[1] - arrow_length / 2 * math.sin(direction_angle - math.radians(arrow_angle)),
        )
        right_wing = (
            end_pos[0] - arrow_length / 2 * math.cos(direction_angle + math.radians(arrow_angle)),
            end_pos[1] - arrow_length / 2 * math.sin(direction_angle + math.radians(arrow_angle)),
        )
        pygame.draw.line(screen, BLACK, end_pos, left_wing, 2)
        pygame.draw.line(screen, BLACK, end_pos, right_wing, 2)


# game loop
omega_slider = Slider(50, HEIGHT - 50, 300, 0.01, 2.0, OMEGA)
projectiles = []
dragging = False
start_pos = (0, 0)

running = True
while running:
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        omega_slider.handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                start_pos = pygame.mouse.get_pos()
                if inside_cylinder(start_pos):
                    dragging = True
                else:
                    dragging = False
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and dragging:
                dragging = False
                end_pos = pygame.mouse.get_pos()
                velocity = calculate_velocity(start_pos, end_pos)
                if inside_cylinder(start_pos):
                    projectiles.append({
                        "pos": list(start_pos),
                        "velocity": list(velocity)
                    })
                    if len(projectiles) > 5:
                        projectiles.pop(0)

    if dragging:
        end_pos = pygame.mouse.get_pos()
        limited_end_pos = (start_pos[0] - limited_drag[0], start_pos[1] - limited_drag[1])
        limited_velocity = calculate_velocity(start_pos, end_pos)
        limited_end_pos = (start_pos[0] - limited_velocity[0] * VELOCITY_SCALE, start_pos[1] - limited_velocity[1] * VELOCITY_SCALE)
        pygame.draw.line(screen, RED, start_pos, limited_end_pos, 2)

    for projectile in projectiles:
        if not hit_cylinder_boundary(projectile["pos"]):
            apply_coriolis_and_centrifugal(projectile, OMEGA)
            projectile["pos"][0] += projectile["velocity"][0]
            projectile["pos"][1] += projectile["velocity"][1]
            if not inside_cylinder(projectile["pos"]):
                projectiles.remove(projectile)
        else:
            projectile["velocity"] = [0, 0]

        pygame.draw.circle(screen, BLUE, (int(projectile["pos"][0]), int(projectile["pos"][1])), 5)

    draw_cylinder_and_crosshairs()
    draw_rotation_arrows()

    if dragging:
        draw_speed_box(screen, start_pos, limited_velocity, OMEGA)

    omega_slider.draw(screen)

    pygame.display.flip()
    pygame.time.Clock().tick(60)

pygame.quit()
