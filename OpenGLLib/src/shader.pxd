#cython: language_level=3

cimport glew as GL


# to use default arguments you use `type x=?`
cdef GL.GLuint compile_single_shader(GL.GLenum shader_type, const char* shader_source, GL.GLuint* out=?)
cdef GL.GLuint create_program(const char* fragment_shader_source, const char* vertex_shader_source, const char* geometry_shader_source=?)
cdef const char* shader_int_to_cstr(GL.GLenum shader_type)

cdef class Shader:
    cdef GL.GLuint Renderer_ID
    cdef readonly int glo
