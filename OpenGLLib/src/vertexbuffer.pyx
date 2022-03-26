#cython: language_level=3

cimport glew as GL

cimport numpy as np
import numpy as np

np.import_array()


cdef class VertexBuffer:
    def __init__(self, array):
        GL.glGenBuffers(1, &self.Renderer_ID)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.Renderer_ID)

        if not isinstance(array, np.ndarray):
            raise TypeError(f"VertexBuffer constructor expected a numpy array but got `{type(array)}`")

        GL.glBufferData(GL.GL_ARRAY_BUFFER, array.nbytes, <void*> array.data, GL.GL_STATIC_DRAW)

        self.size = <unsigned int> array.nbytes
        self.glo = self.Renderer_ID

    def __str__(self):
        return repr(f"<VertexBuffer: {self.Renderer_ID}>")

    def bind(self):
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.Renderer_ID)

    def unbind(self):
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)

    def __del__(self):
        GL.glDeleteBuffers(1, &self.Renderer_ID)


def init():
    cdef GL.GLenum err = GL.glewInit()
    if err != GL.GLEW_OK:
        raise RuntimeError(f"failed to initialize glew: {GL.glewGetErrorString(err).decode('utf-8')}")
