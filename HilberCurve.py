from typing import List
import pygame
import math
import sys


class Visualization:
    def __init__(self):
        self.W: int = 512
        self.H: int = 512
        self.WIN: pygame.surface.Surface = pygame.display.set_mode((self.W, self.H))

        self.running: bool = True
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.FPS: int = 60

        self.order = 7
        self.N = int(math.pow(2, self.order))
        self.total = self.N * self.N
        self.length = self.W / self.N
        self.path: List[pygame.math.Vector2] = [
            (self.hilbert(i) * self.length) + [self.length / 2, self.length / 2] for i in range(self.total)
        ]
        self.counter = 0
        self.progress_per_call = 1

        pygame.display.set_caption("Hilbert Curve visualization")

    def update(self) -> None:
        pass

    def hilbert(self, i) -> pygame.math.Vector2:
        points = [
            pygame.math.Vector2(0, 0),
            pygame.math.Vector2(0, 1),
            pygame.math.Vector2(1, 1),
            pygame.math.Vector2(1, 0)
        ]

        index = i & 3
        v = points[index]

        for j in range(1, self.order):
            i = i >> 2
            index = i & 3
            length = math.pow(2, j)
            if index == 0:
                temp = v.x
                v.x = v.y
                v.y = temp
            elif index == 1:
                v.y += length
            elif index == 2:
                v.x += length
                v.y += length
            elif index == 3:
                temp = length - 1 - v.x
                v.x = length - 1 - v.y
                v.y = temp
                v.x += length

        return v

    def event_handler(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()

    def draw(self) -> None:
        self.WIN.fill((0, 0, 0))
        for i in range(1, self.counter):
            pygame.draw.line(self.WIN, (255, 255, 255), (self.path[i].x, self.path[i].y), (self.path[i-1].x, self.path[i-1].y), 1)
        self.counter += self.progress_per_call
        if self.counter >= self.total:
            self.counter = 0

        pygame.display.update()

    def run(self) -> None:
        self.WIN.fill((0, 0, 0))
        while self.running:
            self.clock.tick(self.FPS)
            self.event_handler()
            self.update()
            self.draw()


def run() -> None:
    pygame.init()
    vis = Visualization()
    vis.run()


if __name__ == '__main__':
    run()
