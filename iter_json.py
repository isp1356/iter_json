import json
from enum import Enum

import pytest


class Kind(Enum):
    sep = 0
    obj = 1


def iter_join(iterable, sep=", "):
    prev = None
    x, y = None, None
    has_data = False
    for i, e in enumerate(iterable):
        has_data = True
        if i == 0:
            y = e
        if i > 0:
            x, y = y, e
            yield Kind.obj, x
            yield Kind.sep, sep
    if not has_data:
        return
    yield Kind.obj, y


def is_iter(obj):
    try:
        iter(obj)
    except TypeError:
        return False
    else:
        return True


def iter_obj(obj, comma=", ", colon=": ", is_key=False):
    if obj is None or isinstance(obj, (int, str)):
        yield Kind.obj, obj, is_key

    elif isinstance(obj, dict):
        yield Kind.sep, "{", False
        for kind, e in iter_join(obj.items(), sep=comma):
            if kind == Kind.sep:
                yield kind, e, False
            elif kind == Kind.obj:
                key, val = e
                yield from iter_obj(key, is_key=True)
                yield Kind.sep, colon, False
                yield from iter_obj(val)
            else:
                raise RuntimeError(f"Unknown kind of object: {kind}")
        yield Kind.sep, "}", False

    elif is_iter(obj):
        yield Kind.sep, "[", False
        for kind, e in iter_join(obj, sep=comma):
            if kind == Kind.sep:
                yield kind, e, False
            elif kind == Kind.obj:
                yield from iter_obj(e, comma=comma, colon=colon)
            else:
                raise RuntimeError(f"Unknown kind of object: {kind}")
        yield Kind.sep, "]", False

    else:
        raise RuntimeError(f"Unknown type of object {type(obj)}")


def iter_json(obj):
    """Iterate over partially known python object and stream it in JSON format."""
    for kind, e, is_key in iter_obj(obj):
        if kind == Kind.sep:
            yield e
        elif kind == Kind.obj:
            if is_key and not isinstance(e, str):
                yield f'"{json.dumps(e)}"'
            else:
                yield json.dumps(e)
        else:
            RuntimeError("Unknown kind of object", kind)


def dumps(obj):
    serialized = ""
    for i in iter_json(obj):
        serialized += i
    return serialized


@pytest.mark.parametrize(
    "input_,",
    [
        # simple objects
        None,
        1,
        "a",
        "abc",
        # lists
        [],
        [1, 2, 3],
        ["a", "b", "c"],
        ["a", 2, "c"],
        [1, 2, []],
        [1, 2, [3, 4]],
        [[3, 4]],
        # dicts
        {},
        {1: 2},
        {"a": "b"},
        {"a": "b", "c": "d"},
        # combinations
        [{}],
        ["{}"],
        {None: None},
        {'\t\n"': None},
        {1: [None, 2]},
        {"a": "b", "c": ["d", "e", {"f": "g"}, 1, {2: 3}]},
        {"a": None, "c": ["d", "e", {"f": None}, 1, {2: 3}]},
    ],
)
def test_dumps_normal_object(input_):
    assert dumps(input_) == json.dumps(input_)


@pytest.mark.parametrize(
    "input_,expected",
    [
        (iter([]), []),
        (iter([1]), [1]),
        (iter([1, 2, 3]), [1, 2, 3]),
        (
            {
                "a": 1,
                "b": {
                    "c": iter([]),
                    "d": iter([1]),
                    2: iter([4, 5]),
                },
            },
            {"a": 1, "b": {"c": [], "d": [1], 2: [4, 5]}},
        ),
        (
            {
                "a": 1,
                "b": iter([1, 2, 3]),
                "c": 4,
            },
            {
                "a": 1,
                "b": [1, 2, 3],
                "c": 4,
            },
        ),
        (iter([{1: 2}, {3: 4}]), [{1: 2}, {3: 4}]),
        (
            {
                "a": 1,
                "b": iter(
                    [
                        1,
                        2,
                        {3: iter([4, 5])},
                    ]
                ),
                "c": 5,
            },
            {
                "a": 1,
                "b": [1, 2, {3: [4, 5]}],
                "c": 5,
            },
        ),
    ],
)
def test_dumps_object_with_range(input_, expected):
    assert dumps(input_) == json.dumps(expected)


@pytest.mark.parametrize(
    "input_,",
    [
        [],
        [1],
        [1, 2],
        [1, 2, 3],
        [(1, 2), 3],
    ],
)
def test_iter_join(input_):
    s = ""
    for _, e in iter_join(input_, sep=", "):
        s += str(e)
    assert s == ", ".join([str(e) for e in input_])
