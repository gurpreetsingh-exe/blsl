_ = [
    {
        'title': "inout integer",
        'src': """void test(inout int a) {
            a = 10;
        }""",
        'output': {
            'a': 10
        }
    },
    {
        'title': "inout vec2",
        'src': """void test(inout vec2 a) {
            a = vec2(10.0, 20.0);
            a = vec2(15.0, 20.0);
        }""",
        'output': {
            'a': [15.0, 20.0, 0.0]
        }
    },
    {
        'title': "multiple inouts",
        'src': """void test(inout float a, inout int b, inout vec2 c, inout vec3 d) {
            a = 10.0;
            b = 20;
            c = vec2(a);
            d = vec3(25.0, 54.0, 34.0);
        }""",
        'output': {
            'a': 10.0,
            'b': 20,
            'c': [10.0, 10.0, 0.0],
            'd': [25.0, 54.0, 34.0]
        }
    },
]
