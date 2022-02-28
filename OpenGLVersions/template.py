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
aspect_ratio: float = 16 / 9
W: int = 1000
H: int = int(W / aspect_ratio)
SCREEN_SIZE: tuple[int, int] = W, H


class MandelbrotSet(mglw.WindowConfig):
    gl_version = 4, 4
    aspect_ratio = aspect_ratio
    window_size = SCREEN_SIZE
    resizable = False
    title = "Template"

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
            vertex_shader="""#version 330
            in vec2 pos;

            void main() {
                gl_Position = vec4(pos, 0.0, 1.0);
            }
            """,
            fragment_shader="""#version 330
            #ifdef GL_ES
            precision mediump float;
            #endif
            
            uniform vec2 resolution;  // Canvas size (width, height)
            uniform float time;       // time since
            
            void main(){
                vec2 st = gl_FragCoord.xy/resolution.xy;
            
                gl_FragColor = vec4(st, 0.0, 1.0) * vec4(abs(sin(time)));
            }
            """,
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

    @classmethod
    def run(cls):
        mglw.run_window_config(cls)

    def render(self, time: float, frame_time: float):
        self.ctx.clear(0, 0, 0, 0)

        self.program["resolution"] = SCREEN_SIZE
        self.program["time"].value = time

        self.vao.render(mgl.TRIANGLES)


if __name__ == "__main__":
    if "--window" not in sys.argv:
        sys.argv.append("--window")
        sys.argv.append("pygame2")
    MandelbrotSet.run()
