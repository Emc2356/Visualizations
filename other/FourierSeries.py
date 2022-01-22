from typing import List
import pygame
import math
import sys
import os


PI = math.pi


class Visualization:
    def __init__(self):
        self.W: int = 1200
        self.H: int = 700
        self.WIN: pygame.surface.Surface = pygame.display.set_mode((self.W, self.H))

        self.running: bool = True
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.FPS: int = 60

        self.n: int = 11
        self.time: float = 0

        self.wave: List[float] = []

        pygame.display.set_caption("Fourier Series")

    def update(self) -> None:
        self.WIN.fill((30, 30, 30))

        x = 350
        y = self.H // 2
        for i in range(self.n):
            px, py = x, y

            n = i * 2 + 1
            radius = 100 * (4 / (n * PI))

            x += radius * math.cos(n * self.time)
            y += radius * math.sin(n * self.time)

            pygame.draw.circle(self.WIN, (255, 255, 255), (px, py), radius, 1)
            pygame.draw.line(self.WIN, (255, 255, 255), (x, y), (px, py), 2)
            pygame.draw.circle(self.WIN, (255, 255, 255), (x, y), 4)

        self.wave.insert(0, y)

        if len(self.wave) > 500:
            self.wave.pop()

        pygame.draw.line(
            self.WIN, (255, 255, 255), (x, y), (self.W // 2 + 150, self.wave[0])
        )

        for i, value in enumerate(self.wave[:-1]):
            x = self.W // 2 + 150 + i
            pygame.draw.line(
                self.WIN, (255, 255, 255), (x, value), (x, self.wave[i + 1])
            )

        pygame.display.update()

        self.time -= 0.05

    def event_handler(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                pygame.quit()
                sys.exit()

    def run(self) -> None:
        while self.running:
            self.clock.tick(self.FPS)
            self.event_handler()
            self.update()


def run() -> None:
    pygame.init()
    vis = Visualization()
    vis.run()


if __name__ == "__main__":
    run()
