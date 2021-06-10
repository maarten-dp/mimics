from .deferred import Deferred
from .inspect import TrueSight
from .record import Recorder


class StasisTrap:
    """
    Used for deferring a known object or class
    """

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


class Mimic:
    """
    Used for deferring an unknown object or class
    """

    def __init__(self):
        self.recorders = {}

    def husk(self):
        recorder = Recorder()
        deferred = Deferred(recorder)
        self.recorders[id(deferred)] = recorder
        return deferred

    def absorb(self, husk):
        recorder = self.recorders[id(husk)]
        return FedMimic(recorder, husk)


class FedMimic:
    """
    A Mimic becomes a FedMimic once the object or class becomes known
    """

    def __init__(self, recorder, husk):
        self.recorder = recorder
        self.deferred = TrueSight(husk)

    def as_being(self, subject):
        self.deferred.subject = subject
        for deferred in self.recorder.deferred_objects:
            deferred.suspended = False
        self.recorder.play()
