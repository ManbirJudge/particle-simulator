import math
import random
from typing import Tuple, List, Dict

import pygame
import pygame_gui
from pygame import gfxdraw
from pygame_gui import UIManager, elements as ui_elements

pygame.init()
pygame.font.init()

pygame.display.set_caption('Particle Simulator | by Manbir Judge')

WIDTH = 800
HEIGHT = 800
BG_COLOR = (27, 36, 48)
FPS = 120
FONTS = pygame.font.get_fonts()
PPM = 1

CHARGE_COLOR_NEG = (255, 51, 51)
CHARGE_COLOR_POS = (91, 192, 222)

k = 1
G = 6.67430 * (10 ** -11)
BOUNCE_SLOWDOWN_FACTOR = 0.8


class Colors:
    WHITE = (255, 255, 255)
    BLACK = (255, 255, 255)

    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)

    YELLOW = (255, 255, 0)
    PURPLE = (255, 0, 255)
    CYAN = (0, 255, 255)


class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __getitem__(self, arg) -> float:
        if type(arg) != int:
            return 0

        if arg == 0:
            return self.x
        elif arg == 1:
            return self.y
        else:
            return 0

    def __str__(self):
        return f'Point({self.x}, {self.y})'

    def to_tuple(self) -> Tuple[float, float]:
        return self.x, self.y

    def to_list(self) -> List[float]:
        return [self.x, self.y]

    def to_dict(self) -> Dict[str, float]:
        return {
            'x': self.x,
            'y': self.y
        }

    def to_vector(self) -> 'Vector':
        return Vector(self.x, self.y)

    @staticmethod
    def from_tuple(obj: Tuple[int, int]) -> 'Point':
        return Point(obj[0], obj[1])


class Vector:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __add__(self, other):
        if type(other) == Vector:
            return Vector(self.x + other.x, self.y + other.y)
        else:
            raise Exception('Error while adding vectors.')

    def __sub__(self, other):
        if type(other) == Vector:
            return Vector(self.x - other.x, self.y - other.y)
        else:
            raise Exception('Error while subtracting vectors.')

    def __mul__(self, other):
        if type(other) == float or type(other) == int:
            return Vector(self.x * other, self.y * other)

        else:
            raise Exception('Error while dividing a vector.')

    def __truediv__(self, other):
        if type(other) == float or type(other) == int:
            return Vector(self.x / other, self.y / other)

        else:
            raise Exception('Error while dividing a vector.')

    def __neg__(self):
        return Vector(-self.x, -self.y)

    def __str__(self) -> str:
        return f'Vector(x={self.x}, y={self.y})'

    def to_point(self) -> Point:
        return Point(self.x, self.y)


class Particle:
    def __init__(self, charge: int, mass: float, pos: Point, vel: Vector = Vector(0, 0)):
        self.charge = charge
        self.mass = mass
        self.pos = pos
        self.vel = vel

    def __add__(self, other) -> float:
        if type(other) == Particle:
            return self.charge + other.charge
        else:
            return self.charge + other

    def __mul__(self, other) -> float:
        if type(other) == Particle:
            return self.charge * other.charge
        else:
            return self.charge * other


def distance(p1: Point, p2: Point) -> float:
    return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)


def random_point() -> Point:
    return Point(
        random.randint(0, WIDTH),
        random.randint(0, HEIGHT)
    )


def time_ms_to_str(ms: int) -> str:
    s = ms / 1000

    return f'{s:.2f} s'


