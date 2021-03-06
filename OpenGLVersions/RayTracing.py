from __future__ import annotations

import moderngl as mgl
import moderngl_window as mglw
import numpy as np
import glm

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
SAMPLES: int = 32


class RayTracing(mglw.WindowConfig):
    gl_version = 4, 4
    aspect_ratio = aspect_ratio
    window_size = SCREEN_SIZE
    resizable = False
    title = "Ray Tracing"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.FPS: int = 60

        self.sphere_count: int = 3

        self.initialize_program()

    def initialize_program(self):
        self.program: mgl.Program = self.ctx.program(
            vertex_shader=read_file(
                os.path.join(shader_dir, "RayTracing.vert")
            ),
            fragment_shader=read_file(
                os.path.join(shader_dir, "RayTracing.frag")
            )
        )

        arr = np.array([
            #  x     y    z    w
            # first triangle
            -1.0, -1.0, 0.0, 1.0,
            -1.0, +1.0, 0.0, 1.0,
            +1.0, -1.0, 0.0, 1.0,
            # second triangle
            -1.0, +1.0, 0.0, 1.0,
            +1.0, -1.0, 0.0, 1.0,
            +1.0, +1.0, 0.0, 1.0,
        ], dtype="f4")

        self.vbo = self.ctx.buffer(arr)
        self.vao = self.ctx.simple_vertex_array(self.program, self.vbo, "in_vert")

        buffer_data = np.fromiter(self.gen_initial_data(), dtype="f4")
        self.sphere_buffer = self.ctx.buffer(buffer_data)

        vfov = 100

        theta = glm.radians(vfov)
        h = glm.tan(theta / 2)
        print(h)
        viewport_height = 2.0 * h
        viewport_width = aspect_ratio * viewport_height
        focal_length = 1.0
        origin = glm.vec3(0, 0, 0)
        horizontal = glm.vec3(viewport_width, 0.0, 0.0)
        vertical = glm.vec3(0.0, viewport_height, 0.0)
        lower_left_corner = origin - horizontal / 2 - vertical / 2 - glm.vec3(0, 0, focal_length)

        self.program["origin"] = tuple(origin)
        self.program["horizontal"] = tuple(horizontal)
        self.program["vertical"] = tuple(vertical)
        self.program["lower_left_corner"] = tuple(lower_left_corner)

        self.program["aspect_ratio"] = aspect_ratio
        self.program["resolution"] = SCREEN_SIZE
        self.program["width"] = W
        self.program["height"] = H
        self.program["samples"] = SAMPLES

        self.program["SphereCount"] = self.sphere_count

        self.sphere_buffer.bind_to_storage_buffer(0)

    def gen_initial_data(self):
        """Generator function creating the initial buffer data"""
        yield from [
            +1.0, +0.0, -1.0, +0.4,  # x, y, z, radius
            +1.0, +0.0, +0.0, +1.0,  # r, g, b, a
            +0.4, +0.0, +0.0, +0.0,  # reflectivity, emission
        ]

        yield from [
            +0.0, +0.0, -1.0, +0.4,  # x, y, z, radius
            +0.0, +1.0, +0.0, +1.0,  # r, g, b, a
            +0.4, +0.0, +0.0, +0.0,  # reflectivity, emission
        ]

        yield from [
            -1.0, +0.0, -1.0, +0.4,  # x, y, z, radius
            +0.0, +0.0, +1.0, +1.0,  # r, g, b, a
            +0.4, +0.0, +0.0, +0.0,  # reflectivity, emission
        ]

    @classmethod
    def run(cls):
        mglw.run_window_config(cls)

    def key_event(self, key, action, modifiers):
        if key == self.wnd.keys.R:
            if modifiers.ctrl != 0:
                if action == self.wnd.keys.ACTION_PRESS:
                    print("reloading shaders...")
                    self.initialize_program()

    def render(self, time: float, frame_time: float):
        self.clock.tick(self.FPS)

        self.ctx.clear(0, 0, 0, 0)

        self.program["time"] = time

        self.vao.render(mgl.TRIANGLES)


if __name__ == "__main__":
    if "--window" not in sys.argv:
        sys.argv.append("--window")
        sys.argv.append("pygame2")
    RayTracing.run()
