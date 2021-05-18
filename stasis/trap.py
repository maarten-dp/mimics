from functools import wraps, partialmethod
import inspect

from .inspect import TrueSight, accessible
from .constants import MAGIC_METHODS
from .record import record, Recorder


def reroute_or_defer(attr):
    def decorator(self, *args, **kwargs):
        if not self.suspended:
            return getattr(self.subject, attr)(*args, **kwargs)
        return Deferred(self.recorder)
    decorator.__name__ = attr
    return accessible(record(decorator))


class StasisTrap:
    def __init__(self):
        self.recorders = {}

    def suspend(self, subject):
        recorder = Recorder()
        deferred = Deferred(recorder, subject)
        self.recorders[id(deferred)] = recorder
        return deferred

    def release(self, subject):
        recorder = self.recorders[id(subject)]
        for deferred in recorder.deferred_objects:
            deferred.suspended = False
        recorder.play()


class DeferredMeta(type):
    def __new__(cls, name, bases, attrs):
        overload = {mm: reroute_or_defer(mm) for mm in MAGIC_METHODS}
        overload.update(attrs)
        return super().__new__(cls,name, bases, overload)

    def __repr__(self):
        import pdb; pdb.set_trace()


class Deferred(metaclass=DeferredMeta):
    @accessible
    def __init__(self, recorder, subject=None):
        self.recorder = recorder
        self.subject = subject
        self.suspended = True
        self.cache = {}

        recorder.deferred_objects.append(self)

    @accessible
    @record
    def __getattr__(self, key):
        if not self.suspended:
            return getattr(self.subject, key)
        if key in self.cache:
            return self.cache[key]
        return Deferred(self.recorder)

    @accessible
    @record
    def __call__(self, *args, **kwargs):
        if not self.suspended:
            return self.subject(*args, **kwargs)
        return Deferred(self.recorder)

    def __getattribute__(self, key):
        raise AttributeError("This object's off limit, yo")


    @accessible
    def __str__(self):
        if not self.suspended:
            return str(self.subject)
        return str(self)


    @accessible
    def __repr__(self):
        if not self.suspended:
            return repr(self.subject)
        return repr(self)

    @accessible
    def __instancecheck__(self, inst):
        if not self.suspended:
            return self.subject.__instancecheck__(inst)
        return self.__class__.__instancecheck__(inst)
