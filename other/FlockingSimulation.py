from PygameHaze import QuadTree
from typing import List, Tuple
import itertools
import random
import pygame
import time
import math
import sys
import os


W: int = 1200
H: int = 750


def randomVector():
    return pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))


setattr(  # needed because the QuadTree is broken atm (-_-)
    QuadTree,
    "get_items",
    lambda self: self.storage + list(itertools.chain.from_iterable([ch.get_items() for ch in self.children]))
)


class Ship:
    max_speed = 5
    max_force = 0.5

    def __init__(self) -> None:
        self.pos: pygame.math.Vector2 = pygame.math.Vector2(random.randint(0, W), random.randint(0, H))
        self.vel: pygame.math.Vector2 = randomVector()
        self.vel.scale_to_length(random.choice([2, 4]))
        self.acc: pygame.math.Vector2 = pygame.math.Vector2()

    def edges(self) -> None:
        self.pos.x = self.pos.x % W
        self.pos.y = self.pos.y % H

    def align(self, others: List["Ship"]) -> pygame.math.Vector2:
        perceptionRadius = 25 * 25
        steering = pygame.math.Vector2()
        total = 0
        for other in others:
            d = self.pos.distance_squared_to(other.pos)
            if other != self and d < perceptionRadius:
                steering += other.vel
                total += 1
        if total > 0:
            steering /= total
            steering.scale_to_length(self.max_speed)
            steering -= self.vel
            if steering.magnitude_squared() > self.max_force * self.max_force: steering.scale_to_length(self.max_force)
        return steering

    def separation(self, others: List["Ship"]) -> pygame.math.Vector2:
        perceptionRadius = 24 * 24
        steering = pygame.math.Vector2()
        total = 0
        for other in others:
            d = self.pos.distance_squared_to(other.pos)
            if other != self and d < perceptionRadius:
                diff = self.pos - other.pos
                diff /= d or 1
                steering += diff
                total += 1

        if total > 0:
            steering /= total
            try: steering.scale_to_length(self.max_speed)
            except ValueError: pass
            steering -= self.vel
            if steering.magnitude_squared() > self.max_force * self.max_force: steering.scale_to_length(self.max_force)
        return steering

    def cohesion(self, others: List["Ship"]) -> pygame.math.Vector2:
        perceptionRadius = 50 * 50
        steering = pygame.math.Vector2()
        total = 0
        for other in others:
            d = self.pos.distance_squared_to(other.pos)
            if other != self and d < perceptionRadius:
                steering += other.pos
                total += 1

        if total > 0:
            steering /= total
            steering -= self.pos
            try: steering.scale_to_length(self.max_speed)
            except ValueError: pass
            steering -= self.vel
            if steering.magnitude_squared() > self.max_force * self.max_force: steering.scale_to_length(self.max_force)

        return steering

    def flock(self, others: QuadTree) -> "Ship":
        al = self.align(others.query(
            pygame.Rect(self.pos - pygame.math.Vector2(25, 25), pygame.math.Vector2(25*2, 25*2)))
        )
        se = self.separation(others.query(
            pygame.Rect(self.pos - pygame.math.Vector2(24, 24), pygame.math.Vector2(24*2, 24*2)))
        )
        co = self.cohesion(others.query(
            pygame.Rect(self.pos - pygame.math.Vector2(50, 50), pygame.math.Vector2(50*2, 50*2)))
        )

        self.acc += al + se + co
        return self

    def update(self, dt: float=1) -> "Ship":
        self.vel += self.acc
        self.pos += self.vel * dt
        if self.vel.magnitude_squared() > self.max_force * self.max_force: self.vel.scale_to_length(self.max_force)
        self.acc.update(0, 0)
        return self

    def draw(self, surface: pygame.surface.Surface) -> None:
        pygame.draw.circle(surface, (255, 255, 255), self.pos, 4)


class Game:
    def __init__(self):
        self.WIN: pygame.surface.Surface = pygame.display.set_mode((W, H))

        self.running: bool = True
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.FPS: int = 60

        self.qt = QuadTree(self.WIN.get_rect(), 5)
        self.ships: List[Ship] = [Ship() for _ in range(200)]

        self.last_time: float = time.time()
        self.dt = (time.time() - self.last_time) * self.FPS
        self.last_time = time.time()

        pygame.display.set_caption("Flocking Simulation with pygame")

    def event_handler(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.ships.append(Ship())
                self.ships[~0].pos = pygame.math.Vector2(event.pos)

    def draw(self) -> None:
        self.WIN.fill((30, 30, 30))
        self.qt = QuadTree(self.WIN.get_rect(), 5)
        self.qt.list_insert(self.ships)
        for ship in self.ships:
            ship.edges()
            ship.flock(self.qt)
            ship.update(self.dt)
            ship.draw(self.WIN)
        pygame.display.update()

    def run(self) -> None:
        while self.running:
            self.dt = (time.time() - self.last_time) * self.FPS
            self.last_time = time.time()
            self.clock.tick(self.FPS)
            self.event_handler()
            self.draw()


def run():
    game = Game()
    game.run()


if __name__ == '__main__':
    run()
