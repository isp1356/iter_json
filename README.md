# iter_json

Stream JSON from uncomplete python object.


## Install

```bash
mkdir -p ~/.virtualenvs
python3 -m venv  ~/.virtualenvs/iter_json
pip install -U pip
pip install -e '.[dev]'
```


## Usage Example

```python
import asyncio
import json

from iter_json import aiter_json


async def some_data_producer():
    for i in range(100_000):
        await asyncio.sleep(0)
        yield i


async def json_streamer():
    partial_result = {
        "start": "hello!",
        "data": some_data_producer(),
        "end": "bye!",
    }
    async for s in aiter_json(partial_result):
        yield s


async def binary_dumps():
    data = bytearray()
    async for i in json_streamer():
        data += i.encode()
    return data


async def json_receiver():
    data = await binary_dumps()
    assert json.loads(data.decode()) == {
        "start": "hello!",
        "data": list(range(100_000)),
        "end": "bye!",
    }


asyncio.run(json_receiver())
```
