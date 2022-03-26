from typing import List

import subprocess
from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy as np

from pathlib import Path
import platform
import shutil
import sys
import os

includes: List[str] = [".", np.get_include()]
glew_header: str = ""

libraries: List[str] = []
library_dirs = []

language = "c"  # "c++"

define_macros = []
undef_macros = []

if platform.system() == "Windows":
    glew_header = "win_glew/include/GL/glew.h"
    includes.append("win_glew/include")
    includes.append("src/")

    libraries.extend(["opengl32", "glew32s", "User32", "Gdi32", "Shell32"])
    library_dirs.append("win_glew/lib/")

    define_macros.append(("GLEW_STATIC", None))
else:
    raise NotImplementedError("not done for the rest of the platforms cause i dont know how (-_-).")

extensions = [
    Extension(
        name="shader",
        sources=["src/shader.pyx"],
        language=language,
        include_dirs=includes,
        libraries=libraries,
        library_dirs=library_dirs,
        define_macros=define_macros,
        undef_macros=undef_macros,
    ),
    Extension(
        name="vertexbuffer",
        sources=["src/vertexbuffer.pyx"],
        language=language,
        include_dirs=includes,
        libraries=libraries,
        library_dirs=library_dirs,
        define_macros=define_macros,
        undef_macros=undef_macros,
    ),
]


def consume_arg(arg: str) -> bool:
    if arg in sys.argv:
        sys.argv.remove(arg)
        return True
    return False


def build():
    global extensions

    Path("build").mkdir(exist_ok=True, parents=True)

    if consume_arg("-h"):
        print("Build CyOpenGL library subcommands:")
        print("    -a, it gives the annotations of the cython file and then builds the library")
        print("    -CyGlew, generate glew.pxd and then builds the library")
        sys.exit(0)

    if consume_arg("-a"):
        for file in Path("src").iterdir():
            if file.suffix == ".pyx":
                print(f"cython {file} -a -o {file.with_suffix('.html')}")
                subprocess.call(f"cython {file} -a -o {file.with_suffix('.html')}")

    if consume_arg("-CyGlew"):
        print(f"Generating glew.pxd based on {glew_header}")

        dir_glew_destination = Path("src")

        from glew_pxd import generate_pxd

        print(f"Writing glew.pxd to {dir_glew_destination}")
        generate_pxd(glew_header, dir_glew_destination)

    if len(sys.argv) == 1:
        sys.argv.append("build_ext")
        sys.argv.append("--inplace")

    setup(ext_modules=cythonize(extensions))

    shutil.rmtree("build")

    # for file in Path("src").iterdir():
    #     if file.suffix == ".pyx":
    #         if file.with_suffix(".c").exists():
    #             print(f"removing {file.with_suffix('.c')}...")
    #             os.remove(file.with_suffix(".c"))
    #         elif file.with_suffix(".cpp").exists():
    #             print(f"removing {file.with_suffix('.cpp')}...")
    #             os.remove(file.with_suffix(".cpp"))


if __name__ == "__main__":
    build()
