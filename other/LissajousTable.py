import colorsys
import pygame
import math
import sys
import os


class Curve:
    def __init__(self) -> None:
        self.points = []
        self.current = pygame.math.Vector2()

    @property
    def x(self):
        return self.current.x

    @x.setter
    def x(self, v):
        self.current.x = v

    @property
    def y(self):
        return self.current.y

    @y.setter
    def y(self, v):
        self.current.y = v

    def draw(self, screen, clr):
        if len(self.points) > 1:
            pygame.draw.lines(screen, clr, False, self.points, 2)
        self.points.append(self.current)
        self.current = pygame.math.Vector2()


class Game:
    def __init__(self):
        self.W: int = 1400
        self.H: int = 700
        self.WIN: pygame.surface.Surface = pygame.display.set_mode((self.W, self.H))

        self.size: int = 100
        self.rows: int = self.W//self.size - 1
        self.columns: int = self.H//self.size - 1

        self.running: bool = True
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.FPS: int = 60

        self.time: float = 0  # going to use radians cause i dont want to go from degrees to radians every frame :P

        self.curves = [[Curve() for j in range(self.rows)] for i in range(self.columns)]

        pygame.display.set_caption("Lissajous Curve Table")

    def event_handler(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()

    def draw(self) -> None:
        self.WIN.fill((30, 30, 30))

        buffer = 2

        pos = pygame.math.Vector2(self.size, self.size)/2 + pygame.math.Vector2(buffer, buffer)
        for i in range(self.columns):
            pos.y += self.size
            pygame.draw.circle(self.WIN, (255, 255, 255), pos, self.size/2 - buffer, 1)
            point_pos = pos + ((self.size/2 - 2) * math.cos(self.time * (i + 1)), (self.size/2 - 2) * math.sin(self.time * (i + 1)))
            pygame.draw.circle(
                self.WIN,
                (255, 255, 255),
                point_pos,
                3
            )
            pygame.draw.line(self.WIN, (255, 255, 255), (0, point_pos.y), (self.W, point_pos.y), 1)
            for r in range(self.rows):
                self.curves[i][r].y = point_pos.y

        pos = pygame.math.Vector2(self.size, self.size)/2 + pygame.math.Vector2(buffer, buffer)
        for j in range(self.rows):
            pos.x += self.size
            pygame.draw.circle(self.WIN, (255, 255, 255), pos, self.size/2 - buffer, 1)
            point_pos = pos + ((self.size/2 - 2) * math.cos(self.time * (j + 1)), (self.size/2 - 2) * math.sin(self.time * (j + 1)))
            pygame.draw.circle(
                self.WIN,
                (255, 255, 255),
                point_pos,
                3
            )
            pygame.draw.line(self.WIN, (255, 255, 255), (point_pos.x, 0), (point_pos.x, self.H), 1)
            for c in range(self.columns):
                self.curves[c][j].x = point_pos.x

        self.time += math.pi/300

        for row in self.curves:
            for curve in row:
                curve.draw(self.WIN, (255, 0, 0))

        pygame.display.update()

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
