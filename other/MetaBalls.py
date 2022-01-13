from typing import Optional
import numba as nb
import numpy as np
import pygame
import random
import time
import math
import sys
import os


CORES = os.cpu_count()


BallsDType = np.dtype([
    ("pos", (np.float64, (2,))),
    ("vel", (np.float64, (2,))),
    ("radius", np.int64)
])


def update_balls(width: int, height: int, balls: np.recarray, dt: float=1) -> None:
    boarders = [width, height]
    for ball in balls:
        ball.pos += ball.vel * dt
        for i in range(2):
            if ball.pos[i] < ball.radius / 10:
                ball.pos[i] = ball.radius / 10
                ball.vel[i] *= -1
            elif ball.pos[i] > boarders[i] - ball.radius / 10:
                ball.pos[i] = boarders[i] - ball.radius / 10
                ball.vel[i] *= -1


@nb.njit
def hsv_to_rgb(h: float, s: float, v: float):
    C = v * s
    X = C * (1 - abs((h / 60) % 2 - 1))
    m = int(v - C)

    if h < 60:  return int(255 * C + m), int(255 * X + m), m
    if h < 120: return int(255 * X + m), int(255 * C + m), m
    if h < 180: return m, int(255 * C + m), int(255 * X + m)
    if h < 240: return m, int(255 * X + m), int(255 * C + m)
    if h < 300: return int(255 * X + m), m, int(255 * C + m)
    return int(255 * C + m), m, int(255 * X + m)


@nb.njit
def render_on_array(array: np.ndarray, balls: np.recarray) -> None:
    width = array.shape[0]
    height = array.shape[1]
    for start in nb.prange(CORES):
        for x in range(start, width, CORES):
            for y in range(height):
                total = 0
                for ball in balls:
                    xdif = x - ball.pos[0]
                    ydif = y - ball.pos[1]
                    d = (math.sqrt(xdif * xdif + ydif * ydif) + 0.01) / 1.5
                    total += 10 * ball.radius / d
                array[x, y] = hsv_to_rgb(total % 360, 1, 1)
                # array[x, y] = total, total, total


class Game:
    def __init__(self):
        self.W: int = 1000
        self.H: int = 500
        self.WIN: pygame.surface.Surface = pygame.display.set_mode((self.W, self.H))

        self.array: np.ndarray = pygame.surfarray.array3d(self.WIN)

        self.n_balls: int = 10
        self.balls: Optional[np.recarray] = None
        self.generate_n_balls(self.n_balls)

        self.running: bool = True
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.FPS: int = 60

        self.last_time: float = time.time()
        self.dt: float = 0

        pygame.display.set_caption("metaballs in python with pygame and numba")

    def generate_n_balls(self, n: int) -> None:
        balls = np.recarray((n,), dtype=BallsDType)
        for i in range(n):
            radius = random.randint(120, 240)
            balls[i].radius = radius
            balls[i].pos = (
                random.randint(radius, self.W - radius),
                random.randint(radius, self.H - radius)
            )
            balls[i].vel = (np.random.random(2) * 2 - 1) * 5
        self.balls = balls

    def update(self) -> None:
        if self.balls is None:
            self.generate_n_balls(self.n_balls)
        update_balls(self.W, self.H, self.balls, self.dt)

    def event_handler(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()

    def draw(self) -> None:
        render_on_array(self.array, self.balls)
        pygame.surfarray.blit_array(self.WIN, self.array)
        pygame.display.update()

    def run(self) -> None:
        while self.running:
            self.dt = (time.time() - self.last_time) * 60
            self.last_time = time.time()
            self.clock.tick(self.FPS)
            self.event_handler()
            self.update()
            self.draw()


def run():
    game = Game()
    game.run()


if __name__ == '__main__':
    run()
