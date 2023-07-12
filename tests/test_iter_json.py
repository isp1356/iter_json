import json

import pytest

from iter_json import iter_json


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


def dumps(obj):
    serialized = ""
    for i in iter_json(obj):
        serialized += i
    return serialized


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
