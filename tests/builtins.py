_ = [
    {
        'title': "max",
        'src': """void test(inout float a, inout vec2 b, inout vec3 c) {
            a = 10.0;
            b = max(vec2(a), vec2(100.0));
            c = max(vec3(a), 100.0);
        }""",
        'input': {
            'a': 20.0,
            'b': [50.0, 50.0, 0.0],
            'c': [0.0, 0.0, 0.0]
        },
        'output': {
            'a': 10.0,
            'b': [100.0, 100.0, 0.0],
            'c': [100.0, 100.0, 100.0],
        }
    },
    {
        'title': "min",
        'src': """void test(inout float a, inout vec2 b, inout vec3 c) {
            a = min(10.0, 25.0);
            b = min(vec2(a), vec2(100.0));
            a = 20.0;
            c = min(vec3(a), 100.0);
        }""",
        'input': {
            'a': 0.0,
            'b': [50.0, 50.0, 0.0],
            'c': [0.0, 0.0, 0.0]
        },
        'output': {
            'a': 20.0,
            'b': [10.0, 10.0, 0.0],
            'c': [20.0, 20.0, 20.0],
        }
    },
    {
        'title': "length",
        'src': """float test() {
            float a = 10.0;
            vec2 b = max(vec2(a), vec2(100.0));
            return length(b);
        }""",
        'output': {
            'ret': 141.42135620117188,
        }
    },
    {
        'title': "abs",
        'src': """float test() {
            return abs(10.0 - 20.0);
        }""",
        'output': {
            'ret': 10.0,
        }
    },
    {
        'title': "dot",
        'src': """void test(out float a, out float b) {
            a = dot(vec2(1.0), vec2(2.0));
            b = dot(vec3(1.0), vec3(1.0, 2.0, 3.0));
        }""",
        'output': {
            'a': 4.0,
            'b': 6.0,
        }
    },
    {
        'title': "cross",
        'src': """vec3 test() {
            return cross(vec3(1.0, 0.0, 0.0), vec3(0.0, 1.0, 0.0));
        }""",
        'output': {
            'ret': [0.0, 0.0, 1.0],
        }
    },
    {
        'title': "clamp",
        'src': """float test() {
            return clamp(50.0, 0.0, 10.0);
        }""",
        'output': {
            'ret': 10.0,
        }
    },
    {
        'title': "sqrt",
        'src': """float test() {
            return sqrt(25.0);
        }""",
        'output': {
            'ret': 5.0,
        }
    },
]
