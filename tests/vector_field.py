_ = [
    {
        'title': "vec2 field access",
        'src': """float test() {
            vec2 a = vec2(2.0, 1.0);
            return a.x;
        }""",
        'output': {
            'ret': 2.0
        }
    },
    {
        'title': "vec3 field access",
        'src': """float test() {
            vec2 a = vec2(2.0, 1.0);
            vec3 b = vec3(a.y, a.x, 1.0);
            return b.x + b.z;
        }""",
        'output': {
            'ret': 2.0
        }
    },
]
