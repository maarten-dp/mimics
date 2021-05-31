from functools import wraps, partialmethod
import inspect
from enum import Enum

from .inspect import TrueSight, accessible
from .constants import MAGIC_METHODS
from .record import record, Recorder, Record


class Identity(Enum):
    INSTANCE = 1
    KLASS = 2


def reroute_or_defer(attr):
    def decorator(self, *args, **kwargs):
        if not self.suspended:
            return getattr(self.subject, attr)(*args, **kwargs)
        return Deferred(self.recorder)
    decorator.__name__ = attr
    return accessible(record(decorator))


class DeferredMeta(type):
    def __new__(cls, name, bases, attrs):
        overload = {mm: reroute_or_defer(mm) for mm in MAGIC_METHODS}
        overload.update(attrs)
        return super().__new__(cls,name, bases, overload)


class UncallableDeferred(metaclass=DeferredMeta):
    def __new__(cls, *args, **kwargs):
        # Acting as class creating an instance
        if len(args) <= 2:
            return super().__new__(cls)

        # Acting as metaclass creating a class
        name, bases, attrs = args
        deferred_obj = TrueSight([d for d in bases if isinstance(d, cls)][0])

        klass = Deferred(deferred_obj.recorder)

        handle = TrueSight(klass)
        handle.acting_as = Identity.KLASS
        deferred_obj.recorder.record(Record(
            deferred_obj, "subclassed", args, kwargs, klass
        ))
        print(f"recording subclassed: {args} -- {kwargs}")

        return klass

    @accessible
    def __init__(self, *args, **kwargs):
        if hasattr(self, 'acting_as') and self.acting_as is Identity.KLASS:
            pass
        else:
            self._init_as_instance(*args, **kwargs)

    @accessible
    def _init_as_instance(self, recorder, subject=None):
        self.recorder = recorder
        self.subject = subject
        self.suspended = True
        self.acting_as = Identity.INSTANCE
        self.cache = {}
        self.metadata = {}

        recorder.deferred_objects.append(self)

    @accessible
    @record
    def __getattr__(self, key):
        if not self.suspended:
            return getattr(self.subject, key)
        if key in self.cache:
            return self.cache[key]
        return_val = Deferred(self.recorder)
        self.cache[key] = return_val
        return return_val

    def __getattribute__(self, key):
        # Reroute to __getattr__ everytime
        raise AttributeError(
            "This object's off limit, yo. Find yaself a TrueSight spell"
        )

    @accessible
    def __str__(self):
        if not self.suspended:
            return str(self.subject)
        return str(self)

    @accessible
    def __repr__(self):
        if not self.suspended:
            return "<Unsuspended {}>".format(repr(self.subject))
        return object.__repr__(self.obj)

    @accessible
    def __instancecheck__(self, inst):
        if not self.suspended:
            return self.subject.__instancecheck__(inst)
        return self.__class__.__instancecheck__(inst)


class Deferred(UncallableDeferred):
    @accessible
    @record
    def __call__(self, *args, **kwargs):
        if not self.suspended:
            return self.subject(*args, **kwargs)
        return Deferred(self.recorder)
