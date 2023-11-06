import math
import random
from typing import Tuple, List, Dict

import pygame

pygame.init()
pygame.font.init()

WIDTH = 800
HEIGHT = 800
BG_COLOR = (27, 36, 48)
FPS = 120
FONTS = pygame.font.get_fonts()
PPM = 1  # pixels per meter

CHARGE_RADIUS = 4
CHARGE_COLOR_NEG = (255, 51, 51)
CHARGE_COLOR_POS = (91, 192, 222)

k = 1  # depends on medium. for void, i mean for vacuum it is = 1
G = 6.67430 * (10 ** -11)
BOUNCE_SLOWDOWN_FACTOR = 0.5


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
    return math.sqrt((p1.x + p2.x) ** 2 + (p1.y + p2.y) ** 2)


def random_point() -> Point:
    return Point(
        random.randint(0, WIDTH),
        random.randint(0, HEIGHT)
    )


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
        Particle(0, 1 ** 13, Point(WIDTH * 1 / 2, HEIGHT / 2)),
        Particle(0, 1, Point(10, (HEIGHT / 2) + 10), Vector(100, 0)),
        Particle(0, 1, Point(10, (HEIGHT / 2) + 20), Vector(100, 0)),
        Particle(0, 1, Point(10, (HEIGHT / 2) + 30), Vector(100, 0)),
        Particle(0, 1, Point(10, (HEIGHT / 2) + 40), Vector(100, 0)),
        Particle(0, 1, Point(10, (HEIGHT / 2) + 50), Vector(100, 0)),
    ],
    [
        Particle(0, 1, random_point(), Vector(0, 0)),
        Particle(-5, 1, random_point()),
        Particle(5, 1, random_point()),
        Particle(5, 1, random_point()),
    ]
]

if __name__ == '__main__':
    run = True

    screen = pygame.display.set_mode(size=(WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    main_font = pygame.font.SysFont('JetBrains Mono', 20)
    delta_t = 0

    particles = PRESETS[3]

    # mainloop
    while run:
        # bg
        screen.fill(BG_COLOR)
        delta_t = clock.get_time()

        # events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        # main drawing logic
        for charge in particles:
            charge_color = (255, 255, 255)

            if charge.charge < 0:
                charge_color = CHARGE_COLOR_NEG
            elif charge.charge > 0:
                charge_color = CHARGE_COLOR_POS

            pygame.draw.circle(screen, charge_color, charge.pos.to_tuple(), CHARGE_RADIUS)

        # main logic
        for Q in particles:
            F_eq = Vector(0, 0)

            F_e_eq = Vector(0, 0)
            F_g_eq = Vector(0, 0)

            for q in particles:
                if q == Q:
                    continue

                r12 = Q.pos.to_vector() - q.pos.to_vector()
                r12_abs = distance(Point(0, 0), r12.to_point())
                hat_r12 = r12 / r12_abs

                # electrical force
                F_e = hat_r12 * k * (Q.charge * q.charge) / (r12_abs ** 2)

                # gravitational force
                F_g = -(hat_r12 * G * (Q.mass * q.mass) / (r12_abs ** 2))

                # ---
                F_e_eq += F_e
                F_g_eq += F_g

            F_eq = F_e_eq + F_g_eq
            a = F_eq / Q.mass

            Q.vel += a

        for Q in particles:
            Q.pos.x += Q.vel.x * (PPM * delta_t / 1000)
            Q.pos.y += Q.vel.y * (PPM * delta_t / 1000)

            if Q.pos.x > WIDTH:
                Q.pos.x = WIDTH
                Q.vel = Vector(-Q.vel.x, Q.vel.y) * BOUNCE_SLOWDOWN_FACTOR
            elif Q.pos.x < 0:
                Q.pos.x = 0
                Q.vel = Vector(-Q.vel.x, Q.vel.y) * BOUNCE_SLOWDOWN_FACTOR

            if Q.pos.y > HEIGHT:
                Q.pos.y = HEIGHT
                Q.vel = Vector(Q.vel.x, -Q.vel.y) * BOUNCE_SLOWDOWN_FACTOR
            elif Q.pos.y < 0:
                Q.pos.y = 0
                Q.vel = Vector(Q.vel.x, -Q.vel.y) * BOUNCE_SLOWDOWN_FACTOR

        # fps
        c_fps = clock.get_fps()
        screen.blit(main_font.render(f'FPS: {c_fps:.0f}', True, (255, 255, 0)), (0, 0))

        # updating the display and ticking the clock
        # run = False
        pygame.display.update()
        clock.tick(FPS)
