from enum import Enum


def is_iter(obj):
    try:
        iter(obj)
    except TypeError:
        return False
    else:
        return True


def is_aiter(obj):
    try:
        getattr(obj, "__aiter__")  # aiter() not available in python3.7
    except AttributeError:
        return False
    else:
        return True


class Kind(Enum):
    sep = 0
    obj = 1


def iter_join(iterable, sep):
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


async def aiter_join(iterable, sep):
    x, y = None, None
    has_data = False
    i = 0
    async for e in iterable:
        has_data = True
        if i == 0:
            y = e
        if i > 0:
            x, y = y, e
            yield Kind.obj, x
            yield Kind.sep, sep
        i += 1
    if not has_data:
        return
    yield Kind.obj, y
