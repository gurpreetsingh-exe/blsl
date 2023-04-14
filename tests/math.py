_ = [
    {
        'title': "int binary expressions",
        'src': """int test() {
            int a = 10 + 50;
            int b = 20 - 10;
            int c = 40 * 2;
            int d = 20 / 4;
            return a + b - c * d / a;
        }""",
        'output': {
            'ret': 63
        }
    },
    {
        # TODO: use compare in geo nodes
        'title': "equality",
        'src': """int test(inout int a, inout int b, inout int c) {
            a = 10 == 20;
            b = 20.5 != 20.5;
            c = 20.5 == 20.5;
            return a != b;
        }""",
        'output': {
            'a': 0,
            'b': 0,
            'c': 1,
            'ret': 0
        }
    },
    {
        'title': "vector equality",
        'src': """int test(inout int a, inout int b, inout int c) {
            a = vec2(10) == vec2(20);
            b = vec2(20.5) != vec2(20.5);
            c = vec2(20.5) == vec2(20.5);
            return a != b;
        }""",
        'output': {
            'a': 0,
            'b': 0,
            'c': 1,
            'ret': 0
        }
    },
    {
        'title': "float binary expressions",
        'src': """float test() {
            float a = 10.0 + 50.0;
            float b = 20.0 - 10.0;
            float c = 40.0 * 2.0;
            float d = 20.0 / 4.0;
            return a + b - c * d / a;
        }""",
        'output': {
            'ret': 63.333333333333336
        }
    },
    {
        'title': "vector math",
        'src': """vec2 test() {
            vec2 a = vec2(1.0, 2.0);
            vec2 b = vec2(2.0) * 2.0;
            return a * b + vec2(2.0);
        }""",
        'output': {
            'ret': [6.0, 10.0, 0.0]
        }
    },
    {
        'title': "vector and scalar ops",
        'src': """vec2 test() {
            vec2 a = vec2(1.0, 2.0);
            return a + 0.5 - vec2(0.1, 0.2);
        }""",
        'output': {
            'ret': [1.4, 2.3, 0.0]
        }
    },
    {
        'title': "vector + float literal",
        'src': """vec2 test() {
            vec2 a = vec2(1.0, 2.0);
            return a + 0.5;
        }""",
        'output': {
            'ret': [1.5, 2.5, 0.0]
        }
    },
    {
        'title': "vector + float variable",
        'src': """vec2 test() {
            vec2 a = vec2(1.0, 2.0);
            float b = 0.5;
            return a + b;
        }""",
        'output': {
            'ret': [1.5, 2.5, 0.0]
        }
    },
    {
        'title': "vector + float argument",
        'src': """vec2 test(float b) {
            vec2 a = vec2(1.0, 2.0);
            return a + b;
        }""",
        'input': {
            'b': 0.5,
        },
        'output': {
            'ret': [1.5, 2.5, 0.0]
        }
    },
    {
        'title': "builtin functions",
        'src': """float test(inout float a, inout vec2 b) {
            a = min(a, 10.0);
            b = max(vec2(a), vec2(100.0));
            return length(b);
        }""",
        'input': {
            'a': 20.0,
            'b': [50.0, 50.0, 0.0],
        },
        'output': {
            'a': 10.0,
            'b': [100.0, 100.0, 0.0],
            'ret': 141.42135620117188,
        }
    },
]
