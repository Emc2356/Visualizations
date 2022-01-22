from _thread import start_new_thread
import pygame
import random
import time
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
        self.array: list = []
        self.resetting = True
        self.reset()

        pygame.display.set_caption("Quick Sort")

    def reset(self) -> None:
        self.resetting = True
        time.sleep(0.5)
        self.resetting = False
        self.array = [i for i in range(1, self.W + 1)]
        random.shuffle(self.array)
        self.i = 0
        self.j = 0
        start_new_thread(self.quick_sort, (0, len(self.array) - 1))

    def partition(self, start: int, end: int) -> int:
        pivot_index = start
        pivot_value = self.array[end]
        for i in range(start, end):
            if self.array[i] < pivot_value:
                self.swap(i, pivot_index)
                pivot_index += 1
        self.swap(pivot_index, end)
        return pivot_index

    def quick_sort(self, start: int, end: int) -> None:
        if start >= end or self.resetting:
            return
        index = self.partition(start, end)
        self.quick_sort(start, index - 1)
        self.quick_sort(index + 1, end)

    def swap(self, a: int, b: int) -> None:
        self.array[a], self.array[b] = self.array[b], self.array[a]
        time.sleep(0.001)

    def draw(self) -> None:
        self.WIN.fill((0, 0, 0))
        for x, height in enumerate(self.array):
            pygame.draw.line(
                self.WIN, (255, 255, 255), (x, self.H), (x, self.H - height), 1
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
            self.event_handler()
            self.draw()


def run() -> None:
    pygame.init()
    vis = Visualization()
    vis.run()


if __name__ == "__main__":
    run()
