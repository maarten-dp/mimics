from functools import wraps

from .inspect import TrueSight, shape_shift, WHITELISTED


# If I'm raised, I probably didn't use a TrueSight obj where I needed to
def ensure_truesight(_accessed, *args, **kwargs):
    if not _accessed == "__getattr__":
        return
    arg = args[0]
    if arg in WHITELISTED:
        raise Exception("Investigate me")


def record(fn):
    @wraps(fn)
    def decorator(self, *args, **kwargs):
        return_deferred = fn(self, *args, **kwargs)
        ensure_truesight(fn.__name__, *args, **kwargs)
        if self.suspended:
            record = Record(self, fn.__name__, args, kwargs, return_deferred)
            self.recorder.record(record)
        return return_deferred

    return decorator


class Record:
    def __init__(self, deferred, action, args, kwargs, return_deferred):
        action_handlers = {
            "__call__": self._handle_call,
            "subclassed": self._handle_subclass,
        }

        self.deferred = deferred
        self.action = action
        self.handler = action_handlers.get(action, self._handle_default)
        self.args = args
        self.kwargs = kwargs
        self.return_deferred = TrueSight(return_deferred)

    @property
    def subject(self):
        return self.deferred.subject

    def perform(self):
        result = self.handler()
        is_checkable = hasattr(self.return_deferred, "is_deferred_object")
        is_deferred = self.return_deferred.is_deferred_object()
        if is_checkable and is_deferred:
            self.return_deferred.subject = result
            shape_shift(self.return_deferred.subject, self.return_deferred.obj)

    def _handle_call(self):
        return self.subject(*self.args, **self.kwargs)

    def _handle_subclass(self):
        name, bases, attrs = self.args

        bases = list(bases)
        bases[bases.index(self.deferred.obj)] = self.deferred.subject

        return type(name, tuple(bases), attrs)

    def _handle_default(self):
        action = getattr(self.subject, self.action)
        return action(*self.args, **self.kwargs)

    def __repr__(self):
        return (
            f"Deferred: {self.deferred}\n"
            f"Subject: {self.subject}\n"
            f"Action: {self.action}\n"
            f"Args: {self.args}\n"
            f"Kwargs: {self.kwargs}\n"
            f"return_deferred: {self.return_deferred}\n"
        )


class Recorder:
    def __init__(self):
        self.records = []
        self.deferred_objects = []

    def record(self, record):
        self.records.append(record)

    def play(self):
        for record in self.records:
            record.perform()
