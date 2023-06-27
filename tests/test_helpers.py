import pytest

from iter_json import aiter_join, iter_join
from iter_json.lib import SEP

pytest_plugins = "pytest_asyncio"


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
    for _, e in iter_join(input_, sep=SEP):
        s += str(e)
    assert s == SEP.join([str(e) for e in input_])


@pytest.mark.asyncio
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
async def test_aiter_join(input_):
    def make_producer(li):
        async def produce():
            for e in li:
                yield e

        return produce()

    producer = make_producer(input_)
    s = ""
    async for _, e in aiter_join(producer):
        s += str(e)
    assert s == SEP.join([str(e) for e in input_])
