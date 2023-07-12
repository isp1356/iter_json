import json

from .lib import COLON, SEP, Kind, iter_join
from .util import aiter_join as _aiter_join
from .util import is_aiter, is_iter


async def aiter_join(iterable, sep=SEP):
    async for i in _aiter_join(iterable=iterable, sep=SEP):
        yield i


async def aiter_obj(obj, comma=SEP, colon=COLON, is_key=False):
    if obj is None or isinstance(obj, (int, str)):
        yield Kind.obj, obj, is_key

    elif isinstance(obj, dict):
        yield Kind.sep, "{", False
        for kind, e in iter_join(obj.items(), sep=comma):
            if kind == Kind.sep:
                yield kind, e, False
            elif kind == Kind.obj:
                key, val = e
                async for keys in aiter_obj(key, comma=comma, colon=colon, is_key=True):
                    yield keys
                yield Kind.sep, colon, False
                async for values in aiter_obj(val, comma=comma, colon=colon):
                    yield values
            else:
                raise RuntimeError(f"Unknown kind of object: {kind}")
        yield Kind.sep, "}", False

    elif is_iter(obj):
        yield Kind.sep, "[", False
        for kind, e in iter_join(obj, sep=comma):
            if kind == Kind.sep:
                yield kind, e, False
            elif kind == Kind.obj:
                async for els in aiter_obj(e, comma=comma, colon=colon):
                    yield els
            else:
                raise RuntimeError(f"Unknown kind of object: {kind}")
        yield Kind.sep, "]", False

    elif is_aiter(obj):
        yield Kind.sep, "[", False
        async for kind, e in aiter_join(obj, sep=comma):
            if kind == Kind.sep:
                yield kind, e, False
            elif kind == Kind.obj:
                async for els in aiter_obj(e, comma=comma, colon=colon):
                    yield els
            else:
                raise RuntimeError(f"Unknown kind of object: {kind}")
        yield Kind.sep, "]", False
    else:
        raise RuntimeError(f"Unknown type of object {type(obj)}")


async def aiter_json(obj):
    """Iterate over partially known python object and stream it in JSON
    format.
    """
    async for kind, e, is_key in aiter_obj(obj):
        if kind == Kind.sep:
            yield e
        elif kind == Kind.obj:
            if is_key and not isinstance(e, str):
                yield f'"{json.dumps(e)}"'
            else:
                yield json.dumps(e)
        else:
            RuntimeError("Unknown kind of object", kind)
