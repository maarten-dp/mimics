from functools import wraps
import inspect


WHITELISTED = [
    "recorder",
    "subject",
    "suspended",
    "cache",
    "_init_as_instance",
]


def accessible(fn):
    @wraps(fn)
    def decorator(self, *args, **kwargs):
        return fn(TrueSight(self), *args, **kwargs)

    return decorator


class TrueSight:
    def __init__(self, obj):
        object.__setattr__(self, "obj", obj)

    def __getattr__(self, key):
        if key not in WHITELISTED:
            raise AttributeError(f"Deferred has no attribute {key}")
        return object.__getattribute__(self.obj, key)

    def __setattr__(self, key, value):
        setattr(self.obj, key, value)

    def get(self, key):
        return self.__getattr__(key)

    def __repr__(self):
        val = object.__repr__(self.obj)
        return f"TrueSight object for {val}"

    def is_deferred_object(self):
        cls_name = object.__getattribute__(self.obj, "__class__").__name__
        return "Deferred" in cls_name


def shape_shift(target, destination):
    if not TrueSight(destination).is_deferred_object():
        return

    def reroute(member, subject):
        def decorator(self, *args, **kwargs):
            return getattr(subject, member)(*args, **kwargs)

        return decorator

    def reroute_to_fn(fn):
        def decorator(self, *args, **kwargs):
            return fn(target, *args, **kwargs)

        return decorator

    def reroute_direct(fn):
        def decorator(self, *args, **kwargs):
            return fn(*args, **kwargs)

        return decorator

    methods = {}
    candidate = target.__class__
    if inspect.isclass(target):
        candidate = target
        methods["__call__"] = reroute_direct(target)
        methods["__instancecheck__"] = reroute_direct(target.__instancecheck__)

    members = dict(inspect.getmembers(candidate))
    for member_name, member in members.items():
        if callable(member):
            methods[member_name] = reroute(member_name, target)

    methods["__getattribute__"] = reroute_to_fn(getattr)
    methods["__repr__"] = reroute_to_fn(repr)
    methods["__str__"] = reroute_to_fn(str)
    methods["__setattr__"] = reroute_to_fn(setattr)

    Proxy = type("Proxy", tuple(), methods)
    destination.__class__ = Proxy
