from tkinter.filedialog import asksaveasfile
from typing import Dict, List
import random
import pygame
import time
import json
import sys


def valid_index(j: int, i: int, grid: List[List["Cell"]]) -> bool:
    return (j >= 0 and i >= 0) and (i < len(grid) and j < len(grid[i]))


green = (0, 255, 0)
purple = (148, 0, 211)
dark_purple = (216, 191, 216)


class Cell:
    def __init__(
        self,
        WIN: pygame.surface.Surface,
        j: int,
        i: int,
        res: int,
        grid: List[List["Cell"]],
    ):
        self.WIN: pygame.surface.Surface = WIN
        self.j: int = j
        self.i: int = i
        self.res = res
        self.x: int = j * res
        self.y: int = i * res
        self.highlighted: bool = False
        self.visited: bool = False

        self.grid: List[List[Cell]] = grid

        self.walls: Dict[str, bool] = {
            "top": True,
            "right": True,
            "bottom": True,
            "left": True,
        }

        self.corner_cords = {
            "topleft": [self.x, self.y],
            "topright": [self.x + res, self.y],
            "bottomright": [self.x + res, self.y + res],
            "bottomleft": [self.x, self.y + res],
        }

        self.border_cords: Dict[str, list[List[int]]] = {
            "top": [self.corner_cords["topleft"], self.corner_cords["topright"]],
            "right": [self.corner_cords["topright"], self.corner_cords["bottomright"]],
            "bottom": [
                self.corner_cords["bottomright"],
                self.corner_cords["bottomleft"],
            ],
            "left": [self.corner_cords["bottomleft"], self.corner_cords["topleft"]],
        }

    def visit(self) -> None:
        self.visited = True

    def leave(self) -> None:
        self.highlighted = False

    def highlight(self) -> None:
        self.highlighted = True

    def draw(self) -> None:
        color = green if self.highlighted else (purple if self.visited else dark_purple)
        pygame.draw.rect(self.WIN, color, [self.x, self.y, self.res, self.res])
        for key, value in self.walls.items():
            if value:
                pygame.draw.line(self.WIN, (0, 0, 0), *self.border_cords[key], 1)

    def merge(self, other) -> None:
        if other.j == self.j and other.i + 1 == self.i:  # other is on the top
            self.walls["top"] = False
            other.walls["bottom"] = False
        elif other.j - 1 == self.j and other.i == self.i:  # other is on the right
            self.walls["right"] = False
            other.walls["left"] = False
        elif other.j == self.j and other.i - 1 == self.i:  # other is on the bottom
            self.walls["bottom"] = False
            other.walls["top"] = False
        elif other.j + 1 == self.j and other.i == self.i:  # other is on the left
            self.walls["left"] = False
            other.walls["right"] = False
        else:
            print("the cell isn't a neighbor")
            return None

    def get_neighbors(self) -> List["Cell"]:
        neighbors = []

        if valid_index(self.j, self.i - 1, self.grid):  # top neighbor
            neighbors.append(self.grid[self.i - 1][self.j])
        if valid_index(self.j + 1, self.i, self.grid):  # right neighbor
            neighbors.append(self.grid[self.i][self.j + 1])
        if valid_index(self.j, self.i + 1, self.grid):  # bottom neighbor
            neighbors.append(self.grid[self.i + 1][self.j])
        if valid_index(self.j - 1, self.i, self.grid):  # left neighbor
            neighbors.append(self.grid[self.i][self.j - 1])

        return neighbors

    def random_neighbor(self) -> "Cell" or None:
        neighbors = self.get_neighbors()
        new_neighbors = []

        for neighbor in neighbors:
            if not neighbor.visited:
                new_neighbors.append(neighbor)

        if new_neighbors:
            return random.choice(new_neighbors)
        else:
            return None


