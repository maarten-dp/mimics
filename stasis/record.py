from functools import wraps

from .inspect import TrueSight


def record(fn):
    @wraps(fn)
    def decorator(self, *args, **kwargs):
        return_deferred = fn(self, *args, **kwargs)
        record = Record(self, fn.__name__, args, kwargs, return_deferred)
        self.recorder.record(record)
        return return_deferred
    return decorator


class Record:
    def __init__(self, deferred, action, args, kwargs, return_deferred):
        self.deferred = deferred
        self.action = action
        self.args = args
        self.kwargs = kwargs
        self.return_deferred = TrueSight(return_deferred)

    @property
    def subject(self):
        return self.deferred.subject

    def perform(self):
        if self.action == '__call__':
            result = self.subject(*self.args, **self.kwargs)
        else:
            if self.action == '__getattr__':
                self.action = '__getattribute__'
            action = getattr(self.subject, self.action)
            result = action(*self.args, **self.kwargs)
        self.return_deferred.subject = result

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
