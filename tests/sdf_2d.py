# https://iquilezles.org/articles/distfunctions2d/
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
        'title': "box sdf",
        'src': """float test(vec2 p, vec2 b) {
            vec2 d = abs(p) - b;
            return length(max(d, 0.0)) + min(max(d.x, d.y), 0.0);
        }""",
        'input': {
            'p': [0.1, 0.2, 0.0],
            'b': [0.123, 0.456, 0.0],
        },
        'output': {
            'ret': -0.023000001907348633
        }
    },
    {
        'title': "segment sdf",
        'src': """float test(vec2 p, vec2 a, vec2 b) {
            vec2 pa = p - a, ba = b - a;
            float h = clamp(dot(pa, ba) / dot(ba, ba), 0.0, 1.0);
            return length(pa - ba * h);
        }""",
        'input': {
            'p': [0.1, 0.2, 0.0],
            'a': [0.0, 0.0, 0.0],
            'b': [0.123, 0.456, 0.0],
        },
        'output': {
            'ret': 0.04446348920464516
        }
    },
]
