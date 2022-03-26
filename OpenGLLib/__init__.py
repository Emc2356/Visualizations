import OpenGLLib.shader
import OpenGLLib.vertexbuffer

VertexBuffer = OpenGLLib.vertexbuffer.VertexBuffer
Shader = OpenGLLib.shader.Shader


def init():
    OpenGLLib.shader.init()
    OpenGLLib.vertexbuffer.init()
