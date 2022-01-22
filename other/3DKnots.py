# http://paulbourke.net/geometry/knots/

from typing import List, Tuple
from math import pi, sin, cos
from OpenGL.GL import *
import pygame
import time
import sys


class Game:
    def __init__(self):
        self.W: int = 500
        self.H: int = 500
        self.WIN: pygame.surface.Surface = pygame.display.set_mode(
            (self.W, self.H), pygame.DOUBLEBUF | pygame.OPENGL
        )

        self.running: bool = True
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.FPS: int = 60

        self.vectors: List[Tuple[float, float, float]] = []
        self.color_data: List[Tuple[int, int, int]] = []

        self.beta: float = 0
        self.timestep: float = 500

        pygame.display.set_caption("3D Konts with pygame/OpenGL")
        glOrtho(-250, 250, 250, -250, 250, -250)

        self.last_time: float = time.time()
        self.dt = (time.time() - self.last_time) * self.FPS
        self.last_time = time.time()

    def event_handler(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.vectors.clear()
                self.color_data.clear()
                self.beta = 0

    def draw(self) -> None:
        r = 100 * (0.8 + 1.6 * sin(6 * self.beta))
        theta = 2 * self.beta
        phi = 0.6 * pi * sin(12 * self.beta)
        x = r * cos(phi) * cos(theta)
        y = r * cos(phi) * sin(theta)
        z = r * sin(phi)

        self.beta += pi / self.timestep
        if len(self.vectors) - 1 < self.timestep:
            self.vectors.append((x, y, z))
            self.color_data.append((255, int(r), 255))

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glRotatef(self.dt, 0, 1, 0)
        glLineWidth(2)
        glBegin(GL_LINE_STRIP)
        for pt, clr in zip(self.vectors, self.color_data):
            glColor3fv(clr)
            glVertex3dv(pt)
        glEnd()
        pygame.display.flip()

    def run(self) -> None:
        while self.running:
            self.dt = (time.time() - self.last_time) * self.FPS
            self.last_time = time.time()
            self.clock.tick(self.FPS)
            self.event_handler()
            self.draw()


def run():
    game = Game()
    game.run()


if __name__ == "__main__":
    run()
