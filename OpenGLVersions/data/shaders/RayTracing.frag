#version 430
#ifdef GL_ES
precision mediump float;
#endif

// #all of the macros
#define lerp mix
#define QUARTER_PI 0.78539816339
#define HALF_PI    1.57079632679
#define PI         3.14159265359
#define TWO_PI     6.28318530718
#define infinity (1.0 / 0.0)

// the structs
struct Ray {
    vec3 origin;
    vec3 dir;
};

struct Sphere {
    vec4 pos;  // x, y, z, radius
    vec4 color;  // r, g, b, a (1.0f)
    vec4 data;  // reflectivity, emission, 0.0f, 0.0f
};

layout(std430, binding=0) buffer spheres {
    Sphere spheres[];
} In;

// declare all of the uniforms
uniform int SphereCount = 3;
uniform vec2 resolution = vec2(0.0);
uniform float aspect_ratio = 16 / 9;
uniform int width = 0;
uniform int height = 0;
uniform float time = 0;
uniform vec3 origin = vec3(0.0);
uniform vec3 horizontal = vec3(0.0);
uniform vec3 vertical = vec3(0.0);
uniform vec3 lower_left_corner = vec3(0.0);
uniform int samples = 32;

// looks better than gl_FragColor
out vec4 outColor;

// functions that arent provided by GLSL
float length_squared(vec4 v) { return v.x * v.x + v.y * v.y + v.z * v.z + v.w * v.w; }
float length_squared(vec3 v) { return v.x * v.x + v.y * v.y + v.z * v.z; }
float length_squared(vec2 v) { return v.x * v.x + v.y * v.y; }

vec3 Ray_at(Ray r, float t) { return r.origin + t*r.dir; }

bool hit_sphere(vec3 center, float radius, inout Ray r) {
    vec3 oc = r.origin - center;
    float a = length_squared(r.dir);
    float half_b = dot(oc, r.dir);
    float c = length_squared(oc) - radius*radius;
    float discriminant = half_b*half_b - a*c;
    return (discriminant > 0);
}

vec3 ray_color(inout Ray r) {
    for (int i = 0; i < 3; i++) {
        if (hit_sphere(In.spheres[i].pos.xyz, In.spheres[i].pos.w, r)) {
            return In.spheres[i].color.rgb;
        }
    }
    vec3 unit_direction = normalize(r.dir);
    float t = 0.5*(unit_direction.y + 1.0);
    return lerp(vec3(1.0, 1.0, 1.0), vec3(0.5, 0.7, 1.0), t);
}

void get_ray_ip(out Ray r, float u, float v) {
    r.origin = origin;
    r.dir = lower_left_corner + u*horizontal + v*vertical - origin;
}

Ray get_ray(float u, float v) {
    Ray ray;
    get_ray_ip(ray, u, v);
    return ray;
}

void main() {
    vec2 xyNormalized = gl_FragCoord.xy / resolution;
    float i = gl_FragCoord.x;
    float j = gl_FragCoord.y;
    float u; // x
    float v; // y

    Ray r;
    vec3 color;

    u = gl_FragCoord.x / (width - 1);
    v = gl_FragCoord.y / (height - 1);
    get_ray_ip(r, u, v);
    color = ray_color(r);

    outColor = vec4(color, 1.0);
}
