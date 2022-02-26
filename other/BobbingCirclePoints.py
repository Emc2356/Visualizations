import pygame
import math
import sys
import os


# (r, phi)
def from_polar(r, phi) -> pygame.math.Vector2:
    v = pygame.math.Vector2()
    v.from_polar((r, math.degrees(phi)))
    return v


DRAW_LINES: bool = True
DRAW_POINTS: bool = True
DRAW_CIRCLE: bool = True


class Game:
    def __init__(self):
        self.W: int = 500
        self.H: int = 500
        self.WIN: pygame.surface.Surface = pygame.display.set_mode((self.W, self.H))

        self.center: pygame.math.Vector2 = self.WIN.get_rect().center

        self.running: bool = True
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.FPS: int = 60

        self.radius: int = 200

        self.N: int = 1

        self.progress: float = math.pi / 200
        self.time: float = 0

        pygame.display.set_caption("Boobing Circle points")

    def update(self) -> None:
        pass

    def event_handler(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                key = event.key
                if key == pygame.K_UP or key == pygame.K_SPACE:
                    self.N += 1
                if key == pygame.K_DOWN:
                    self.N = max(1, self.N - 1)

    def draw(self) -> None:
        self.WIN.fill((0, 0, 0))

        if DRAW_CIRCLE:
            pygame.draw.circle(self.WIN, (255, 255, 255), self.center, self.radius, 1)

        offset = self.time
        theta = 0  # θ to flex the theta char
        for i in range(self.N):
            pos0 = from_polar(self.radius, theta) + self.center
            pos1 = from_polar(self.radius, theta + math.pi) + self.center
            if DRAW_LINES:
                pygame.draw.line(self.WIN, (255, 255, 255), pos0, pos1, 1)

            if DRAW_POINTS:
                point_pos = pos0.lerp(pos1, (math.sin(offset) + 1) / 2)

                pygame.draw.circle(self.WIN, (255, 255, 255), point_pos, 3)

            offset += math.pi / self.N
            theta += math.pi / self.N

        pygame.display.update()

        self.time += self.progress

    def run(self) -> None:
        while self.running:
            self.clock.tick(self.FPS)
            self.event_handler()
            self.update()
            self.draw()


def run():
    game = Game()
    game.run()


if __name__ == "__main__":
    run()
