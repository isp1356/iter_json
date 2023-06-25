import pytest

from .. import iter_join


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
