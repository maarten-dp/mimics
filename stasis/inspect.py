from functools import wraps


class TrueSight:
    def __init__(self, obj):
        object.__setattr__(self, 'obj', obj)

    def __getattr__(self, key):
        return object.__getattribute__(self.obj, key)

    def __setattr__(self, key, value):
        setattr(self.obj, key, value)

    def get(self, key):
        return self.__getattr__(key)

    def __repr__(self):
        val = object.__repr__(self.obj)
        return f"TrueSight object for {val}"


def accessible(fn):
    @wraps(fn)
    def decorator(self, *args, **kwargs):
        return fn(TrueSight(self), *args, **kwargs)
    return decorator
