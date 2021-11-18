from typing import List, Tuple
import OpenGL.GLU as GLU
import OpenGL.GL as GL
import itertools
import colorsys
import pygame
import math
import sys
import os


class Game:
    def __init__(self):
        self.W: int = 500
        self.H: int = 500
        WIN_FLAGS = pygame.OPENGL | pygame.DOUBLEBUF
        self.WIN: pygame.surface.Surface = pygame.display.set_mode((self.W, self.H), WIN_FLAGS)

        self.running: bool = True
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.FPS: int = 60

        # values taken from https://en.wikipedia.org/wiki/Lorenz_system
        self.x: float = 0.01
        self.y: float = 0
        self.z: float = 0

        self.a: float = 10
        self.b: float = 28
        self.c: float = 8 / 3

        self.dt: float = 0.01

        self.vertices: List[List[float]] = [[0, 0, 0]]
        self.color_data: List[Tuple[float]] = [colorsys.hsv_to_rgb(1/255, 1, 1)]

        self.rotations: List[int] = [1, 1, 1, 1]

        pygame.display.set_caption("Lorenz System")

        GL.glOrtho(-1, 1, 1, -1, 1, -1)
        GL.glTranslate(-50/self.W, -50/self.H, 0)  # this is what i call pulling numbers from your ass

    def update(self) -> None:
        dx = (self.a * (self.y - self.x)) * self.dt
        dy = (self.x * (self.b - self.z) - self.y) * self.dt
        dz = (self.x * self.y - self.c * self.z) * self.dt
        self.x = self.x + dx
        self.y = self.y + dy
        self.z = self.z + dz

        self.vertices.append([self.x/60, self.y/60, self.z/60])
        self.color_data.append(colorsys.hsv_to_rgb((len(self.color_data))/255, 1, 1))

    def event_handler(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()

    def draw(self) -> None:
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        GL.glRotatef(*self.rotations)
        GL.glBegin(GL.GL_LINE_STRIP)
        for pt, clr in zip(self.vertices, self.color_data):
            GL.glColor3fv(clr)
            GL.glVertex3dv(pt)
        GL.glEnd()

        # GL.glEnableClientState(GL.GL_VERTEX_ARRAY)
        # GL.glEnableClientState(GL.GL_COLOR_ARRAY)
        #
        # GL.glColorPointer(3, GL.GL_FLOAT, 0, self.color_data)
        # GL.glVertexPointer(2, GL.GL_FLOAT, 0, self.vertices)
        # GL.glDrawElements(GL.GL_LINE_STRIP, len(self.color_data), GL. GL_UNSIGNED_INT, )
        #
        # GL.glDisableClientState(GL.GL_VERTEX_ARRAY)
        # GL.glDisableClientState(GL.GL_COLOR_ARRAY)

        pygame.display.flip()

    def run(self) -> None:
        while self.running:
            self.clock.tick(self.FPS)
            self.event_handler()
            self.update()
            self.draw()


def run():
    game = Game()
    game.run()


if __name__ == '__main__':
    run()
