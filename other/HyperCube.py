from typing import List, Tuple, Union
import OpenGL.GL as GL
import pygame
import math
import sys


class Vector4:
    __slots__ = "x", "y", "z", "w"

    def __init__(self, x: float = 0, y: float = 0, z: float = 0, w: float = 0):
        self.x: float = x
        self.y: float = y
        self.z: float = z
        self.w: float = w

    def mult(self, f: float) -> "Vector4":
        self.x *= f
        self.y *= f
        self.z *= f
        self.w *= f
        return self

    def toMatrix(self) -> List[List[float]]:
        return [[self.x], [self.y], [self.z], [self.w]]

    @staticmethod
    def fromMatrix(m: Union[List[List[float]]]) -> "Vector4":
        return Vector4(m[0][0], m[1][0], m[2][0], 0 if len(m) < 4 else m[3][0])

    def __getitem__(self, index: int) -> float:
        return [self.x, self.y, self.z, self.w][index]

    def __len__(self) -> int:
        return 4


def matmul(a, b):
    if isinstance(b, Vector4):
        return Vector4.fromMatrix(matmul(a, b.toMatrix()))

    colsA = len(a[0])
    rowsA = len(a)
    colsB = len(b[0])
    rowsB = len(b)

    if colsA != rowsB:
        raise IndexError("Columns of A must match rows of B")

    return [
        [sum([a[j][n] * b[n][i] for n in range(colsA)]) for i in range(colsB)]
        for j in range(rowsA)
    ]


def CreateHyperCubePoints() -> List[Vector4]:
    return [
        Vector4(-1, -1, -1, 1),
        Vector4(1, -1, -1, 1),
        Vector4(1, 1, -1, 1),
        Vector4(-1, 1, -1, 1),
        Vector4(-1, -1, 1, 1),
        Vector4(1, -1, 1, 1),
        Vector4(1, 1, 1, 1),
        Vector4(-1, 1, 1, 1),
        Vector4(-1, -1, -1, -1),
        Vector4(1, -1, -1, -1),
        Vector4(1, 1, -1, -1),
        Vector4(-1, 1, -1, -1),
        Vector4(-1, -1, 1, -1),
        Vector4(1, -1, 1, -1),
        Vector4(1, 1, 1, -1),
        Vector4(-1, 1, 1, -1),
    ]


class Game:
    def __init__(self):
        self.W: int = 500
        self.H: int = 500
        WIN_FLAGS = pygame.OPENGL | pygame.DOUBLEBUF
        self.WIN: pygame.surface.Surface = pygame.display.set_mode(
            (self.W, self.H), WIN_FLAGS
        )

        self.running: bool = True
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.FPS: int = 60

        self.vertices: List[List[float]] = []
        self.color_data: List[Tuple[float]] = []

        self.rotations: List[int] = [0, 0, 0, 0]

        self.points: List[Vector4] = CreateHyperCubePoints()

        self.timestep: float = math.pi / 3000
        self.time: float = -self.timestep

        GL.glOrtho(-1, 1, 1, -1, 1, -1)
        GL.glRotate(-90, 1, 0, 0)

        pygame.display.set_caption("Hyper Cube (4D Cube or Tesseract)")

    def event_handler(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                pygame.quit()
                sys.exit()

    def connect(self, offset, i, j, points):
        a = points[i + offset]
        b = points[j + offset]
        GL.glVertex3d(a.x, a.y, a.z)
        GL.glVertex3d(b.x, b.y, b.z)

    def calculate_rotations(
        self,
    ) -> Tuple[List[List[Union[int, float]]], List[List[Union[int, float]]]]:
        self.time += self.timestep
        c, s = math.cos(self.time), math.sin(self.time)
        return [[c, -s, 0, 0], [s, c, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]], [
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, c, -s],
            [0, 0, s, c],
        ]

    def draw(self) -> None:
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        projected3d = []

        GL.glPointSize(7)
        GL.glBegin(GL.GL_POINTS)
        for i, point in enumerate(self.points):
            rotationXY, rotationZW = self.calculate_rotations()

            rotated = matmul(rotationXY, point)
            rotated = matmul(rotationZW, rotated)

            distance = 2
            w = 1 / (distance - rotated.w)

            projection = [
                [w, 0, 0, 0],
                [0, w, 0, 0],
                [0, 0, w, 0],
            ]

            projected = matmul(projection, rotated)
            projected.mult(0.3)
            projected3d.append(projected)
            GL.glVertex3dv(projected[:3])
        GL.glEnd()

        GL.glLineWidth(1)
        GL.glBegin(GL.GL_LINES)
        # connecting
        for i in range(4):
            self.connect(0, i + 4, ((i + 1) % 4) + 4, projected3d)
            self.connect(8, i + 4, ((i + 1) % 4) + 4, projected3d)
            self.connect(0, i, (i + 1) % 4, projected3d)
            self.connect(8, i, (i + 1) % 4, projected3d)
            self.connect(0, i, i + 4, projected3d)
            self.connect(8, i, i + 4, projected3d)

        for i in range(8):
            self.connect(0, i, i + 8, projected3d)
        GL.glEnd()

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
