#version 330
#ifdef GL_ES
precision mediump float;
#endif

uniform vec2 resolution;  // Canvas size (width, height)

int width = int(resolution.x);
int height = int(resolution.y);

uniform int   detail   = 500;
uniform float infinity = 2.0;
uniform float RE_START = -2;
uniform float RE_END   = 1;
uniform float IM_START = -1;
uniform float IM_END   = 1;


void main(){
    vec2 st = gl_FragCoord.xy / resolution;

    float x0 = RE_START + (gl_FragCoord.x / width ) * (RE_END - RE_START);
    float y0 = IM_START + (gl_FragCoord.y / height) * (IM_END - IM_START);

    float x, y, x2, y2, w;
    int m;

    for (m = 0; m < detail && x * x + y * y < infinity * infinity; m++) {
        x = x2 - y2 + x0;
        y = w - x2 - y2 + y0;
        x2 = x * x;
        y2 = y * y;
        w = (x + y) * (x + y);
    }

    vec3 color = vec3(
        float(m + ((m * 20) % 156)) / 255.0,
        float(100 + ((m * 20) % 156)) / 255.0,
        1.0
    ) * (1 - step(detail, m));
    // instead of branching with if/else we will use the step function

    gl_FragColor = vec4(color, 1.0);
}
