# more information can be found here:
# https://en.wikipedia.org/wiki/L-system

from typing import Callable, Dict, List
import pygame
import sys


W: int = 750
H: int = 750


class System:
    variables: List[str]  # the name of the strings that are going to grow
    constants: List[str]  # the name of the string that will stay static
    axiom: str  # the starting point
    angle: int  # if it is going to turn by how much
    rules: Dict[str, str]  # include all of your strings here, even if they are static
    commands: Dict[str, Callable]  # what each string means
    start: pygame.math.Vector2
    velocity: pygame.math.Vector2

    name: str  # name of the l system
    order: int  # not important

    fraction: float  # by how much the size of the velocity will be decreased in each progress call

    pos: pygame.math.Vector2  # the starting point for the l system
    velocity: pygame.math.Vector2  # were it will be looking and heading

    def __init__(self) -> None:
        self.setup()

    # if you want to do anything extra on startup you need to override setup
    def setup(self) -> None:
        ...

    @classmethod
    def progress(cls) -> None:
        cls.order += 1

        cls.velocity /= cls.fraction

        cls.axiom = "".join(cls.rules[char] for char in cls.axiom)

    @classmethod
    def draw(cls, surface: pygame.surface.Surface) -> None:
        if len(cls.axiom) < 2:
            return

        pos = pygame.math.Vector2(cls.pos)
        velocity = pygame.math.Vector2(cls.velocity)

        pygame.draw.lines(
            surface,
            (255, 255, 255),
            False,
            [cls.commands[char](pos, velocity, cls.angle) for char in cls.axiom],
        )


