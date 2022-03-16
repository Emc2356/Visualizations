# formulas taken from https://www.myphysicslab.com/pendulum/double-pendulum-en.html
import pygame
import math
import sys


class Visualization:
    def __init__(self) -> None:
        pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN])
        self.W: int = 600
        self.H: int = 600
        self.center: pygame.math.Vector2 = pygame.math.Vector2(self.W // 2, self.H // 4)
        self.WIN: pygame.surface.Surface = pygame.display.set_mode((self.W, self.H))

        self.running: bool = True
        self.draw_lines: bool = False
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.FPS: int = 60

        self.background: pygame.surface.Surface = pygame.surface.Surface(
            self.WIN.get_size()
        )

        self.background.fill((255, 255, 255))
        self.px2: float = 0
        self.py2: float = 0
        self.l1: float = 150
        self.l2: float = 150
        self.m1: float = 10
        self.m2: float = 10
        self.a1: float = 0
        self.a2: float = 0
        self.a1_v: float = 0.1
        self.a2_v: float = 0
        self.a1_a: float = 0
        self.a2_a: float = 0
        self.g: float = 1
        pygame.display.set_caption("Double pendulum")

    def calc_acceleration(self) -> None:
        # first pendulum
        num1 = -self.g * (2 * self.m1 + self.m2) * math.sin(self.a1)
        num2 = self.m2 * self.g * math.sin(self.a1 - 2 * self.a2)
        num3 = (
            2
            * math.sin(self.a1 - self.a2)
            * self.m2
            * (
                (self.a2_v * self.a2_v) * self.l2
                + (self.a1_v * self.a1_v) * self.l1 * math.cos(self.a1 - self.a2)
            )
        )
        den = self.l1 * (
            2 * self.m1 + self.m2 - self.m2 * math.cos(2 * self.a1 - 2 * self.a2)
        )
        self.a1_a = (num1 - num2 - num3) / den

        # second pendulum
        num1 = 2 * math.sin(self.a1 - self.a2)
        num2 = (self.a1_v * self.a1_v) * self.l1 * (self.m1 + self.m2)
        num3 = self.g * (self.m1 + self.m2) * math.cos(self.a1)
        num4 = (self.a2_v * self.a2_v) * self.l2 * self.m2 * math.cos(self.a1 - self.a2)
        den = self.l2 * (
            2 * self.m1 + self.m2 - self.m2 * math.cos(2 * self.a1 - 2 * self.a2)
        )
        self.a2_a = (num1 * (num2 + num3 + num4)) / den

        # change the angle variables
        self.a1_v += self.a1_a
        self.a2_v += self.a2_a
        self.a1 += self.a1_v
        self.a2 += self.a2_v

    def get_pos(self) -> list[tuple[float, float]]:
        x1 = self.l1 * math.cos(self.a1 + math.pi / 2) + self.center.x
        y1 = self.l1 * math.sin(self.a1 + math.pi / 2) + self.center.y

        x2 = x1 + self.l2 * math.cos(self.a2 + math.pi / 2)
        y2 = y1 + self.l2 * math.sin(self.a2 + math.pi / 2)
        return [(x1, y1), (x2, y2)]

    def draw(self) -> None:
        self.WIN.blit(self.background, (0, 0))

        self.calc_acceleration()
        [x1, y1], [x2, y2] = self.get_pos()

        pygame.draw.line(self.WIN, (0, 0, 0), self.center, (x1, y1), 1)
        pygame.draw.circle(self.WIN, (0, 0, 0), (x1, y1), self.m1)

        pygame.draw.line(self.WIN, (0, 0, 0), (x1, y1), (x2, y2), 1)
        pygame.draw.circle(self.WIN, (0, 0, 0), (x2, y2), self.m2)

        if self.draw_lines:
            pygame.draw.line(
                self.background, (0, 0, 0), (self.px2, self.py2), (x2, y2), 1
            )
        else:
            self.draw_lines = True
        self.px2, self.py2 = x2, y2
        pygame.display.update()

    def event_handler(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                pygame.quit()
                sys.exit()

    def run(self) -> None:
        while self.running:
            self.clock.tick(self.FPS)
            self.event_handler()
            self.draw()


def run() -> None:
    pygame.init()
    vis = Visualization()
    vis.run()


if __name__ == "__main__":
    run()
