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

        self.array: list = []
        self.resetting: bool = False
        self.reset()

        pygame.display.set_caption("Selection sort")

    def reset(self) -> None:
        self.resetting = True
        time.sleep(0.5)
        self.resetting = False
        self.array = [i for i in range(1, self.W + 1)]
        random.shuffle(self.array)
        start_new_thread(self.selection_sort, (0,))

    def selection_sort(self, start: int) -> None:
        if start >= len(self.array) or self.resetting:
            return
        cur_min = float("inf")
        cur_min_index = None
        for i in sorted(range(start, len(self.array)), reverse=True):
            if self.array[i] < cur_min:
                cur_min = self.array[i]
                cur_min_index = i
        self.swap(start, cur_min_index)
        self.selection_sort(start + 1)

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
