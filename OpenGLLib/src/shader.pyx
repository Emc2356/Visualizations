#cython: language_level=3

cimport glew as GL


cdef int[1] nullptr = [0]


class ShaderError(Exception):
    def __init__(self, msg):
        super().__init__(self, msg)


cdef const char* shader_int_to_cstr(GL.GLenum shader_type):
    if shader_type == GL.GL_FRAGMENT_SHADER:
        return "fragment"
    if shader_type == GL.GL_VERTEX_SHADER:
        return "vertex"
    if shader_type == GL.GL_COMPUTE_SHADER:
        return "compute"
    if shader_type == GL.GL_GEOMETRY_SHADER:
        return "geometry"
    else:
        raise ValueError(f"unrecognized shader type `{shader_type}`")


cdef GL.GLuint compile_single_shader(
    GL.GLenum shader_type,
    const char* shader_source,
    GL.GLuint* out=NULL,
):
    cdef GL.GLsizei log_length = 0
    cdef GL.GLchar message[1024]
    cdef GL.GLchar message_err[1224]

    cdef GL.GLuint shader_id = GL.glCreateShader(shader_type)
    GL.glShaderSource(shader_id, 1, &shader_source, NULL)
    GL.glCompileShader(shader_id)

    cdef GL.GLint compiled;
    GL.glGetShaderiv(shader_id, GL.GL_COMPILE_STATUS, &compiled)

    if compiled != GL.GL_TRUE:
        if out != NULL:
            out[0] = 0

        GL.glGetShaderInfoLog(shader_id, log_length, &log_length, message)
        GL.glDeleteShader(shader_id)

        raise ShaderError(
            f"failed while compiling {shader_int_to_cstr(shader_type).decode()} "
            f"shader\n==========\n"
            f"{message.decode()}"
        )

    if out != NULL:
        out[0] = shader_id

    return shader_id


cdef GL.GLuint create_program(
        const char* fragment_shader_source,
        const char* vertex_shader_source,
        const char* geometry_shader_source=NULL,
):
    cdef GL.GLsizei log_length = 0
    cdef GL.GLchar message[1024]

    cdef GL.GLuint program_id = GL.glCreateProgram()

    cdef GL.GLuint fs = compile_single_shader(GL.GL_FRAGMENT_SHADER, fragment_shader_source);
    if fs == 0:
        return 0
    cdef GL.GLuint vs = compile_single_shader(GL.GL_VERTEX_SHADER, vertex_shader_source);
    if vs == 0:
        return 0
    cdef GL.GLuint gs;

    if geometry_shader_source != NULL:
        gs = compile_single_shader(GL.GL_GEOMETRY_SHADER, geometry_shader_source)
        if gs == 0:
            return 0
    GL.glAttachShader(program_id, fs)
    GL.glAttachShader(program_id, vs)
    if geometry_shader_source != NULL:
        GL.glAttachShader(program_id, gs)

    GL.glLinkProgram(program_id)

    cdef GL.GLint linked;
    GL.glGetProgramiv(program_id, GL.GL_LINK_STATUS, &linked)

    if linked == GL.GL_FALSE:
        GL.glGetProgramInfoLog(program_id, 1024, &log_length, message)

        GL.glDeleteShader(fs)
        GL.glDeleteShader(vs)
        if geometry_shader_source != NULL:
            GL.glDeleteShader(gs)
        GL.glDeleteProgram(program_id)

        raise ShaderError(
            f"failed while linking the program\n"
            f"==========\n"
            f"{message.decode()}"
        )

    GL.glValidateProgram(program_id)

    cdef GL.GLint valid;
    GL.glGetProgramiv(program_id, GL.GL_LINK_STATUS, &valid)

    if valid == GL.GL_FALSE:
        GL.glGetProgramInfoLog(program_id, 1024, &log_length, message)

        GL.glDeleteShader(fs)
        GL.glDeleteShader(vs)
        if geometry_shader_source != NULL:
            GL.glDeleteShader(gs)
        GL.glDeleteProgram(program_id)

        raise ShaderError(
            f"fprogram can not run\n"
            f"==========\n"
            f"{message.decode()}"
        )

    GL.glDeleteShader(fs)
    GL.glDeleteShader(vs)
    if geometry_shader_source != NULL:
        GL.glDeleteShader(gs)

    return program_id


cdef class Shader:
    def __init__(
        self,
        fragment_source,
        vertex_source,
        geometry_source="",
    ):
        fragment_source_bytes = bytes(fragment_source, "ascii")
        vertex_source_bytes = bytes(vertex_source, "ascii")
        geometry_source_bytes = bytes(geometry_source, "ascii")

        cdef char* C_fragment_source = <bytes> fragment_source_bytes
        cdef char* C_vertex_source = <bytes> vertex_source_bytes
        cdef char* C_geometry_source = <bytes> geometry_source_bytes

        if len(geometry_source) == 0:
            C_geometry_source = NULL

        # for internal access
        self.Renderer_ID: GL.GLuint = create_program(
            C_fragment_source,
            C_vertex_source,
            C_geometry_source,
        )
        # for python access
        self.glo = <int> self.Renderer_ID

    def bind(self):
        GL.glUseProgram(self.Renderer_ID)

    def unbind(self):
        GL.glUseProgram(0)

    def __hash__(self):
        return id(self)

    def __del__(self):
        GL.glDeleteProgram(self.Renderer_ID)

    def __str__(self):
        return repr(f"<Program: {self.Renderer_ID}>")


def init():
    cdef GL.GLenum err = GL.glewInit()
    if err != GL.GLEW_OK:
        raise RuntimeError(f"failed to initialize glew: {GL.glewGetErrorString(err).decode('utf-8')}")
