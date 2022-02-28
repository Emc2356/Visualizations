#version 430 core

in vec4 in_vert;

void main() {
    gl_Position = vec4(in_vert);
}
