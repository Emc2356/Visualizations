from math import sqrt, inf as infinity
from typing import *
import numba as nb
import numpy as np
import pygame
import sys
import os


CORES = os.cpu_count()

Ray = nb.float64[:, :]  # index 0 is origin, index 1 is direction
vec3 = nb.float64[:]

BLACK_COLOR = np.array([0.0, 0.0, 0.0])
WHITE_COLOR = np.array([1.0, 1.0, 1.0])
BLUE_COLOR  = np.array([0.5, 0.7, 1.0])

SphereSize = 3 + 1  # how many "bytes" or just slots the array will have

aspect_ratio = 16 / 9
W = 880  # 1200
H = int(W / aspect_ratio)

SAMPLES = 16
DEPTH = 8

random_values = np.random.uniform(0, 0.999999999, (H, W, SAMPLES))   # calculate all of them in one batch

viewport_height = 2
viewport_width = aspect_ratio * viewport_height
focal_length = 1

origin = np.array([0, 0, 0])
horizontal = np.array([viewport_width, 0, 0])
vertical = np.array([0, viewport_height, 0])
lower_left_corner = origin - horizontal/2 - vertical/2 - np.array([0, 0, focal_length])


def show_array_as_image(array: np.ndarray):
    WIN = pygame.display.set_mode((W, H))
    pygame.surfarray.blit_array(WIN, array)
    WIN.blit(pygame.transform.flip(WIN, False, True), (0, 0))
    pygame.display.update()

    while True:
        event = pygame.event.wait()
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            pygame.quit()
            sys.exit(-1)


@nb.njit
def clamp(v: float, mini: float, maxi: float) -> float:
    return mini if v < mini else maxi if v > maxi else v


@nb.njit
def create_sphere(center: vec3, r: float) -> np.ndarray:
    arr = np.zeros((SphereSize,))  # 3 for vec3, 1 for r
    arr[0:3] = center
    arr[3] = r
    return arr


@nb.njit
def create_hittable_collection(count: int):
    return np.zeros((count, SphereSize))


@nb.njit
def hittable_collection_hit(hittables: np.ndarray, ray: Ray, t_min: float, t_max: float, rec: np.ndarray) -> bool:
    temp_rec = create_blank_hit_record()
    hit_anything = False
    closest_so_far = t_max

    for i in range(len(hittables)):
        sphere = hittables[i]
        if sphere_hit(sphere, ray, t_min, closest_so_far, temp_rec):
            hit_anything = True
            closest_so_far = temp_rec[6]
            rec[:] = temp_rec[:]

    return hit_anything


@nb.njit
def sphere_hit(sphere: np.ndarray, ray: Ray, t_min: float, t_max: float, rec: np.ndarray) -> bool:
    radius = sphere[3]
    center = sphere[0:3]
    oc = ray[0] - center
    a = dot(ray[1], ray[1])
    half_b = dot(oc, ray[1])
    c = dot(oc, oc) - radius*radius

    discriminant = half_b*half_b - a*c
    if discriminant < 0:
        return False
    sqrtd = sqrt(discriminant)

    root = (-half_b - sqrtd) / a
    if root < t_min or t_max < root:
        root = (-half_b + sqrtd) / a
        if root < t_min or t_max < root:
            return False

    rec[6] = root
    rec[0:3] = ray_at(ray, rec[6])
    rec[3:6] = (rec[0:3] - center) / radius

    return True


@nb.njit
def random_in_unit_sphere():
    while True:
        v = np.random.random((3,)) * 2 - 1
        if sqrt(dot(v, v)) >= 1:
            continue
        return v


@nb.njit
def random_unit_vector():
    unit_vector(random_in_unit_sphere())


@nb.njit
def random_in_hemisphere(normal: vec3):
    in_unit_sphere = random_in_unit_sphere()
    if dot(in_unit_sphere, normal) > 0.0:
        return in_unit_sphere
    return -in_unit_sphere


@nb.njit
def create_blank_hit_record():
    arr = np.zeros((3 + 3 + 1 + 1,))
    arr[0:3] = 0  # "p", (np.float64, (3,))
    arr[3:6] = 0  # "normal", (np.float64, (3,))
    arr[6] = 0  # "t", np.float64
    arr[7] = 0  # "front_face", bool or just np.int64
    return arr


@nb.njit
def hit_record_set_face_normal(rec: np.ndarray, ray: Ray, outward_normal: vec3):
    rec[7] = int(dot(ray[1], outward_normal) < 0)
    rec[3:6] = rec[7] if outward_normal else -outward_normal


@nb.njit
def ray_at(ray: Ray, t: float) -> np.ndarray:
    return ray[0] + ray[1] * t


@nb.njit
def unit_vector(arr: vec3):  # normalizing a vector
    return arr / sqrt(np.sum(arr * arr))


@nb.njit
def dot(a: vec3, b: vec3) -> vec3:
    return np.sum(a * b)


@nb.njit
def ray_color(ray: Ray, world: np.ndarray, depth: int) -> np.ndarray:
    rec = create_blank_hit_record()

    if depth <= 0:
        return BLACK_COLOR

    if hittable_collection_hit(world, ray, 0.001, infinity, rec):
        target = rec[0:3] + rec[3:6] + random_in_hemisphere(rec[3:6])
        r = np.zeros((2, 3))
        r[0] = rec[0:3]
        r[1] = target - rec[0:3]
        return 0.5 * ray_color(r, world, depth - 1)

    unit_direction = unit_vector(ray[1])
    t = 0.5 * (unit_direction[1] + 1.0)
    return (1.0 - t) * WHITE_COLOR + t * BLUE_COLOR


@nb.njit
def write_color(j: int, i: int, rgb: np.ndarray, arr: np.ndarray) -> None:
    r = int(255 * clamp(sqrt(rgb[0] / SAMPLES), 0, 0.999))
    g = int(255 * clamp(sqrt(rgb[1] / SAMPLES), 0, 0.999))
    b = int(255 * clamp(sqrt(rgb[2] / SAMPLES), 0, 0.999))

    arr[j, i] = r, g, b


@nb.njit
def _render_on_array(out: np.ndarray) -> None:
    width = out.shape[0]
    height = out.shape[1]
    ray = np.zeros((2, 3))
    world = create_hittable_collection(2)
    world[0] = create_sphere(np.array([0, 0, -1]), 0.5)
    world[1] = create_sphere(np.array([0, -100.5, -1]), 100)

    # if something already exists there is no reason to re-compute it
    ray[0] = origin

    for j in range(width):
        for i in range(height):
            color = np.zeros((3,))
            for s in range(SAMPLES):
                u = (i + random_values[j, i, s]) / (height - 1)
                v = (j + random_values[j, i, s]) / (width - 1)
                ray[1] = lower_left_corner + u * horizontal + vertical * v - origin
                color += ray_color(ray, world, DEPTH)
            write_color(j, i, color, out)
        p = int(j / width * 100)
        print("[" + ("=" * p) + ("-" * (100 - p)) + "]")
    print("[" + "="*100 + "]")


def render(out: Optional[np.ndarray]=None) -> np.ndarray:
    if out is None:
        out = np.zeros((H, W, 3), dtype=np.uint64)
    _render_on_array(out)
    return out


print("compiling...")
render(np.zeros((2, 2, 3)))

print("computing...")
show_array_as_image(render().transpose((1, 0, 2)))
