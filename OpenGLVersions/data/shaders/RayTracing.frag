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
#define HittableObjectCount 1  // %HittableObjectCount%
#define infinity (1.0 / 0.0)
#define GrowthRate 3.57  // used for the logistic map speudo random numbers

// the structs
struct Ray {
    vec3 origin;
    vec3 dir;
};

struct HitRecord {
    vec3 p;
    vec3 normal;
    float t;
    bool front_face;
};

// the vec4 is composed of x, y, z, radius
struct Sphere {
    vec4 pos;
};

layout(std430, binding=0) buffer spheres {
    Sphere spheres[];
} In;

//layout(std430, binding=1) buffer numbers {
//    float numbers[];
//} In;

// declare all of the uniforms
uniform vec2 resolution = vec2(0.0);
uniform float aspect_ratio = 16 / 9;
uniform int width = 0;
uniform int height = 0;
uniform float time = 0;
uniform float viewport_height = 0;
uniform float viewport_width = 0;
uniform float focal_length = 0;
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

float rand(vec2 co) {
    float a = 12.9898;
    float b = 78.233;
    float c = 43758.5453;
    float dt = dot(co.xy ,vec2(a,b));
    float sn = mod(dt, PI);
    return fract(sin(sn) * c);
}

// "methods" of the structs, the names start with the name of
// the struct and the first argument is the object that the function will work in
void HitRecord_set_face_normal(inout HitRecord rec, Ray r, vec3 outward_normal) {
    rec.front_face = dot(r.dir, outward_normal) < 0;
    rec.normal = rec.front_face ? outward_normal :-outward_normal;
}

vec3 Ray_at(Ray r, float t) { return r.origin + t*r.dir; }

bool Sphere_hit(Sphere sphere, Ray r, float t_min, float t_max, inout HitRecord rec) {
    vec3 oc = r.origin - sphere.pos.xyz;
    float a = length_squared(r.dir);
    float half_b = dot(oc, r.dir);
    float c = length_squared(oc) - sphere.pos.w * sphere.pos.w;

    float discriminant = half_b*half_b - a*c;
    if (discriminant < 0) return false;
    float sqrtd = sqrt(discriminant);

    // Find the nearest root that lies in the acceptable range.
    float root = (-half_b - sqrtd) / a;
    if (root < t_min || t_max < root) {
        root = (-half_b + sqrtd) / a;
        if (root < t_min || t_max < root)
            return false;
    }

    rec.t = root;
    rec.p = Ray_at(r, rec.t);
    vec3 outward_normal = (rec.p - sphere.pos.xyz) / sphere.pos.w;
    HitRecord_set_face_normal(rec, r, outward_normal);

    return true;
}

bool hit_with_spheres(Ray r, float t_min, float t_max, out HitRecord rec) {
    HitRecord temp_rec;
    bool hit_anything = false;
    float closest_so_far = t_max;

    for (int i = 0; i < HittableObjectCount; i++) {
        Sphere sphere = In.spheres[i];
        if (Sphere_hit(sphere, r, t_min, closest_so_far, temp_rec)) {
            hit_anything = true;
            rec = temp_rec;
        }
    }

    return hit_anything;
}

vec3 ray_color(Ray r) {
    HitRecord rec;
    if (hit_with_spheres(r, 0, infinity, rec)) {
        return 0.5 * (rec.normal + vec3(1, 1, 1));
    }
    vec3 unit_direction = normalize(r.dir);
    float t = 0.5 * (unit_direction.y + 1.0);
    return (1.0-t)*vec3(1.0, 1.0, 1.0) + t*vec3(0.5, 0.7, 1.0);
}

Ray get_ray(float u, float v) {
    return Ray(origin, lower_left_corner + u*horizontal + v*vertical - origin);
}

void get_ray_ip(out Ray r, float u, float v) {
    r.origin = origin;
    r.dir = lower_left_corner + u*horizontal + v*vertical - origin;
}

void main() {
    vec2 xyNormalized = gl_FragCoord.xy / resolution;
    float u = xyNormalized.x;
    float v = xyNormalized.y;
    float i = gl_FragCoord.x;
    float j = gl_FragCoord.y;

    Ray r;
    vec3 color;

    for (int s = 0; s < samples; s++) {
        u = (i + rand(xyNormalized.xy + s)) / (width-1);
        v = (j + rand(xyNormalized.xy + s)) / (height-1);
        get_ray_ip(r, u, v);
        color += ray_color(r);
    }
    // rand

    outColor = vec4(color / samples, 1.0);
}
