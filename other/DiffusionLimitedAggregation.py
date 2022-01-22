from PygameHaze import QuadTree
from typing import List, Set
import itertools
import pygame
import random
import math
import sys
import os

W: int = 500
H: int = 500


def clampVc(self, x, y):
    self.x = max(min(self.x, x), 0)
    self.y = max(min(self.y, y), 0)
    return self


def randomVc():
    return pygame.math.Vector2(random.uniform(-1, 1), random.uniform(0, 0.5))


class Particle:
    def __init__(self, pos: pygame.math.Vector2, r: float, stuck=False) -> None:
        self.pos: pygame.math.Vector2 = pos
        self.stuck: bool = stuck
        self.r: int = r

    def move(self) -> None:
        if not self.stuck:
            self.pos = clampVc((self.pos + randomVc()), W, H)


class Game:
    def __init__(self):
        self.WIN: pygame.surface.Surface = pygame.display.set_mode((W, H))

        self.running: bool = True
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.FPS: int = 60

        self.tree: Set[Particle] = set()
        self.particles: Set[Particle] = set()

        self.particle_limit = 25
        self.iterations = 100
        self.radius = 8
        self.shrink = 0.9995

        for x in range(0, W, self.radius * 2):
            self.tree.add(
                Particle(pygame.math.Vector2(x, H - self.radius), self.radius, True)
            )

        self.qt: QuadTree = QuadTree(self.WIN.get_rect(), 10)
        self.qt.list_insert(self.tree)

        pygame.display.set_caption("Diffusion-limited aggregation")

    def update(self) -> None:
        for _ in range(self.iterations):
            while len(self.particles) < self.particle_limit:
                self.particles.add(
                    Particle(
                        pygame.math.Vector2(random.random() * W, random.random() * 10),
                        self.radius,
                    )
                )
            to_remove = set()
            for p in self.particles:
                p.move()
                for o in self.qt.query(
                    pygame.Rect(
                        p.pos - (self.radius, self.radius),
                        (self.radius * 3, self.radius * 3),
                    )
                ):
                    if p.pos.distance_to(o.pos) < self.radius * 2 - 2:
                        p.stuck = True
                        to_remove.add(p)
                        self.tree.add(p)
                        self.qt.insert(p)
                        self.radius *= self.shrink
            self.particles.difference_update(to_remove)

    def event_handler(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                pygame.quit()
                sys.exit()

    def draw(self) -> None:
        self.WIN.fill((30, 30, 30))
        for p in self.tree:
            pygame.draw.circle(self.WIN, (255, 0, 0), p.pos, p.r)
        for p in self.particles:
            pygame.draw.circle(self.WIN, (255, 255, 255), p.pos, p.r)
        pygame.display.update()

    def run(self) -> None:
        while self.running:
            self.clock.tick(self.FPS)
            self.event_handler()
            self.update()
            self.draw()


def run():
    game = Game()
    game.run()


if __name__ == "__main__":
    run()
