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
