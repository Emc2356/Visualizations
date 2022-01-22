import pygame
import sys


BLUE = 0xEC015A
PINK = 0x2DC5F4
YELLOW = 0xFCEE21


class Visualization:
    def __init__(self):
        self.W: int = 750
        self.H: int = 750
        self.WIN: pygame.surface.Surface = pygame.display.set_mode((self.W, self.H))

        self.running: bool = True
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.FPS: int = 60

        self.iteration: int = 0

        self.draw()

    def draw(self) -> None:
        pygame.display.set_caption(f"Infinite Squares n={self.iteration}")
        self.draw_square(0, 0, self.W, False, 0)
        pygame.display.update()

    def event_handler(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.iteration += 1
                self.draw()

    def draw_square(self, x: float, y: float, w: float, is_pink, count) -> None:
        if is_pink:
            clr = PINK
        else:
            clr = BLUE
        pygame.draw.rect(self.WIN, YELLOW, (x, y, w, w), 2)
        pygame.draw.rect(self.WIN, clr, (x + 0.5, y + 0.5, w - 1, w - 1))

        if count < self.iteration and not is_pink:
            if count % 2 == 1:
                is_pink = not is_pink
            w /= 2

            self.draw_square(x, y, w, (is_pink := not is_pink), count + 1)
            self.draw_square(x + w, y, w, (is_pink := not is_pink), count + 1)
            self.draw_square(x + w, y + w, w, (is_pink := not is_pink), count + 1)
            self.draw_square(x, y + w, w, (is_pink := not is_pink), count + 1)

    def run(self) -> None:
        while self.running:
            self.clock.tick(self.FPS)
            self.event_handler()


def run() -> None:
    pygame.init()
    vis = Visualization()
    vis.run()


if __name__ == "__main__":
    run()
