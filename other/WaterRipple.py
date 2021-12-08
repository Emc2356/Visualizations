from _thread import start_new_thread as thread
import numpy as np
import pygame
import sys


WIDTH: int = 500
HEIGHT: int = 500
DAMPING: float = 0.99
temp: np.ndarray = np.ndarray((WIDTH, HEIGHT))

# formulas are taken from https://web.archive.org/web/20160418004149/http://freespace.virgin.net/hugo.elias/graphics/x_water.htm
# but implemented with numpy arrays


def compute(arr1: np.ndarray, arr2: np.ndarray) -> None:
    # this part is heavily inspired by https://github.com/davidpendergast/pygame-utils/blob/2628aed6788e86fe28fa9ff77d87e08d395811b6/life.py#L21
    temp[:] = 0
    arr1[:, [0, -1]] = 0
    arr1[[0, -1]] = 0
    shifted = np.roll(arr1, (-1, 0), (0, 1))
    np.add(temp, shifted, out=temp)
    shifted = np.roll(arr1, (+1, 0), (0, 1))
    np.add(temp, shifted, out=temp)
    shifted = np.roll(arr1, (0, +1), (0, 1))
    np.add(temp, shifted, out=temp)
    shifted = np.roll(arr1, (0, -1), (0, 1))
    np.add(temp, shifted, out=temp)
    np.divide(temp, 2, out=temp)
    np.subtract(temp, arr2, out=arr2)

    arr2[:] *= DAMPING


class Game:
    def __init__(self):
        self.WIN: pygame.surface.Surface = pygame.display.set_mode((WIDTH, HEIGHT))

        self.buffer1: np.ndarray = np.ndarray((WIDTH, HEIGHT))
        self.buffer2: np.ndarray = np.ndarray((WIDTH, HEIGHT))

        self.running: bool = True
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.FPS: int = 60

        self.reset: bool = False

        pygame.display.set_caption("Water Ripple effect")

    def compute(self) -> None:
        clock = pygame.time.Clock()
        while self.running:
            clock.tick(self.FPS)
            if self.reset:
                self.buffer1[:] = 0
                self.buffer2[:] = 0
                self.reset = False
            compute(self.buffer1, self.buffer2)
            self.buffer1, self.buffer2 = self.buffer2, self.buffer1

    def event_handler(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.reset = True
        # use events if you want to trigger only at start of the click
        # with this you can drag click
        if pygame.mouse.get_pressed(3)[0]:
            self.buffer1[pygame.mouse.get_pos()] = 255

    def draw(self) -> None:
        pygame.surfarray.blit_array(self.WIN, self.buffer1)
        pygame.display.flip()

    def run(self) -> None:
        thread(self.compute, ())
        while self.running:
            self.clock.tick(self.FPS)
            self.event_handler()
            self.draw()


def run():
    game = Game()
    game.run()


if __name__ == '__main__':
    run()
