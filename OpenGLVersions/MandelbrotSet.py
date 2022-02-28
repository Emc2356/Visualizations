from __future__ import annotations

import moderngl as mgl
import moderngl_window as mglw
import glm
import numpy as np

import pygame
import sys
import os


def read_file(path: str) -> str:
    with open(path, "r") as f:
        return f.read()


shader_dir: str = os.path.join(".", "data", "shaders")
W: int = 1000
H: int = int(W / 1.5)
SCREEN_SIZE: tuple[int, int] = W, H


class BaseMglWindow(mglw.WindowConfig):
    gl_version = 4, 4
    title = "Base ModernGL Window"
    window_size = 500, 500
    aspect_ratio = 1
    resizable = False

    @classmethod
    def run(cls):
        mglw.run_window_config(cls)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)


class MandelbrotSet(BaseMglWindow):
    title = "Mandelbrot Set"
    window_size = SCREEN_SIZE
    aspect_ratio = 1.5

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.running: bool = True
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.FPS: int = 60

        self.re_start: float = -2
        self.re_end: float = 1
        self.im_start: float = -1
        self.im_end: float = 1

        self.program: mgl.Program = self.ctx.program(
            vertex_shader=read_file(
                os.path.join(shader_dir, "MandelbrotSet_vert.glsl")
            ),
            fragment_shader=read_file(
                os.path.join(shader_dir, "MandelbrotSet_frag.glsl")
            ),
        )

        arr = np.array([
            # x    y
            # first triangle
            -1.0, -1.0,
            -1.0, +1.0,
            +1.0, -1.0,
            # second triangle
            -1.0, +1.0,
            +1.0, -1.0,
            +1.0, +1.0,
        ], dtype="f4")

        self.vbo = self.ctx.buffer(arr)
        self.vao = self.ctx.simple_vertex_array(self.program, self.vbo, "pos")

    def mouse_scroll_event(self, x_offset: float, y_offset: float):
        scroll = y_offset
        x, y = pygame.mouse.get_pos()
        x = (x / W) * (self.re_end - self.re_start) + self.re_start
        y = (y / H) * (self.im_end - self.im_start) + self.im_start

        if scroll < 0:
            new_width = (self.re_end - self.re_start) * 1.5 * abs(scroll)
            new_height = (self.im_end - self.im_start) * 1.5 * abs(scroll)
        else:
            new_width = (self.re_end - self.re_start) / 1.5 * abs(scroll)
            new_height = (self.im_end - self.im_start) / 1.5 * abs(scroll)
        self.re_start = x - new_width / 2
        self.re_end = x + new_width / 2
        self.im_start = y - new_height / 2
        self.im_end = y + new_height / 2

    def render(self, time: float, frame_time: float):
        self.program["resolution"] = SCREEN_SIZE
        self.program["RE_START"] = self.re_start
        self.program["RE_END"] = self.re_end
        self.program["IM_START"] = self.im_end
        self.program["IM_END"] = self.im_start
        self.program["detail"] = 1000
        self.program["infinity"] = 50

        self.vao.render(mgl.TRIANGLES)


if __name__ == "__main__":
    if "--window" not in sys.argv:
        sys.argv.append("--window")
        sys.argv.append("pygame2")
    MandelbrotSet.run()
