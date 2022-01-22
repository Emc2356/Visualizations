import pygame
import random
import sys


class Visualization:
    def __init__(self) -> None:
        pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN])
        self.W: int = 750
        self.H: int = 750
        self.WIN: pygame.surface.Surface = pygame.display.set_mode((self.W, self.H))

        self.running: bool = True
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.FPS: int = 60

        self.i: int = 0
        self.j: int = 0
        self.moved: int = 0
        self.array: list = []
        self.reset()

        pygame.display.set_caption("Bubble Sort")

    def reset(self) -> None:
        self.array = [i for i in range(1, self.W + 1)]
        random.shuffle(self.array)
        self.i = 0
        self.j = 0
        self.moved = 0

    def sort(self) -> None:
        for _ in range(1000):
            a = self.array[self.j]
            b = self.array[self.j + 1]
            if a < b:
                self.swap(self.j, self.j + 1)
                self.moved = self.j
            self.j += 1
            if self.j >= len(self.array) - self.i - 1:
                self.i += 1
                self.j = 0

    def swap(self, a: int, b: int) -> None:
        self.array[a], self.array[b] = self.array[b], self.array[a]

    def draw(self) -> None:
        self.WIN.fill((0, 0, 0))
        for x, height in enumerate(self.array):
            pygame.draw.line(
                self.WIN,
                (255, 255, 255) if x != self.moved + 1 else (255, 0, 0),
                (x, self.H),
                (x, self.H - (self.H - height)),
                1,
            )
        pygame.display.update()

    def event_handler(self) -> None:
        mods = pygame.key.get_mods()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and (mods & pygame.K_LCTRL):
                    self.reset()

    def run(self) -> None:
        while self.running:
            self.clock.tick(self.FPS)
            self.sort()
            self.event_handler()
            self.draw()


def run() -> None:
    pygame.init()
    vis = Visualization()
    vis.run()


if __name__ == "__main__":
    run()
