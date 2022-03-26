import OpenGL.GL as GL
import numba as nb
import numpy as np
import colorsys
import pygame


sigma = 10
beta = 8 / 3
ro = 28


# process
@nb.njit
def process_single_attractor(
        X: np.ndarray,
        Y: np.ndarray,
        Z: np.ndarray,
        dt: float,
        total: int,
        current: int,
        scale: float,
        steps: int,
) -> None:
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


@nb.njit(parallel=True)
def process_multiple_attractors(
    XX: np.ndarray,
    YY: np.ndarray,
    ZZ: np.ndarray,
    count: int,
    dt: float,
    total: int,
    current: int,
    scale: float,
    steps: int,
) -> None:
    for i in nb.prange(count):
        process_single_attractor(
            XX[i],
            YY[i],
            ZZ[i],
            dt,
            total,
            current,
            scale,
            steps,
        )


class SingleAttractor:
    def __init__(self):
        self.W: int = 750
        self.H: int = 750

        self.WIN: pygame.surface.Surface = pygame.display.set_mode(
            (self.W, self.H), pygame.DOUBLEBUF | pygame.OPENGL
        )

        self.running: bool = True
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.FPS: int = 60

        self.N: int = 200_000 * 3
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
            red, green, blue = colorsys.hsv_to_rgb(i / 1000, 1, 1)
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
        process_single_attractor(self.X, self.Y, self.Z, self.dt, self.N, self.current, self.scale, self.steps)
        self.current = min(self.current + self.steps, self.N)

        if self.current <= self.N:
            self.vertex_data[0:self.current*3:3] = self.X[:self.current]
            self.vertex_data[1:self.current*3:3] = self.Y[:self.current]
            self.vertex_data[2:self.current*3:3] = self.Z[:self.current]

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


class MultiAttractors:
    def __init__(self):
        self.W: int = 750
        self.H: int = 750

        self.WIN: pygame.surface.Surface = pygame.display.set_mode(
            (self.W, self.H), pygame.DOUBLEBUF | pygame.OPENGL
        )

        self.running: bool = True
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.FPS: int = 60

        # how many "heads" we will have
        self.ATTRACTOR_COUNT: int = 2

        self.N: int = 50_000 * 3
        assert self.N % 3 == 0.0, "expected `N` to be divisible by 3"
        self.steps: int = 100
        self.current: int = 0
        self.scale: float = 60

        self.attractors: np.recarray = np.recarray(
            (self.ATTRACTOR_COUNT,),
            [
                ("X", (np.float64, (self.N,))),
                ("Y", (np.float64, (self.N,))),
                ("Z", (np.float64, (self.N,))),
                ("vertex_data", (np.float64, (self.N * 3,))),
                ("color", (np.float64, (3,))),
            ]
        )

        self.attractors.X[:, 0] = np.linspace(0.0001, 0.001, self.ATTRACTOR_COUNT, dtype=np.float64)

        self.dt: float = 0.001

        for i in range(self.ATTRACTOR_COUNT):
            red, green, blue = colorsys.hsv_to_rgb(i / self.ATTRACTOR_COUNT, 1, 1)
            self.attractors[i].color[0] = red
            self.attractors[i].color[1] = green
            self.attractors[i].color[2] = blue

        self.index_data = np.arange(0, self.N, dtype=np.int64)
        self.index_data[0::3] = np.arange(0, self.N, 3, dtype=np.int64)
        self.index_data[1::3] = np.arange(0, self.N, 3, dtype=np.int64)
        self.index_data[2::3] = np.arange(0, self.N, 3, dtype=np.int64)

        pygame.display.set_caption("Lorenz Attractor")

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
        process_multiple_attractors(
            self.attractors.X,
            self.attractors.Y,
            self.attractors.Z,
            self.ATTRACTOR_COUNT,
            self.dt,
            self.N,
            self.current,
            self.scale,
            self.steps
        )
        self.current = min(self.current + self.steps, self.N)

        self.attractors.vertex_data[:, 0:self.N*3:3] = self.attractors.X[:]
        self.attractors.vertex_data[:, 1:self.N*3:3] = self.attractors.Y[:]
        self.attractors.vertex_data[:, 2:self.N*3:3] = self.attractors.Z[:]

        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        GL.glRotatef(1, 1, 1, 1)

        for i in range(self.ATTRACTOR_COUNT):
            GL.glColor3f(
                self.attractors[i].color[0],
                self.attractors[i].color[1],
                self.attractors[i].color[2],
            )

            GL.glEnableClientState(GL.GL_VERTEX_ARRAY)

            GL.glVertexPointer(3, GL.GL_FLOAT, 0, self.attractors[i].vertex_data)
            GL.glDrawElements(
                GL.GL_LINE_STRIP, self.current, GL.GL_UNSIGNED_INT, self.index_data
            )

            GL.glDisableClientState(GL.GL_VERTEX_ARRAY)

        pygame.display.flip()

    def run(self) -> None:
        while self.running:
            self.clock.tick(self.FPS)
            self.event_handler()
            self.draw()


def run():
    lorenz_system = SingleAttractor()
    lorenz_system.run()


if __name__ == "__main__":
    run()