PRESETS = [
    [
        Particle(-5, 1, Point(WIDTH / 4, HEIGHT / 2)),
        Particle(5, 1, Point(WIDTH / 2, HEIGHT / 2)),
        Particle(-5, 1, Point(WIDTH * 3 / 4, HEIGHT / 2)),
    ],
    [
        Particle(-5, 1, Point(WIDTH / 4, HEIGHT / 4)),
        Particle(5, 1, Point(WIDTH / 2, HEIGHT / 2)),
        Particle(-5, 1, Point(WIDTH * 3 / 4, HEIGHT / 4)),
    ],
    [
        Particle(-15, 0.1, Point(0, 0), Vector(30, 22)),
        Particle(15, 1, Point(WIDTH / 2, HEIGHT / 2)),
    ],
    [
        Particle(0, 1, Point(10, (HEIGHT / 2) - 10), Vector(100, 0)),
        Particle(0, 1, Point(10, (HEIGHT / 2) - 20), Vector(100, 0)),
        Particle(0, 1, Point(10, (HEIGHT / 2) - 30), Vector(100, 0)),
        Particle(0, 1, Point(10, (HEIGHT / 2) - 40), Vector(100, 0)),
        Particle(0, 1, Point(10, (HEIGHT / 2) - 50), Vector(100, 0)),
        Particle(0, 10 ** 13, Point(WIDTH * 1 / 2, HEIGHT / 2)),
        # Particle(0, 1, Point(10, (HEIGHT / 2) + 10), Vector(100, 0)),
        # Particle(0, 1, Point(10, (HEIGHT / 2) + 20), Vector(100, 0)),
        # Particle(0, 1, Point(10, (HEIGHT / 2) + 30), Vector(100, 0)),
        # Particle(0, 1, Point(10, (HEIGHT / 2) + 40), Vector(100, 0)),
        # Particle(0, 1, Point(10, (HEIGHT / 2) + 50), Vector(100, 0)),
    ],
    [
        Particle(0, 1, random_point(), Vector(0, 0)),
        Particle(-5, 1, random_point()),
        Particle(5, 1, random_point()),
        Particle(5, 1, random_point()),
    ]
]