class Game:
    def __init__(self, W: int, H: int, res: int):
        pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN])
        self.W: int = W
        self.H: int = H
        self.WIN: pygame.surface.Surface = pygame.display.set_mode((self.W, self.H))

        self.res: int = res
        self.rows: int = self.W // self.res
        self.columns: int = self.H // self.res

        self.running: bool = True
        self.finished: bool = False
        self.starting_time: float = time.time()
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.FPS: int = 0
        self.algorithm_iteration: int = 1  # up this number to make the algorithm go faster for larger mazes put it high so it gets completed faster
        self.single_cell_update: bool = False if self.algorithm_iteration > 1 else True

        self.grid: List[List[Cell]] = []
        self.current_cell: Cell = None
        self.starting_cell: Cell = None
        self.path: List[Cell] = []
        self.reset()

        pygame.display.set_caption("Maze Generation with Iterative implementation")

    def reset(self) -> None:
        self.grid: List[List[Cell]] = []

        for i in range(self.columns):
            self.grid.append([])
            for j in range(self.rows):
                self.grid[i].append(Cell(self.WIN, j, i, self.res, self.grid))

        self.current_cell: Cell = self.grid[0][0]
        self.current_cell.visit()
        self.current_cell.highlight()
        self.starting_cell: Cell = self.current_cell

        self.path: List[Cell] = [self.current_cell]
        if self.single_cell_update:
            self.draw()
        self.finished = False
        self.starting_time = time.time()

    def event_handler(self) -> None:
        mods = pygame.key.get_mods()
        for event in pygame.event.get():  # type: pygame.event.Event
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if mods & pygame.K_LCTRL:
                    if event.key == pygame.K_r:
                        self.reset()
                    if event.key == pygame.K_s:
                        if self.finished:
                            self.save_maze()

    def save_maze(self) -> None:
        file_extensions = [
            ["JSON files", "*.json"],
            ["Python files", "*.py"],
            ["All files", "*.*"],
        ]
        f = asksaveasfile(
            filetypes=file_extensions,
            defaultextension=file_extensions,
            title="Save As",
            initialfile="untitled",
            mode="w",
        )
        if f is not None:
            try:
                filename = f.name
                if filename.endswith(".py"):
                    data: str = f"""
from typing import Dict, List, Union, Tuple
import pygame
import sys


def valid_index(j: int, i: int, grid: List[List["Cell"]]) -> bool:
    return (j >= 0 and i >= 0) and (i < len(grid) and j < len(grid[i]))


class Cell:
    def __init__(self, WIN: pygame.surface.Surface, res: int, j: int, i: int, walls: Dict[str, Union[bool, int]]):
        self.WIN: pygame.surface.Surface = WIN
        self.j: int = j
        self.i: int = i
        self.res = res
        self.x: int = j * res
        self.y: int = i * res

        self.walls: Dict[str, bool] = walls

        self.corner_cords = {{
            "topleft": [self.x, self.y],
            "topright": [self.x + res, self.y],
            "bottomright": [self.x + res, self.y + res],
            "bottomleft": [self.x, self.y + res]
        }}

        self.border_cords: Dict[str, list[List[int]]] = {{
            "top": [self.corner_cords["topleft"], self.corner_cords["topright"]],
            "right": [self.corner_cords["topright"], self.corner_cords["bottomright"]],
            "bottom": [self.corner_cords["bottomright"], self.corner_cords["bottomleft"]],
            "left": [self.corner_cords["bottomleft"], self.corner_cords["topleft"]]
        }}

    def draw(self, cell_color: Union[List[int], Tuple[int, int, int]]=(216, 191, 216), border_color: Union[List[int], Tuple[int, int, int]]=(0, 0, 0)) -> None:
        pygame.draw.rect(self.WIN, cell_color, [self.x, self.y, self.res, self.res])
        for key, value in self.walls.items():
            if value:
                pygame.draw.line(self.WIN, border_color, *self.border_cords[key], 1)

    def get_neighbors(self, grid: List[List["Cell"]]):
        neighbors = []

        if valid_index(self.j, self.i - 1, self.grid):  # top neighbor
            neighbors.append(self.grid[self.i - 1][self.j])
        if valid_index(self.j + 1, self.i, self.grid):  # right neighbor
            neighbors.append(self.grid[self.i][self.j + 1])
        if valid_index(self.j, self.i + 1, self.grid):  # bottom neighbor
            neighbors.append(self.grid[self.i + 1][self.j])
        if valid_index(self.j - 1, self.i, self.grid):  # left neighbor
            neighbors.append(self.grid[self.i][self.j - 1])

        return neighbors

res: int = {self.res}
rows: int = {self.rows}
columns: int = {self.columns}
W: int = {self.W}
H: int = {self.H}
WIN: pygame.surface.Surface = pygame.display.set_mode((W, H))
grid: List[List[Cell]] = {f'''{[[f"Cell(WIN, res, {cell.j}, {cell.i}, {cell.walls})" for cell in row] for row in self.grid]}'''.replace('"', "").replace("True", "1").replace("False", "0")}
running: bool = True
clock: pygame.time.Clock = pygame.time.Clock()
FPS: int = 60

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit(-1)
    WIN.fill((0, 0, 0))
    for row in grid:
        for cell in row:
            cell.draw()
    pygame.display.update()
"""[
                        1:
                    ]
                    f.write(data)
                else:
                    data: Dict[str, any] = {
                        "map": [
                            [
                                {"j": cell.j, "i": cell.i, "walls": cell.walls}
                                for cell in row
                            ]
                            for row in self.grid
                        ],
                        "rows": self.rows,
                        "columns": self.columns,
                        "res": self.grid[0][0].res,
                        "start": [self.starting_cell.i, self.starting_cell.j],
                        "end": [len(self.grid) - 1, len(self.grid[0]) - 1],
                        "screen_size": {"width": self.W, "height": self.H},
                    }
                    json.dump(data, f, indent=4)
            finally:
                f.close()

    def algorithm(self) -> None:
        if not self.finished:
            for _ in range(self.algorithm_iteration):
                next_cell: Cell = self.current_cell.random_neighbor()
                if next_cell:
                    next_cell.visit()
                    next_cell.highlight()
                    self.path.append(next_cell)
                    self.current_cell.merge(next_cell)
                    self.current_cell.leave()
                    if self.single_cell_update:
                        self.draw_cells([self.current_cell, next_cell])
                    self.current_cell = next_cell
                else:
                    if self.path:
                        self.current_cell.leave()
                        next_cell = self.path.pop()
                        next_cell.visit()
                        next_cell.highlight()
                        if self.single_cell_update:
                            self.draw_cells([self.current_cell, next_cell])
                        self.current_cell = next_cell
                    else:
                        self.finished = True
                        pygame.display.update()
                        print(
                            f"for a maze with {self.columns * self.rows} cells it took: {time.time() - self.starting_time}s"
                        )

    def draw_cells(self, cells: List["Cell"]) -> None:
        for cell in cells:
            cell.draw()
        pygame.display.update(
            [
                min([cell.x for cell in cells]) - self.res,
                min([cell.y for cell in cells]) - self.res,
                self.res * 4,
                self.res * 4,
            ]
        )

    def draw(self) -> None:
        self.WIN.fill((0, 0, 0))
        for row in self.grid:
            for cell in row:
                cell.draw()
        pygame.display.update()

    def run(self) -> None:
        if self.single_cell_update:
            self.draw()
        while self.running:
            self.clock.tick(self.FPS)
            self.event_handler()
            self.algorithm()
            if not self.single_cell_update:
                self.draw()


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser(description="A maze generation visualization")
    parser.add_argument("--w", type=int, default=1200, help="the width of the window")
    parser.add_argument("--h", type=int, default=750, help="the height of the window")
    parser.add_argument("--res", type=int, default=5, help="the size of the cells")

    args = parser.parse_args()

    pygame.init()

    game = Game(args.w, args.h, args.res)
    game.run()
