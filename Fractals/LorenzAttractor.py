import OpenGL.GL as GL
import numba as nb
import numpy as np
import colorsys
import pygame


@nb.njit
def progress(
        X: np.ndarray,
        Y: np.ndarray,
        Z: np.ndarray,
        dt: float,
        total: int,
        current: int,
        scale: float,
        steps: int,
):
    sigma = 10
    beta = 8 / 3
    ro = 28

    for _ in range(steps):
        if current == total:
            return

        x = X[current] * scale
        y = Y[current] * scale
        z = Z[current] * scale

        dx = sigma * (y - x)
        dy = x * (ro - z) - y
        dz = x * y - beta * z

        # we set everything after a point to a value cause otherwise we would a weird like pen effect
        current += 1
        X[current:current + 1] = (x + (dx * dt)) / scale
        Y[current:current + 1] = (y + (dy * dt)) / scale
        Z[current:current + 1] = (z + (dz * dt)) / scale


class Game:
    def __init__(self):
        self.W: int = 750
        self.H: int = 750

        self.WIN: pygame.surface.Surface = pygame.display.set_mode(
            (self.W, self.H), pygame.DOUBLEBUF | pygame.OPENGL
        )

        self.running: bool = True
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.FPS: int = 60

        self.N: int = 100_000 * 3
        assert self.N % 3 == 0.0, "expected `N` to be divisible by 3"
        self.steps: int = 1000
        self.current: int = 0
        self.scale: float = 60

        self.X: np.ndarray = np.zeros(self.N, dtype=np.float64)
        self.Y: np.ndarray = np.zeros(self.N, dtype=np.float64)
        self.Z: np.ndarray = np.zeros(self.N, dtype=np.float64)

        self.X[0] = 0.01

        self.dt: float = 0.001

        self.vertex_data = np.zeros(self.N * 3, dtype=np.float64)

        self.color_data = np.ones(self.N * 3, dtype=np.float64)
        for i in range(self.N):
            red, green, blue = colorsys.hsv_to_rgb(i / 255, 1, 1)
            self.color_data[i * 3 + 0] = red
            self.color_data[i * 3 + 1] = green
            self.color_data[i * 3 + 2] = blue

        self.index_data = np.arange(0, self.N, dtype=np.int64)
        self.index_data[0::3] = np.arange(0, self.N, 3, dtype=np.int64)
        self.index_data[1::3] = np.arange(0, self.N, 3, dtype=np.int64)
        self.index_data[2::3] = np.arange(0, self.N, 3, dtype=np.int64)

        pygame.display.set_caption("<TitleGoesHere>")

    def event_handler(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.current = 0

    def draw(self) -> None:
        progress(self.X, self.Y, self.Z, self.dt, self.N, self.current, self.scale, self.steps)
        self.current = min(self.current + self.steps, self.N)

        self.vertex_data[0:self.N*3:3] = self.X
        self.vertex_data[1:self.N*3:3] = self.Y
        self.vertex_data[2:self.N*3:3] = self.Z

        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        GL.glRotatef(1, 1, 1, 1)

        GL.glEnableClientState(GL.GL_VERTEX_ARRAY)
        GL.glEnableClientState(GL.GL_COLOR_ARRAY)

        GL.glVertexPointer(3, GL.GL_FLOAT, 0, self.vertex_data)
        GL.glColorPointer(3, GL.GL_FLOAT, 0, self.color_data)
        GL.glDrawElements(
            GL.GL_LINE_STRIP, self.current, GL.GL_UNSIGNED_INT, self.index_data
        )

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


if __name__ == "__main__":
    run()
