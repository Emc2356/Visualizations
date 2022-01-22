import random
import pygame
import sys


class Game:
    def __init__(self):
        self.W: int = 750
        self.H: int = 750
        self.WIN: pygame.surface.Surface = pygame.display.set_mode((self.W, self.H))

        self.running: bool = True
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.FPS: int = 60

        self.angle: float = -1

        # how many times we are going to do the algorithm each frame
        self.ITERATIONS: int = 10000
        self.LENGTH: float = 1
        self.angle_change: float = 0.755  # random.uniform(0.5, 1)
        print(self.angle_change)
        # angles that look decent:
        # 0.5825336617933341
        # julia set like: 0.755
        # snowflake fractal like: 0.735

        center = pygame.math.Vector2(self.WIN.get_size()) // 2
        self.cure_pos: pygame.math.Vector2 = pygame.math.Vector2(center)
        self.prev_pos: pygame.math.Vector2 = pygame.math.Vector2(center)
        self.velocity: pygame.math.Vector2 = pygame.math.Vector2(0, self.LENGTH)

        self.WIN.fill((30, 30, 30))
        pygame.display.set_caption(f"Angle Drawing, angle={self.angle_change}")

    def event_handler(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    self.angle_change -= 0.01
                elif event.key == pygame.K_UP:
                    self.angle_change += 0.01
                else:
                    continue

                center = pygame.math.Vector2(self.WIN.get_size()) // 2
                self.cure_pos = pygame.math.Vector2(center)
                self.prev_pos = pygame.math.Vector2(center)
                self.velocity = pygame.math.Vector2(0, self.LENGTH)
                self.angle = -1
                print(self.angle_change)
                self.WIN.fill((30, 30, 30))
                pygame.display.set_caption(f"Angle Drawing, angle={self.angle_change}")

    def draw(self) -> None:
        points = []
        for i in range(self.ITERATIONS):
            self.velocity.rotate_ip(self.angle)

            self.cure_pos += self.velocity
            points.extend([tuple(self.cure_pos), tuple(self.prev_pos)])

            self.prev_pos.update(self.cure_pos)

            self.angle += self.angle_change

        pygame.draw.lines(self.WIN, (255, 255, 255), False, points)

        pygame.display.update()

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
