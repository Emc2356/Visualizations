from typing import List, Tuple, Optional
import pygame
import sys


class Visualization:
    def __init__(self):
        pygame.display.set_caption("Sudoku Solver with backtracking")
        self.W: int = 500
        self.H: int = 500
        self.WIN: pygame.surface.Surface = pygame.display.set_mode((self.W, self.H))

        self.running: bool = True
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.FPS: int = 10

        self.font: pygame.font.Font = pygame.font.Font(None, 50)

        self.board: List[List[int]] = [
            [7, 8, 0, 4, 0, 0, 1, 2, 0],
            [6, 0, 0, 0, 7, 5, 0, 0, 9],
            [0, 0, 0, 6, 0, 1, 0, 7, 8],
            [0, 0, 7, 0, 4, 0, 2, 6, 0],
            [0, 0, 1, 0, 5, 0, 9, 3, 0],
            [9, 0, 4, 0, 6, 0, 0, 0, 5],
            [0, 7, 0, 3, 0, 0, 0, 1, 2],
            [1, 2, 0, 0, 0, 7, 4, 0, 0],
            [0, 4, 9, 2, 0, 6, 0, 0, 7]
        ]
        self.sequence: List[List[List[int]]] = []

        self.grid_surf: pygame.surface.Surface = pygame.surface.Surface(self.WIN.get_size())
        self.grid_surf.fill((30, 30, 30))
        for rect in [pygame.Rect(i*self.W//9, j*self.H//9, self.W//9, self.H//9) for j in range(len(self.board[0])) for i in range(len(self.board))]:
            pygame.draw.rect(self.grid_surf, (255, 255, 255), rect, 2)

        self.solve()

        self.show_sequence()

    def solve(self) -> bool:
        try:
            for i in range(len(self.board)):
                for j in range(len(self.board[0])):
                    if self.board[i][j] == 0:
                        col, row = j, i
                        raise StopIteration
        except StopIteration: pass
        else: return True

        for i in range(1, 10):
            if not self.valid_spot(i, (row, col)):
                continue
            self.board[row][col] = i
            self.sequence.append([[v for v in row] for row in self.board])

            if self.solve():
                return True

            self.board[row][col] = 0
        return False

    def valid_spot(self, move: int, pos: Tuple[int, int]) -> bool:
        bx, by = pos[1] // 3, pos[0] // 3
        return not (
            any([(self.board[pos[0]][i] == move and pos[1] != i) for i in range(len(self.board[0]))]) or
            any([(self.board[i][pos[1]] == move and pos[0] != i) for i in range(len(self.board))]) or
            any([(self.board[i][j] == move and (i, j) != pos) for j in range(bx * 3, bx * 3 + 3) for i in range(by * 3, by * 3 + 3)])
        )

    def draw_board(self) -> None:
        self.WIN.fill((30, 30, 30))
        self.WIN.blit(self.grid_surf, (0, 0))

        for i, row in enumerate(self.board):
            for j, v in enumerate(row):
                label = self.font.render(str(v), True, (255, 255, 255))
                self.WIN.blit(label, (j * self.W//9 + (self.W//9)//2 - label.get_width()//2, i * self.H//9 + (self.H//9)//2 - label.get_height()//2))

        pygame.display.update()

    def show_sequence(self) -> None:
        for step in self.sequence:
            self.clock.tick(self.FPS)
            self.board = step.copy()
            self.event_handler()
            self.draw_board()

    def event_handler(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()

    def run(self) -> None:
        while self.running:
            self.clock.tick(self.FPS)
            self.event_handler()


def run() -> None:
    pygame.init()
    vis = Visualization()
    vis.run()


if __name__ == '__main__':
    run()
