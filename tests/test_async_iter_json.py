import json

import pytest

from .. import adumps

pytest_plugins = "pytest_asyncio"


@pytest.mark.asyncio
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
async def test_dumps_normal_object(input_):
    assert await adumps(input_) == json.dumps(input_)


async def producer(it):
    for i in it:
        yield i


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "input_,expected",
    [
        (producer([]), []),
        (producer([1]), [1]),
        (producer([1, 2]), [1, 2]),
        (producer([1, 2, 3]), [1, 2, 3]),
        (
            {
                "a": 1,
                "b": {
                    "c": producer([]),
                    "d": producer([1]),
                    2: iter([4, 5]),
                },
            },
            {"a": 1, "b": {"c": [], "d": [1], 2: [4, 5]}},
        ),
        (
            {
                "a": 1,
                "b": producer([1, 2, 3]),
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
                        {3: producer([4, producer([5, iter([6, 7])])])},
                    ]
                ),
                "c": 5,
            },
            {
                "a": 1,
                "b": [1, 2, {3: [4, [5, [6, 7]]]}],
                "c": 5,
            },
        ),
    ],
)
async def test_dumps_object_with_range(input_, expected):
    assert await adumps(input_) == json.dumps(expected)
