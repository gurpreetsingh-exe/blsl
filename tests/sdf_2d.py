_ = [
    {
        'title': "circle sdf",
        'src': """float test(vec2 p, float r) {
            return length(p) - r;
        }""",
        'input': {
            'p': [4.0, 3.0, 0.0],
            'r': 2.5
        },
        'output': {
            'ret': 2.5
        }
    },
    {
        'skip': True,
        'title': "box sdf",
        'src': """float sdBox(in vec2 p, in vec2 b) {
            vec2 d = abs(p) - b;
            return length(max(d, 0.0)) + min(max(d.x, d.y), 0.0);
        }""",
        'output': {
            'ret': 0.0
        }
    },
]
