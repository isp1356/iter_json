def is_iter(obj):
    try:
        iter(obj)
    except TypeError:
        return False
    else:
        return True