class Systems:
    class DragonCurve(System):
        name = "Dragon Curve"

        order = 0

        fraction = 1.1

        variables = ["F", "G"]
        constants = ["-", "+"]

        axiom = "F"
        angle = 90

        rules = {"F": "F+G", "G": "F-G", "-": "-", "+": "+"}

        commands = {
            "F": lambda pos, vel, angle: pygame.math.Vector2(
                (pos.update(pos + vel), pos)[1]
            ),
            "G": lambda pos, vel, angle: pygame.math.Vector2(
                (pos.update(pos + vel), pos)[1]
            ),
            "+": lambda pos, vel, angle: pygame.math.Vector2(
                (pos, vel.rotate_ip(+angle))[0]
            ),
            "-": lambda pos, vel, angle: pygame.math.Vector2(
                (pos, vel.rotate_ip(-angle))[0]
            ),
        }

        pos = pygame.math.Vector2(W // 2, H // 2 - 100)
        velocity = pygame.math.Vector2(5, 0)

    class KochCurve(System):
        name = "Koch Curve"

        order = 0

        fraction = 1.1

        variables = ["F"]
        constants = ["-", "+"]

        axiom = "F"
        angle = 90

        rules = {"F": "F+F-F-F+F", "-": "-", "+": "+"}

        commands = {
            "F": lambda pos, vel, angle: pygame.math.Vector2(
                (pos.update(pos + vel), pos)[1]
            ),
            "+": lambda pos, vel, angle: pygame.math.Vector2(
                (pos, vel.rotate_ip(-angle))[0]
            ),
            "-": lambda pos, vel, angle: pygame.math.Vector2(
                (pos, vel.rotate_ip(+angle))[0]
            ),
        }

        pos = pygame.math.Vector2(0, H)
        velocity = pygame.math.Vector2(5, 0)

    class SierpinskiTriangle(System):
        name = "Sierpinski triangle"

        order = 0

        fraction = 1.1

        variables = ["F", "G"]
        constants = ["-", "+"]

        axiom = "F-G-G"
        angle = 120

        rules = {"F": "F-G+F+G-F", "G": "GG", "-": "-", "+": "+"}

        commands = {
            "F": lambda pos, vel, angle: pygame.math.Vector2(
                (pos.update(pos + vel), pos)[1]
            ),
            "G": lambda pos, vel, angle: pygame.math.Vector2(
                (pos.update(pos + vel), pos)[1]
            ),
            "+": lambda pos, vel, angle: pygame.math.Vector2(
                (pos, vel.rotate_ip(+angle))[0]
            ),
            "-": lambda pos, vel, angle: pygame.math.Vector2(
                (pos, vel.rotate_ip(-angle))[0]
            ),
        }

        pos = pygame.math.Vector2(0, H)
        velocity = pygame.math.Vector2(5, 0)

    class SierpinskiArrowheadCurve(System):
        name = "Sierpiński arrowhead curve"

        order = 0

        fraction = 1.3

        variables = ["A", "B"]
        constants = ["-", "+"]

        axiom = "A"
        angle = 60

        rules = {"A": "B-A-B", "B": "A+B+A", "-": "-", "+": "+"}

        commands = {
            "A": lambda pos, vel, angle: pygame.math.Vector2(
                (pos.update(pos + vel), pos)[1]
            ),
            "B": lambda pos, vel, angle: pygame.math.Vector2(
                (pos.update(pos + vel), pos)[1]
            ),
            "+": lambda pos, vel, angle: pygame.math.Vector2(
                (pos, vel.rotate_ip(+angle))[0]
            ),
            "-": lambda pos, vel, angle: pygame.math.Vector2(
                (pos, vel.rotate_ip(-angle))[0]
            ),
        }

        pos = pygame.math.Vector2(0, H)
        velocity = pygame.math.Vector2(5, 0)

        def setup(self) -> None:
            super().progress()

        @classmethod
        def progress(cls) -> None:
            super().progress()
            super().progress()

    class FractalTree(System):
        name = "Fractal tree"

        order = 0

        fraction = 1.6

        variables = ["F", "X"]
        constants = ["-", "+", "[", "]"]

        axiom = "F"
        angle = 25

        rules = {
            "F": "FF+[+F-F-F]-[-F+F+F]",
            "+": "+",
            "-": "-",
            "[": "[",
            "]": "]",
        }
        # this system uses its own method as it needs a stack to function
        commands = {}

        pos = pygame.math.Vector2(W // 2, H)
        velocity = pygame.math.Vector2(0, -50)

        # sadly we have to override because we need that LIFO queue
        @classmethod
        def draw(cls, surface: pygame.surface.Surface) -> None:
            if len(cls.axiom) < 2:
                return

            pos = pygame.math.Vector2(cls.pos)
            vel = pygame.math.Vector2(cls.velocity)
            # a simple LIFO (Last In First Out) queue
            stack = []

            for char in cls.axiom:
                if char == "F":
                    pygame.draw.line(surface, (255, 255, 255), pos, pos + vel, 1)
                    pos += vel
                elif char == "+":
                    vel.rotate_ip(cls.angle)
                elif char == "-":
                    vel.rotate_ip(-cls.angle)
                elif char == "[":
                    stack.append((pygame.math.Vector2(pos), pygame.math.Vector2(vel)))
                elif char == "]":
                    pos, vel = stack.pop()
                else:
                    print(char)

    class FractalPlant(System):
        name = "Fractal plant"

        order = 0

        fraction = 1.5

        variables = ["F", "X"]
        constants = ["-", "+", "[", "]"]

        axiom = "X"
        angle = 25

        rules = {
            "F": "FF",
            "X": "F+[[X]-X]-F[-FX]+X",
            "+": "+",
            "-": "-",
            "[": "[",
            "]": "]",
        }
        # this system uses its own method as it needs a stack to function
        commands = {}

        pos = pygame.math.Vector2(200, H)
        velocity = pygame.math.Vector2(0, -20).rotate(angle)

        # sadly we have to override because we need that LIFO queue
        @classmethod
        def draw(cls, surface: pygame.surface.Surface) -> None:
            if len(cls.axiom) < 2:
                return

            pos = pygame.math.Vector2(cls.pos)
            vel = pygame.math.Vector2(cls.velocity)
            # a simple LIFO (Last In First Out) queue
            stack = []

            for char in cls.axiom:
                if char == "X":
                    continue
                elif char == "F":
                    pygame.draw.line(surface, (255, 255, 255), pos, pos + vel, 1)
                    pos += vel
                elif char == "+":
                    vel.rotate_ip(-cls.angle)
                elif char == "-":
                    vel.rotate_ip(+cls.angle)
                elif char == "[":
                    stack.append((pygame.math.Vector2(pos), pygame.math.Vector2(vel)))
                elif char == "]":
                    pos, vel = stack.pop()


class Game:
    def __init__(self):
        self.WIN: pygame.surface.Surface = pygame.display.set_mode((W, H))

        self.running: bool = True
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.FPS: int = 60

        # Systems:
        # DragonCurve
        # KochCurve
        # SierpinskiTriangle
        # SierpinskiArrowheadCurve
        # FractalTree
        # FractalPlant

        self.system: System = Systems.DragonCurve()

        pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1}))

    def event_handler(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.system.progress()
                    self.draw()
                    pygame.display.set_caption(
                        f"LSystem: {self.system.name}, order={self.system.order}"
                    )

    def draw(self) -> None:
        self.WIN.fill((30, 30, 30))

        self.system.draw(self.WIN)

        pygame.display.update()

    def run(self) -> None:
        while self.running:
            self.clock.tick(self.FPS)
            self.event_handler()


def run():
    game = Game()
    game.run()


if __name__ == "__main__":
    run()
