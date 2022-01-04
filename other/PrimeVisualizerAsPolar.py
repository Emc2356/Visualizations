from OpenGL.GL import *
import OpenGL.GL as GL
import numpy as np
import pygame


USE_PRIMES: bool = True

N: int = 5000  # the number of primes that we will use
POINT_SIZE: float = .05


if USE_PRIMES:
    # pip install prime-sieve
    from prime_sieve.array import PrimeArraySieve


class Game:
    def __init__(self):
        self.W: int = 750
        self.H: int = 750

        self.WIN: pygame.surface.Surface = pygame.display.set_mode((self.W, self.H), pygame.DOUBLEBUF | pygame.OPENGL)

        self.running: bool = True
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.FPS: int = 60

        if USE_PRIMES:
            self.sieve: PrimeArraySieve = PrimeArraySieve()
            self.numbers: np.ndarray = self.sieve[:N]
        else:
            self.numbers: np.ndarray = np.arange(N, dtype=int)

        self.x: np.ndarray = self.numbers * np.cos(self.numbers)
        self.y: np.ndarray = self.numbers * np.sin(self.numbers)

        self.vertex_data = np.zeros(N * 2, dtype=float)
        self.vertex_data[0:N*2:2] = self.x
        self.vertex_data[1:N*2:2] = self.y

        # rgb value: (170, 255, 170)
        # hex value: 0xAAFFAA
        self.color_data = np.ones(N * 3, dtype=float)
        self.color_data[0::3] = 170 / 255  # Red
        self.color_data[1::3] = 255 / 255  # Green
        self.color_data[2::3] = 170 / 255  # Blue

        self.index_data = np.arange(0, N, dtype=int)
        self.index_data[0::2] = np.arange(0, N, 2, dtype=int)
        self.index_data[1::2] = np.arange(0, N, 2, dtype=int)

        pygame.display.set_caption("Prime Number Visualizer as polar coordinates")
        view = int(self.numbers[~0])
        glOrtho(-view, view, view, -view, view, -view)

    def event_handler(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                raise SystemExit

    def draw(self) -> None:
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        GL.glPointSize(POINT_SIZE)

        GL.glEnableClientState(GL.GL_VERTEX_ARRAY)
        GL.glEnableClientState(GL.GL_COLOR_ARRAY)

        GL.glVertexPointer(2, GL.GL_FLOAT, 0, self.vertex_data)
        GL.glColorPointer(3, GL.GL_FLOAT, 0, self.color_data)
        GL.glDrawElements(GL.GL_POINTS, len(self.index_data), GL.GL_UNSIGNED_INT, self.index_data)

        GL.glDisableClientState(GL.GL_VERTEX_ARRAY)
        GL.glDisableClientState(GL.GL_COLOR_ARRAY)

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