if __name__ == '__main__':
    # game vars
    run = True

    screen = pygame.display.set_mode(size=(WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    delta_t = 0

    up_pressed = False
    down_pressed = False

    # fonts
    main_font = pygame.font.SysFont('JetBrains Mono', 15)
    small_font = pygame.font.SysFont('JetBrains Mono', 10)

    # ui
    ui_manager = UIManager((WIDTH, HEIGHT))

    particle_radius_slider = ui_elements.UIHorizontalSlider(
        relative_rect=pygame.Rect((550, 0), (250, 20)),
        start_value=4,
        value_range=(1, 10),
        manager=ui_manager,
        click_increment=2
    )
    sim_speed_slider = ui_elements.UIHorizontalSlider(
        relative_rect=pygame.Rect((550, 40), (250, 20)),
        start_value=2,
        value_range=(1, 100),
        manager=ui_manager,
        click_increment=2
    )

    # required vars
    particles = PRESETS[-1]
    total_time_passed = 0
    selected_particle_i = None

    # configurable vars
    particle_radius = 4
    labels = False
    sim_speed = 2
    paused = False

    # mainloop
    while run:
        # bg
        screen.fill(BG_COLOR)

        # time
        delta_t = clock.get_time()
        sim_delta_t = delta_t * sim_speed

        # events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused

                if event.key == pygame.K_UP:
                    up_pressed = True

                if event.key == pygame.K_DOWN:
                    down_pressed = True

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    up_pressed = False

                if event.key == pygame.K_DOWN:
                    down_pressed = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = Point.from_tuple(pygame.mouse.get_pos())

                for i, p in enumerate(particles):
                    if distance(mouse_pos, p.pos) < particle_radius:
                        selected_particle_i = i
                        break

            elif event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                if event.ui_element == particle_radius_slider:
                    particle_radius = particle_radius_slider.current_value

                if event.ui_element == sim_speed_slider:
                    sim_speed = sim_speed_slider.current_value

            ui_manager.process_events(event)

        if up_pressed:
            sim_speed = min(sim_speed + 10, 1000)
        if down_pressed:
            sim_speed = max(sim_speed - 10, 1)

        ui_manager.update(delta_t)

        # main drawing logic
        for i, charge in enumerate(particles):
            charge_color = (255, 255, 255)

            if charge.charge < 0:
                charge_color = CHARGE_COLOR_NEG
            elif charge.charge > 0:
                charge_color = CHARGE_COLOR_POS

            # pygame.draw.circle(screen, charge_color, charge.pos.to_tuple(), particle_radius)
            gfxdraw.aacircle(screen, int(charge.pos.x), int(charge.pos.y), particle_radius, charge_color)

            if labels:
                p_name = small_font.render(f'p{i + 1}', True, Colors.WHITE)
                screen.blit(p_name,
                            (charge.pos.x - particle_radius, charge.pos.y - particle_radius - p_name.get_height()))

        ui_manager.draw_ui(screen)

        # --- main logic ---
        if not paused:
            total_time_passed += sim_delta_t

            # calculating forces
            for P in particles:
                F_eq = Vector(0, 0)

                F_e_eq = Vector(0, 0)
                F_g_eq = Vector(0, 0)

                for p in particles:
                    if p == P:
                        continue

                    r12 = P.pos.to_vector() - p.pos.to_vector()
                    r12_abs = distance(Point(0, 0), r12.to_point())
                    hat_r12 = r12 / r12_abs

                    # electrical force
                    F_e = hat_r12 * k * (P.charge * p.charge) / (r12_abs ** 2)

                    # gravitational force
                    F_g = -(hat_r12 * G * (P.mass * p.mass) / (r12_abs ** 2))

                    # ---
                    F_e_eq += F_e
                    F_g_eq += F_g

                F_eq = F_e_eq + F_g_eq
                a = F_eq / P.mass

                P.vel += a

            # updating positions
            for P in particles:
                P.pos.x += P.vel.x * (PPM * sim_delta_t / 1000)
                P.pos.y += P.vel.y * (PPM * sim_delta_t / 1000)

                if P.pos.x > WIDTH:
                    P.pos.x = WIDTH
                    P.vel = Vector(-P.vel.x, P.vel.y) * BOUNCE_SLOWDOWN_FACTOR
                elif P.pos.x < 0:
                    P.pos.x = 0
                    P.vel = Vector(-P.vel.x, P.vel.y) * BOUNCE_SLOWDOWN_FACTOR

                if P.pos.y > HEIGHT:
                    P.pos.y = HEIGHT
                    P.vel = Vector(P.vel.x, -P.vel.y) * BOUNCE_SLOWDOWN_FACTOR
                elif P.pos.y < 0:
                    P.pos.y = 0
                    P.vel = Vector(P.vel.x, -P.vel.y) * BOUNCE_SLOWDOWN_FACTOR

            # checking collision
            for P in particles:
                for p in particles:
                    pass

        # --- stats ---
        # main stats
        screen.blit(main_font.render(f'FPS: {clock.get_fps():.0f}', True, (255, 255, 0)), (0, 0))
        screen.blit(main_font.render(f'Time: {time_ms_to_str(total_time_passed)}', True, (255, 255, 0)), (0, 20))

        # configurable vars stats
        particle_radius_text = main_font.render(f'Particle radius: {particle_radius} px', True, (255, 255, 0))
        labels_text = main_font.render(f'Labels: {labels}', True, (255, 255, 0))
        sim_speeed_text = main_font.render(f'Simulation speed: {sim_speed}X', True, (255, 255, 0))
        paused_text = main_font.render(f'Paused: {paused}', True, (255, 255, 0))

        screen.blit(particle_radius_text, (WIDTH - 250, 20))
        screen.blit(sim_speeed_text, (WIDTH - 250, 60))
        screen.blit(labels_text, (WIDTH - 250, 80))
        screen.blit(paused_text, (WIDTH - 250, 100))

        # particle stats
        if selected_particle_i is not None:
            p = particles[selected_particle_i]
            p_stats_str = f'p{selected_particle_i + 1}\nPosition: {p.pos}\nCharge: {p.charge} C\nMass: {p.mass} kg' \
                          f'\nVelocity: {p.vel}\n'
            p_stats_text = main_font.render(p_stats_str, True, Colors.YELLOW)

            screen.blit(p_stats_text, (0, HEIGHT - p_stats_text.get_height()))

        # updating the display and ticking the clock
        # run = False
        pygame.display.update()
        clock.tick(FPS)
