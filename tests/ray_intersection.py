_ = [
    {
        'title': "ray sphere intersection",
        'src': """float ray_sphere_intersection(vec3 ro, vec3 rd, vec3 loc, float radius) {
            vec3 v = ro - loc;
            float a = dot(v, rd);
            float b = dot(v, v) - radius * radius;
            return -a - sqrt(a * a - b);
        }""",
        'input': {
            'ro': [5.0, 7.0, 0.0],
            'rd': [1.0, 1.0, 1.0],
            'loc': [0.2, 0.3, 0.0],
            'radius': 0.5,
        },
        'output': {
            'ret': -19.535545349121094,
        },
    },
]
