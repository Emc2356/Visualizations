from typing import Dict, List, Union
import random
import pygame
import json
import sys


def valid_index(j, i, grid) -> bool:
    try:
        if j < 0 or i < 0:
            raise IndexError
        x = grid[i][j]
        return True
    except IndexError:
        return False


green = (0, 255, 0)
purple = (148, 0, 211)
dark_purple = (216, 191, 216)
red = (255, 0, 0)


class Cell:

    def __init__(self, WIN: pygame.surface.Surface, j: int, i: int, res: int, grid: List[List["Cell"]]):
        self.WIN: pygame.surface.Surface = WIN
        self.j: int = j
        self.i: int = i
        self.res = res
        self.x: int = j * res
        self.y: int = i * res
        self.rect: pygame.Rect = pygame.Rect(self.x, self.y, res, res)
        self.highlighted: bool = False
        self.visited: bool = False
        self.dead_end: bool = False
        self.one_dir: bool = False

        self.grid: List[List[Cell]] = grid

        self.walls: Dict[str, bool] = {
            "top": True,
            "right": True,
            "bottom": True,
            "left": True
        }

        self.corner_cords = {
            "topleft": [self.x, self.y],
            "topright": [self.x + res, self.y],
            "bottomright": [self.x + res, self.y + res],
            "bottomleft": [self.x, self.y + res]
        }

        self.border_cords: Dict[str, list[List[int]]] = {
            "top": [self.corner_cords["topleft"], self.corner_cords["topright"]],
            "right": [self.corner_cords["topright"], self.corner_cords["bottomright"]],
            "bottom": [self.corner_cords["bottomright"], self.corner_cords["bottomleft"]],
            "left": [self.corner_cords["bottomleft"], self.corner_cords["topleft"]]
        }

        self.neighbors: List[Cell] = []

    def calc_neighbors(self) -> None:
        self.neighbors.clear()

        if valid_index(self.j, self.i - 1, self.grid):  # top neighbor
            self.neighbors.append(self.grid[self.i - 1][self.j])
        if valid_index(self.j + 1, self.i, self.grid):  # right neighbor
            self.neighbors.append(self.grid[self.i][self.j + 1])
        if valid_index(self.j, self.i + 1, self.grid):  # bottom neighbor
            self.neighbors.append(self.grid[self.i + 1][self.j])
        if valid_index(self.j - 1, self.i, self.grid):  # left neighbor
            self.neighbors.append(self.grid[self.i][self.j - 1])

    def visit(self) -> None:
        self.visited = True

    def forget(self) -> None:
        self.visited = False
        self.highlighted = False

    def leave(self) -> None:
        self.highlighted = False

    def silent_kill(self) -> None:
        self.dead_end = True

    def highlight(self) -> None:
        self.highlighted = True

    def draw_base(self) -> None:
        pygame.draw.rect(self.WIN, dark_purple if not self.highlighted else green, [self.x, self.y, self.res, self.res])
        for key, value in self.walls.items():
            if value:
                pygame.draw.line(self.WIN, (0, 0, 0), *self.border_cords[key], 1)

    def draw(self) -> None:
        color = green if self.highlighted else (purple if self.visited and not self.dead_end else (red if self.dead_end else dark_purple))
        pygame.draw.rect(self.WIN, color, [self.x, self.y, self.res, self.res])
        for key, value in self.walls.items():
            if value:
                pygame.draw.line(self.WIN, (0, 0, 0), *self.border_cords[key], 1)

    def get_location(self, other) -> Union[str, None]:
        if other.j == self.j and other.i + 1 == self.i:  # other is on the top
            return "top"
        elif other.j - 1 == self.j and other.i == self.i:  # other is on the right
            return "right"
        elif other.j == self.j and other.i - 1 == self.i:  # other is on the bottom
            return "bottom"
        elif other.j + 1 == self.j and other.i == self.i:  # other is on the left
            return "left"
        else:
            print("the cell isn't a neighbor")
            return

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
        return self.neighbors

    def get_available_neighbors(self) -> List["Cell"]:
        neighbors = list(filter(lambda ne: not ne.visited and not ne.dead_end, self.get_neighbors()))
        for i, neighbor in sorted(enumerate(neighbors), reverse=True):
            location = self.get_location(neighbor)
            if location == "top" and neighbor.walls["bottom"]: neighbors.pop(i)
            if location == "right" and neighbor.walls["left"]: neighbors.pop(i)
            if location == "bottom" and neighbor.walls["top"]: neighbors.pop(i)
            if location == "left" and neighbor.walls["right"]: neighbors.pop(i)
        return neighbors

    def random_neighbor(self) -> "Cell" or None:
        neighbors = list(filter(lambda neighbor: not neighbor.visited, self.get_neighbors()))
        if neighbors: return random.choice(neighbors)
        return None


