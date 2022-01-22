from typing import Tuple, Callable
from argparse import ArgumentParser
from math import floor, ceil, log
from typing import List, Union
from PIL import Image
import numba as nb
import numpy as np
import time
import sys
import os


def check_args(arg: Union[str, List[str]]):
    if isinstance(arg, str):
        if arg in sys.argv:
            sys.argv.remove(arg)
            return True
        return False
    else:
        ret = False  # to remove all of the arguments that it finds
        for a in arg:
            if a in sys.argv:
                sys.argv.remove(a)
                ret = True
        return ret


if check_args(["-h", "-help", "--h", "--help"]):
    print(
        "|-------- mandelbrot set --------| \n"
        "[-p {val}] the precision of the set, aka the iterations \n"
        "[-i {val}] the break off point of the mandelbrot set \n"
        "[-s {val}] the width of the mandelbrot set, the height is calculated by width/1.5 \n"
        "[--save] it saves the output image \n"
        "[--run] it pops up a window that shows the mandelbrot set with zooming capability \n"
        "[--rainbow] whether the set is going to be rainbow-ish or not \n"
        "[--BW] whether the set is going to be black and white or not \n"
    )
    sys.exit()

print("compiling...")

PRECISION = 500
INFINITY = 2

# Image size (pixels)
WIDTH = 600
HEIGHT = int(WIDTH / 1.5)

# constants for the complex plain
# the real axis (or x axis)
RE_START = -2
RE_END = 1
# "imaginary" or lateral axis (or y axis)
IM_START = -1
IM_END = 1

CORES = os.cpu_count()

RAINBOW = False
RUN = False
SAVE = False
BW = False


@nb.njit("float64(float64, float64, float64)")
def _lerp(a: float, b: float, t: float) -> float:
    return a * (1 - t) + b * t


@nb.njit()
def hsv_to_rgb(h: float, s: float, v: float):
    C = v * s
    X = C * (1 - abs((h / 60) % 2 - 1))
    m = int(v - C)

    if h < 60:
        return int(255 * C + m), int(255 * X + m), m
    if h < 120:
        return int(255 * X + m), int(255 * C + m), m
    if h < 180:
        return m, int(255 * C + m), int(255 * X + m)
    if h < 240:
        return m, int(255 * X + m), int(255 * C + m)
    if h < 300:
        return int(255 * X + m), m, int(255 * C + m)
    return int(255 * C + m), m, int(255 * X + m)


@nb.njit("complex128(int64, int64, int64, int64, float64, float64, float64, float64)")
def _index_to_complex(
    i: int,
    j: int,
    width: int,
    height: int,
    re_start: float,
    re_end: float,
    im_start: float,
    im_end: float,
) -> complex:
    return complex(
        re_start + (i / width) * (re_end - re_start),
        im_start + (j / height) * (im_end - im_start),
    )


@nb.njit("float64(complex128, int64, float64)", fastmath=True, nogil=True)
def _mandelbrot_at_green(c: complex, precision: int, infinity: float) -> float:
    z = complex(0, 0)
    for i in range(precision):
        z = z * z + c  # Zn+1 = Zn^2 + C
        if abs(z) > infinity:
            return i + 1 - log(log(abs(z)))
    return precision


@nb.njit("float64(complex128, int64, float64)", fastmath=True, nogil=True)
def _mandelbrot_at(c: complex, precision: int, infinity: float) -> float:
    z = complex(0, 0)
    for i in range(precision):
        z = z * z + c  # Zn+1 = Zn^2 + C
        if abs(z) > infinity:
            return i
    return precision


@nb.njit(parallel=True)
def _mandelbrot_set_green(
    out: np.ndarray,
    precision: int,
    infinity: float,
    re_start: float,
    re_end: float,
    im_start: float,
    im_end: float,
):
    width = out.shape[0]
    height = out.shape[1]

    histogram = np.zeros(precision)
    values = np.zeros(out.shape[:2])

    for start in nb.prange(CORES):
        for x in range(start, width, CORES):
            for y in range(height):
                # calculate C then do the iterations
                m = _mandelbrot_at_green(
                    _index_to_complex(
                        x, y, width, height, re_start, re_end, im_start, im_end
                    ),
                    precision,
                    infinity,
                )
                values[x, y] = m
                if m < precision:
                    histogram[floor(m)] += 1

    total = histogram.sum()
    np.divide(histogram, total, histogram)

    hues = np.zeros(
        precision,
    )
    h = 0
    for i in range(precision):
        h += histogram[i]
        hues[i] = h
    hues[precision] = h

    for start in nb.prange(CORES):
        for x in range(start, width, CORES):
            for y in range(height):
                m = values[x, y]
                out[x, y] = hsv_to_rgb(
                    360 - int(360 * _lerp(hues[floor(m)], hues[ceil(m)], m % 1)),
                    1,
                    1 if m < precision else 0,
                )


@nb.njit(parallel=True)
def _mandelbrot_set_BW(
    out: np.ndarray,
    precision: int,
    infinity: float,
    re_start: float,
    re_end: float,
    im_start: float,
    im_end: float,
):
    width = out.shape[0]
    height = out.shape[1]
    for start in nb.prange(CORES):
        for x in range(start, width, CORES):
            for y in range(height):
                m = floor(
                    _mandelbrot_at(
                        _index_to_complex(
                            x, y, width, height, re_start, re_end, im_start, im_end
                        ),
                        precision,
                        infinity,
                    )
                )
                out[x, y][:] = 0 if m == precision else 255


