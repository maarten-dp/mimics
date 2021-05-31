from functools import wraps
import inspect


WHITELISTED = [
    "recorder",
    "subject",
    "suspended",
    "acting_as",
    "cache",
    "metadata",
    "_init_as_class",
    "_init_as_instance"
]



from functools import wraps, partialmethod


def accessible(fn):
    @wraps(fn)
    def decorator(self, *args, **kwargs):
        return fn(TrueSight(self), *args, **kwargs)
    return decorator


def reroute_wrapper(fn):
    @wraps(fn)
    def decorator(self, *args, **kwargs):
        return fn(*args, **kwargs)
    return decorator



class TrueSight:
    def __init__(self, obj):
        object.__setattr__(self, 'obj', obj)

    def __getattr__(self, key):
        if key not in WHITELISTED:
            raise AttributeError(f'Deferred has no attribute {key}')
        return object.__getattribute__(self.obj, key)

    def __setattr__(self, key, value):
        setattr(self.obj, key, value)

    def get(self, key):
        return self.__getattr__(key)

    def __repr__(self):
        val = object.__repr__(self.obj)
        return f"TrueSight object for {val}"

    def is_deferred_object(self):
        return "Deferred" in object.__getattribute__(self.obj, '__class__').__name__


def shape_shift(target, destination):
    from .deferred import UncallableDeferred

    if not TrueSight(destination).is_deferred_object():
        return

    def raise_error(*a, **kw):
        raise AttributeError()

    def reroute(member, subject):
        def decorator(self, *args, **kwargs):
            return getattr(subject, member)(*args, **kwargs)
        return decorator

    methods = {}
    candidate = target.__class__
    if inspect.isclass(target):
        candidate = target
        methods['__call__'] = lambda s, *a, **kw: target(*a, **kw)
        methods['__instancecheck__'] = lambda s, *a, **kw: target.__instancecheck__(*a, **kw)
    members = dict(inspect.getmembers(candidate))

    for member_name, member in members.items():
        if callable(member):
            methods[member_name] = reroute(member_name, target)
    methods['__getattr__'] = lambda s, *a, **kw: getattr(target, *a, **kw)
    methods['__getattribute__'] = raise_error
    methods['__repr__'] = lambda s, *a, **kw: repr(target, *a, **kw)
    methods['__str__'] = lambda s, *a, **kw: str(target, *a, **kw)
    methods['__setattr__'] = lambda s, *a, **kw: setattr(target, *a, **kw)
    Proxy = type('Proxy', tuple(), methods)
    destination.__class__ = Proxy
