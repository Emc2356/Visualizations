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

        pygame.display.set_caption("Heap Sort")

    def reset(self) -> None:
        self.resetting = True
        time.sleep(0.5)
        self.resetting = False
        self.array = [i for i in range(1, self.W + 1)]
        random.shuffle(self.array)
        self.i = 0
        self.j = 0
        start_new_thread(self.heap_sort, ())

    def heapify(self, n, i):
        largest = i
        l = 2 * i + 1
        r = 2 * i + 2

        if l < n and self.array[largest] < self.array[l]:
            largest = l

        if r < n and self.array[largest] < self.array[r]:
            largest = r

        if largest != i:
            self.array[i], self.array[largest] = self.array[largest], self.array[i]  # swap

            # Heapify the root.
            self.heapify(n, largest)
        time.sleep(0.001)

    def heap_sort(self):
        n = len(self.array)

        for i in range(n // 2 - 1, -1, -1):
            self.heapify(n, i)

        for i in range(n - 1, 0, -1):
            self.array[i], self.array[0] = self.array[0], self.array[i]  # swap
            self.heapify(i, 0)

    def swap(self, a: int, b: int) -> None:
        self.array[a], self.array[b] = self.array[b], self.array[a]
        time.sleep(0.001)

    def draw(self) -> None:
        self.WIN.fill((0, 0, 0))
        for x, height in enumerate(self.array):
            pygame.draw.line(self.WIN, (255, 255, 255), (x, self.H), (x, self.H - height), 1)
        pygame.display.update()

    def event_handler(self) -> None:
        mods = pygame.key.get_mods()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
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


if __name__ == '__main__':
    run()
