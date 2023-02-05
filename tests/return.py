_ = [
    {
        'title': "return int variable",
        'src': """int test() {
            int a = 10;
            return a;
        }""",
        'output': {
            'ret': 10
        }
    },
    {
        'title': "return float addition",
        'src': """float test() {
            return 20.0 + 10;
        }""",
        'output': {
            'ret': 30.0
        }
    },
    {
        'title': "return int variable addition",
        'src': """int test() {
            int a = 10;
            int b = 11;
            return a + b;
        }""",
        'output': {
            'ret': 21
        }
    },
    {
        'title': "return binary expr",
        'src': """float test() {
            return 10 + 20 + 30 + 40;
        }""",
        'output': {
            'ret': 100
        }
    },
    {
        'title': "return vec3",
        'src': """vec3 test() {
            return vec3(1.0);
        }""",
        'output': {
            'ret': [1.0, 1.0, 1.0]
        }
    },
    {
        'title': "return vec2",
        'src': """vec2 test() {
            return vec2(1.0, 1.0);
        }""",
        'output': {
            'ret': [1.0, 1.0, 0.0]
        }
    },
]
