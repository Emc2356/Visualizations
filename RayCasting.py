from typing import Optional, Union
import pygame
import random
import sys


class Wall:
    def __init__(self, WIN: pygame.surface.Surface, ax: int, ay: int, bx: int, by: int) -> None:
        self.WIN: pygame.surface.Surface = WIN
        self.a: pygame.math.Vector2 = pygame.math.Vector2(ax, ay)
        self.b: pygame.math.Vector2 = pygame.math.Vector2(bx, by)

    def draw(self) -> None:
        pygame.draw.line(self.WIN, (255, 255, 255), self.a, self.b, 1)


class Ray:
    def __init__(self, pos: pygame.math.Vector2, angle: int) -> None:
        self.pos: pygame.math.Vector2 = pygame.math.Vector2(pos)
        self.angle: int = angle
        self.dir: pygame.math.Vector2 = pygame.math.Vector2(1, 0).rotate(angle)

    def look_at(self, x: int, y: int) -> None:
        self.dir.x = x - self.pos.x
        self.dir.y = y - self.pos.y
        self.dir.normalize()

    def get_casting_point(self, wall: Wall) -> Optional[pygame.math.Vector2]:
        x1 = wall.a.x
        y1 = wall.a.y
        x2 = wall.b.x
        y2 = wall.b.y

        x3 = self.pos.x
        y3 = self.pos.y
        x4 = self.pos.x + self.dir.x
        y4 = self.pos.y + self.dir.y

        den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if den == 0:  # line are parallel and they will never meet even if you stretch them out infinitely
            return

        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
        u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / den
        if t > 0 and t < 1 and u > 0:
            return pygame.math.Vector2(
                x1 + t * (x2 - x1),
                y1 + t * (y2 - y1)
            )
        else:
            return


class Source:
    def __init__(self, WIN: pygame.surface.Surface, x: int, y: int, radius: int=10, max_distance: float=float("inf")) -> None:
        self.WIN: pygame.surface.Surface = WIN
        self.pos: pygame.math.Vector2 = pygame.math.Vector2(x, y)
        self.max_distance: float = max_distance
        self.radius: int = radius
        self.rays: list[Ray] = []
        for a in range(0, 360, 1):  # angle in degrees
            self.rays.append(Ray(self.pos, a))

    def move(self, pos: Union[list[int], tuple[int, int]]):
        self.pos.x = pos[0]
        self.pos.y = pos[1]
        for ray in self.rays:
            ray.pos = self.pos

    def cast(self, walls: list[Wall]) -> None:
        for ray in self.rays:
            # closest = min([point for wall in walls
            #           if ((point := ray.get_casting_point(wall)) and (dist := self.pos.distance_to(point)) and dist <= self.max_distance)],
            #           key=lambda vector: self.pos.distance_to(vector), default=None)
            closest = None
            record = float("inf")
            for wall in walls:
                point = ray.get_casting_point(wall)
                if point:
                    dis = self.pos.distance_to(point)
                    if dis < record and dis <= self.max_distance:
                        record = dis
                        closest = point
            if closest:
                pygame.draw.line(self.WIN, (255, 255, 255), self.pos, closest, 1)

    def draw(self):
        pygame.draw.circle(self.WIN, (255, 255, 255), self.pos, self.radius)


class Visualization:
    def __init__(self) -> None:
        pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEMOTION])
        self.W: int = 750
        self.H: int = 750
        self.WIN: pygame.surface.Surface = pygame.display.set_mode((self.W, self.H))

        self.running: bool = True
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.FPS: int = 60

        self.source: Source = None
        self.walls: list[Wall] = []

        self.reset()

        pygame.display.set_caption("RayCasting")

    def reset(self) -> None:
        del self.source
        del self.walls
        self.source = Source(self.WIN, self.W//2, self.H//2)
        # the random walls
        self.walls = [Wall(self.WIN, random.randint(0, self.W), random.randint(0, self.H), random.randint(0, self.W), random.randint(0, self.H)) for _ in range(5)]
        # border walls so it has something to hit on all of the time (if the max_distance in the source is not inf)
        self.walls.append(Wall(self.WIN, 0, 0, self.W, 0))
        self.walls.append(Wall(self.WIN, self.W, 0, self.W, self.H))
        self.walls.append(Wall(self.WIN, self.W, self.H, 0, self.H))
        self.walls.append(Wall(self.WIN, 0, self.H, 0, 0))

    def draw(self) -> None:
        self.WIN.fill((0, 0, 0))
        [wall.draw() for wall in self.walls]
        self.source.draw()
        self.source.cast(self.walls)
        pygame.display.update()

    def event_handler(self) -> None:
        mods = pygame.key.get_mods()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and (mods & pygame.K_LCTRL):
                    self.reset()
            elif event.type == pygame.MOUSEMOTION:
                self.source.move(event.pos)

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
