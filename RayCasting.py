from typing import Union
import pygame
import random
import sys


class Source:
    def __init__(self, WIN: pygame.surface.Surface, x: int, y: int, radius: int=5, max_distance: float=float("inf"), ray_generation: Union[list[int], tuple[int, int, int]]=(0, 360, 1)) -> None:
        self.WIN: pygame.surface.Surface = WIN
        self.pos: pygame.math.Vector2 = pygame.math.Vector2(x, y)
        self.max_distance: float = max_distance
        self.radius: int = radius
        self.rays: list[pygame.math.Vector2] = []
        for a in range(*ray_generation):  # angle in degrees
            self.rays.append(pygame.math.Vector2(1, 0).rotate(a).normalize())  # it contains the direction of the ray

    def move(self, pos: Union[list[int], tuple[int, int], pygame.math.Vector2]) -> None:
        self.pos.x = pos[0]
        self.pos.y = pos[1]

    def cast(self, walls: Union[list[list[int]], tuple[tuple[int]], list[tuple[int]], tuple[list[int]]], color: Union[list[int], tuple[int, int, int]]=(255, 255, 255)) -> None:
        for ray in self.rays:
            x3, y3, x4, y4 = self.pos.x, self.pos.y, self.pos.x + ray.x, self.pos.y + ray.y
            record = float("inf")
            closest = None
            for wall in walls:
                x1, y1, x2, y2 = wall
                den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
                if den == 0:  # line are parallel and they will never meet even if you stretch them out infinitely
                    continue

                t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
                u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / den

                if 0 <= t <= 1 and 0 <= u:
                    p = pygame.math.Vector2(x1 + t * (x2 - x1), y1 + t * (y2 - y1))
                    dis = self.pos.distance_to(p)
                    if dis < record and dis <= self.max_distance:
                        record = dis
                        closest = p
            if closest:
                pygame.draw.line(self.WIN, color, self.pos, closest, 1)

    def draw(self, color: Union[list[int], tuple[int, int, int]]=(255, 255, 255)) -> None:
        pygame.draw.circle(self.WIN, color, self.pos, self.radius)


class Visualization:
    def __init__(self) -> None:
        pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN])
        self.W: int = 750
        self.H: int = 750
        self.WIN: pygame.surface.Surface = pygame.display.set_mode((self.W, self.H))

        self.running: bool = True
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.FPS: int = 60

        self.source: Union[Source, None] = None
        self.walls: list[list[int]] = []

        self.reset()

        pygame.display.set_caption("RayCasting")

    def reset(self) -> None:
        del self.source
        del self.walls
        self.source = Source(self.WIN, self.W//2, self.H//2)
        # the random walls
        self.walls = [[random.randint(0, self.W), random.randint(0, self.H), random.randint(0, self.W), random.randint(0, self.H)] for _ in range(5)]
        # border walls so it has something to hit on all of the time (if the max_distance in the source is not inf)
        self.walls.append([0, 0, self.W, 0])
        self.walls.append([self.W, 0, self.W, self.H])
        self.walls.append([self.W, self.H, 0, self.H])
        self.walls.append([0, self.H, 0, 0])

    def draw(self) -> None:
        self.WIN.fill((0, 0, 0))
        for wall in self.walls:
            pygame.draw.line(self.WIN, (255, 255, 255), wall[:2], wall[2:], 1)
        self.source.draw()
        self.source.cast(self.walls)
        pygame.display.update()

    def event_handler(self) -> None:
        self.source.move(pygame.mouse.get_pos())
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and (pygame.key.get_mods() & pygame.K_LCTRL):
                    self.reset()

    def run(self) -> None:
        while self.running:
            self.clock.tick(self.FPS)
            print(self.clock.get_fps())
            self.event_handler()
            self.draw()


def run() -> None:
    pygame.init()
    vis = Visualization()
    vis.run()


if __name__ == '__main__':
    run()
