#cython: language_level=3

cimport glew as GL


cdef class VertexBuffer:
    # for internal use
    cdef GL.GLuint Renderer_ID
    # the size of the buffer for checks (internal use)
    cdef unsigned int size
    # for the python side
    cdef readonly int glo