class Game:
    def __init__(self):
        self.W: int = 600
        self.H: int = 600
        self.WIN: pygame.surface.Surface = pygame.display.set_mode((self.W, self.H))

        self.res: int = 25
        self.rows: int = self.W // self.res
        self.columns: int = self.H // self.res

        self.running: bool = True
        self.finished: bool = False
        self.algorithm_iteration: int = 1  # change this for the algorithm to go faster
        self.single_cell_update: bool = True if self.algorithm_iteration == 1 else False
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.FPS: int = 0

        self.grid: List[List[Cell]] = []
        self.current_cell: Cell = None
        self.starting_cell: Cell = None
        self.end_cell: Cell = None
        self.prev_cell: Cell = None
        self.path_taken_to_draw: List[Cell] = []
        self.path: List[Cell] = []

        self.reset()

        pygame.display.set_caption("Maze solving")

    def reset(self) -> None:
        with open("./maze.json", "r") as f:
            data = json.loads(f.read())

        self.W = data["screen_size"]["width"]
        self.H = data["screen_size"]["height"]
        self.WIN = pygame.display.set_mode((self.W, self.H))
        self.res = data["res"]
        self.rows = self.W // self.res
        self.columns = self.H // self.res

        self.grid.clear()
        self.finished = False
        for row in data["map"]:
            self.grid.append([])
            for cell_info in row:
                self.grid[cell_info["i"]].append(
                    Cell(self.WIN, cell_info["j"], cell_info["i"], self.res, self.grid)
                )
                self.grid[cell_info["i"]][cell_info["j"]].walls = cell_info["walls"]
        for row in self.grid:
            for cell in row:
                cell.calc_neighbors()
        self.current_cell = self.grid[data["start"][0]][data["start"][1]]
        self.starting_cell = self.current_cell
        self.current_cell.highlight()
        self.current_cell.visit()
        self.path = [self.current_cell]
        self.end_cell = self.grid[data["end"][0]][data["end"][1]]
        self.path_taken_to_draw: List[Cell] = [self.starting_cell]
        if self.single_cell_update: self.draw()

    def event_handler(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.reset()

    def algorithm(self) -> None:
        if not self.finished:
            for i in range(self.algorithm_iteration):
                next_cells = self.current_cell.get_available_neighbors()
                if next_cells:
                    next_cell = random.choice(next_cells)
                    self.current_cell.leave()
                    self.current_cell.dead_end = False
                    next_cell.dead_end = False
                    next_cell.highlight()
                    next_cell.visit()
                    self.path.append(next_cell)
                    if self.single_cell_update: self.draw_cells([self.current_cell, next_cell])
                    self.current_cell = next_cell
                else:
                    if self.path:
                        next_cell = self.path[-1]
                        self.current_cell.leave()
                        self.current_cell.silent_kill()
                        next_cell.silent_kill()
                        next_cell.highlight()
                        next_cell.visit()
                        if not next_cell.get_available_neighbors():
                            next_cell.silent_kill()
                            self.path.pop()
                        if self.single_cell_update: self.draw_cells([self.current_cell, next_cell])
                        self.current_cell = next_cell
                if self.current_cell == self.end_cell:
                    self.finished = True
                    break

    def draw_cells(self, cells: List["Cell"]) -> None:
        for cell in cells:
            cell.draw()
        pygame.display.update([min([cell.x for cell in cells]), min([cell.y for cell in cells]), self.res*4, self.res*4])

    def draw(self) -> None:
        self.WIN.fill((0, 0, 0))
        if not self.finished:
            for row in self.grid:
                for cell in row:
                    cell.draw()
        else:
            for row in self.grid:
                for cell in row:
                    cell.draw_base()
            for cell in self.path:
                cell.draw()
        pygame.display.update()

    def run(self) -> None:
        while self.running:
            self.clock.tick(self.FPS)
            self.event_handler()
            self.algorithm()
            if not self.single_cell_update or self.finished: self.draw()


if __name__ == '__main__':
    game = Game()
    game.run()
