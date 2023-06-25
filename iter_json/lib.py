import json
from enum import Enum

from .util import is_iter


class Kind(Enum):
    sep = 0
    obj = 1


def iter_join(iterable, sep=", "):
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
    """Iterate over partially known python object and stream it in JSON
    format.
    """
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
