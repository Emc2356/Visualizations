from _thread import start_new_thread as thread
import numba as nb
import numpy as np
import pygame
import sys


DAMPING: float = 0.99


@nb.jit("void(f8[:,:],f8[:,:])", fastmath=True)
def compute(arr1: np.ndarray, arr2: np.ndarray) -> None:
    # formulas are taken from https://web.archive.org/web/20160418004149/http://freespace.virgin.net/hugo.elias/graphics/x_water.htm
    for i in range(1, len(arr1)-1):
        for j in range(1, len(arr1[i])-1):
            arr2[i, j] = (
                           arr1[i-1, j] +
                           arr1[i+1, j] +
                           arr1[i, j+1] +
                           arr1[i, j-1]
                           ) / 2 - arr2[i, j]
    arr2[:] *= DAMPING


class Game:
    def __init__(self):
        self.W: int = 500
        self.H: int = 500
        self.WIN: pygame.surface.Surface = pygame.display.set_mode((self.W, self.H))

        self.buffer1: np.ndarray = np.ndarray((self.H, self.W))
        self.buffer2: np.ndarray = np.ndarray((self.H, self.W))

        self.running: bool = True
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.FPS: int = 60

        thread(self.compute, ())

        pygame.display.set_caption("Water Ripple effect")

    def compute(self) -> None:
        clock = pygame.time.Clock()
        while self.running:
            clock.tick(self.FPS)
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
                    self.buffer1[:] = 0
                    self.buffer2[:] = 0
        # use events if you want to trigger only at start of the click
        # with this you can drag click
        if pygame.mouse.get_pressed(3)[0]:
            self.buffer1[pygame.mouse.get_pos()] = 255

    def draw(self) -> None:
        pygame.surfarray.blit_array(self.WIN, self.buffer1)
        pygame.display.flip()

    def run(self) -> None:
        while self.running:
            self.clock.tick(self.FPS)
            self.event_handler()
            self.draw()


def run():
    game = Game()
    game.run()


if __name__ == '__main__':
    run()