@nb.njit(parallel=True)
def _mandelbrot_set(
    out: np.ndarray,
    precision: int,
    infinity: float,
    re_start: float,
    re_end: float,
    im_start: float,
    im_end: float,
):
    width = out.shape[0]
    height = out.shape[1]
    for start in nb.prange(CORES):
        for x in range(start, width, CORES):
            for y in range(height):
                # calculate C then do the iterations
                m = _mandelbrot_at(
                    _index_to_complex(
                        x, y, width, height, re_start, re_end, im_start, im_end
                    ),
                    precision,
                    infinity,
                )
                if m < precision:
                    out[x, y] = (
                        int(m + ((m * 20) % 156)),
                        int(100 + ((m * 20) % 156)),
                        int(255),
                    )
                else:
                    out[x, y][:] = 0


def mandelbrot_set(
    width: int,
    height: int,
    precision: int,
    infinity: float,
    inArr: np.ndarray = None,
    pg: bool = False,
) -> np.ndarray:
    if inArr is None:
        output = np.ndarray((width, height, 3))
    else:
        assert len(inArr.shape) == 3, "the input array must be a 3D array"
        assert inArr.shape[2] == 3, "the third dimension should be of length 3"
        output = inArr

    if RAINBOW:
        _mandelbrot_set_green(
            output, precision, infinity, RE_START, RE_END, IM_START, IM_END
        )
    elif BW:
        _mandelbrot_set_BW(
            output, precision, infinity, RE_START, RE_END, IM_START, IM_END
        )
    else:
        _mandelbrot_set(output, precision, infinity, RE_START, RE_END, IM_START, IM_END)

    return output if pg else output.transpose((1, 0, 2))


def zoom(x: int, y: int, scroll: int):
    # zooming algorithm taken from https://github.com/davidpendergast/Fractal-Generator/blob/b0b772c9b641f67c65bf182adaed52e7791ca994/fractal.py#L63
    global RE_START, RE_END, IM_START, IM_END
    x = (x / WIDTH) * (RE_END - RE_START) + RE_START
    y = (y / HEIGHT) * (IM_END - IM_START) + IM_START

    if scroll < 0:
        new_width = (RE_END - RE_START) * 1.5 * abs(scroll)
        new_height = (IM_END - IM_START) * 1.5 * abs(scroll)
    else:
        new_width = (RE_END - RE_START) / 1.5 * abs(scroll)
        new_height = (IM_END - IM_START) / 1.5 * abs(scroll)
    RE_START = x - new_width / 2
    RE_END = x + new_width / 2
    IM_START = y - new_height / 2
    IM_END = y + new_height / 2


def run_pygame():
    import pygame

    WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("mandelbrot set with numba")
    FPS = 60
    clock = pygame.time.Clock()
    running = True
    array = np.ndarray((WIDTH, HEIGHT, 3))  # so we dont have to create it every time
    update = True

    while running:
        clock.tick(FPS)
        if update:
            array.fill(0)
            pygame.surfarray.blit_array(
                WIN,
                mandelbrot_set(
                    WIDTH, HEIGHT, PRECISION, INFINITY, inArr=array, pg=True
                ),
            )
            update = False
            pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                pygame.quit()
                sys.exit(-1)
            elif event.type == pygame.MOUSEWHEEL:
                zoom(*pygame.mouse.get_pos(), event.y)
                update = True


if __name__ == "__main__":
    SAVE = check_args("--save")
    RUN = check_args("--run")
    RAINBOW = check_args("--rainbow")
    BW = check_args("--BW")

    parser = ArgumentParser(description="a mandelbrot-set generator")
    parser.add_argument(
        "-p",
        type=int,
        metavar="int",
        default=PRECISION,
        help=f"the precision of the set (default {PRECISION})",
    )
    parser.add_argument(
        "-i",
        type=int,
        metavar="int",
        default=INFINITY,
        help=f"the finite infinity of the set (default {INFINITY})",
    )
    parser.add_argument(
        "-s",
        type=int,
        metavar="int",
        default=WIDTH,
        help=f"the size of the set (default {WIDTH})",
    )

    args = parser.parse_args()

    PRECISION = args.p
    INFINITY = args.i
    WIDTH = int(args.s)
    HEIGHT = int(args.s / 1.5)

    mandelbrot_set(1, 1, PRECISION, INFINITY)  # compile function

    if RUN:
        sys.exit(run_pygame())

    print(f"creating the mandelbrot-set of size {WIDTH}x{HEIGHT}...")
    start_time = time.perf_counter()
    output = mandelbrot_set(WIDTH, HEIGHT, PRECISION, INFINITY)
    print(
        f"for a mandelbrot-set of size {WIDTH}x{HEIGHT} it took {time.perf_counter() - start_time}s"
    )

    image = Image.fromarray(np.uint8(output), "RGB")
    if SAVE:
        image.save(
            f"mandelbrot-set ({WIDTH=}, {HEIGHT=}, {PRECISION=}, {INFINITY=}).png",
            "PNG",
        )
    image = Image.fromarray(np.uint8(output), "RGB")
    image.show()
    sys.exit(0)
