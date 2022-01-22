from math import cos, sin, pi
import numpy as np  # ironic cause i use numpy to do the calculations when numpy as discrete fourier init (-_-)
import random
import pygame
import sys
import os


TWO_PI = pi * 2


def dft(values: list) -> np.recarray:
    N = len(values)
    out: np.recarray = np.recarray(
        (N,),
        dtype=[
            ("re", float),
            ("im", float),
            ("freq", int),
            ("ampl", float),
            ("phase", float),
        ],
    )
    values = np.array(values)
    NRange = np.arange(N)
    for k in range(N):
        out[k].re = (values * np.cos((NRange * k * TWO_PI) / N)).sum() / N
        out[k].im = (-values * np.sin((NRange * k * TWO_PI) / N)).sum() / N
    out.freq = NRange
    np.sqrt(out.re * out.re + out.im * out.im, out=out.ampl)
    np.arctan2(out.im, out.re, out=out.phase)

    return out


class Game:
    def __init__(self):
        self.W: int = 1200
        self.H: int = 750
        self.WIN: pygame.surface.Surface = pygame.display.set_mode((self.W, self.H))

        self.running: bool = True
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.FPS: int = 60

        x, y = [], []
        for i in range(500):
            x.append(i)
            y.append(sin(i / 10) * 200)

        self.Y = dft(y)
        self.Y.sort(order="ampl")
        self.Y = np.flip(self.Y)

        self.X = dft(x)
        self.X.sort(order="ampl")
        self.X = np.flip(self.X)

        self.time: float = 0
        self.timestep: float = TWO_PI / len(self.Y)

        self.path = []

    def draw_epic_cycles(
        self, pos: pygame.math.Vector2, rotation: float, series: np.recarray
    ) -> pygame.math.Vector2:
        for i in range(len(series)):
            prev_pos = pygame.math.Vector2(pos)
            freq = series[i].freq
            radius = series[i].ampl
            phase = series[i].phase
            pos += (
                radius * cos(freq * self.time + phase + rotation),
                radius * sin(freq * self.time + phase + rotation),
            )

            pygame.draw.circle(self.WIN, (255, 255, 255), prev_pos, radius, 1)
            pygame.draw.line(self.WIN, (255, 255, 255), prev_pos, pos)
        return pygame.math.Vector2(pos)

    def event_handler(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                pygame.quit()
                sys.exit()

    def draw(self) -> None:
        self.WIN.fill((30, 30, 30))

        vy = self.draw_epic_cycles(
            pygame.math.Vector2(200, self.H / 2), self.time, self.Y
        )
        vx = self.draw_epic_cycles(
            pygame.math.Vector2(self.W - 200, 300), self.time, self.X
        )

        v = pygame.math.Vector2(vx.x, vy.y)

        self.path.append(pygame.math.Vector2(pygame.math.Vector2(v)))

        pygame.draw.line(self.WIN, (255, 255, 255), (vx.x, vx.y), (v.x, v.y))
        pygame.draw.line(self.WIN, (255, 255, 255), (vy.x, vy.y), (v.x, v.y))

        if len(self.path) > 1:
            pygame.draw.lines(self.WIN, (255, 255, 255), False, self.path)

        self.time += self.timestep

        if self.time > pi:
            self.time = 0
            self.path.clear()

        pygame.display.update()

    def run(self) -> None:
        while self.running:
            self.clock.tick(self.FPS)
            self.event_handler()
            self.draw()


def run():
    game = Game()
    game.run()


if __name__ == "__main__":
    run()
