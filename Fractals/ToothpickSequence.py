from typing import List, Optional, Tuple
import pygame
import math
import sys
import os


class ToothPick:
    def __init__(self, pos: pygame.math.Vector2, direction: int, length: float) -> None:

        if direction == 1:
            self.pt1: pygame.math.Vector2 = pygame.math.Vector2(pos.x - length / 2, pos.y)
            self.pt2: pygame.math.Vector2 = pygame.math.Vector2(pos.x + length / 2, pos.y)
        else:
            self.pt1: pygame.math.Vector2 = pygame.math.Vector2(pos.x, pos.y - length / 2)
            self.pt2: pygame.math.Vector2 = pygame.math.Vector2(pos.x, pos.y + length / 2)

        self.direction: int = direction
        self.length: float = length
        self.new: bool = True
        self.useful: bool = True

    def draw(self, WIN: pygame.surface.Surface) -> None:
        pygame.draw.line(WIN, (255, 255, 255), self.pt1, self.pt2, 1)

    def intersects(self, pos: pygame.math.Vector2) -> bool:
        return pos == self.pt1 or pos == self.pt2

    def create_picks(self, others) -> Tuple[Optional["ToothPick"], Optional["ToothPick"]]:
        a, b = None, None
        for tp in others:
            if tp != self and tp.intersects(self.pt1):
                break
        else:
            a = ToothPick(self.pt1, self.direction*-1, self.length)

        for tp in others:
            if tp != self and tp.intersects(self.pt2):
                break
        else:
            b = ToothPick(self.pt2, self.direction*-1, self.length)
        return a, b

    def __bool__(self) -> bool:
        return self.useful


class Visualization:
    def __init__(self) -> None:
        self.W: int = 500
        self.H: int = 500
        self.WIN: pygame.surface.Surface = pygame.display.set_mode((self.W, self.H))

        self.running: bool = True
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.FPS: int = 60

        self.length: int = 10
        self.toothpicks: List[ToothPick] = [
            ToothPick(pygame.math.Vector2(self.W//2, self.H//2), 1, self.length)
        ]

        pygame.display.set_caption("Toothpick Sequence")

    def update(self) -> None:
        toothpicks = self.toothpicks[:]
        for i, tp in sorted(enumerate(self.toothpicks), reverse=True):
            if not tp.new or not tp:
                tp.self.useful = False
                continue
            tp.new = False
            a, b = tp.create_picks(toothpicks)
            if a:
                self.toothpicks.append(a)
                a.draw(self.WIN)
            if b:
                self.toothpicks.append(b)
                b.draw(self.WIN)
            self.toothpicks.pop(i)

    def event_handler(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()

    def run(self) -> None:
        self.WIN.fill((30, 30, 30))
        while self.running:
            self.clock.tick(self.FPS)
            self.event_handler()
            self.update()
            pygame.display.update()


def run() -> None:
    pygame.init()
    vis = Visualization()
    vis.run()


if __name__ == '__main__':
    run()
