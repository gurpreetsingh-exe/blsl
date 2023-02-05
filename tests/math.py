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
        'title': "equality",
        'src': """int test() {
            int a = 10 == 20;
            int b = 20.5 != 20.5;
            return a != b;
        }""",
        'output': {
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
            'ret': 63.33333206176758
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
]
