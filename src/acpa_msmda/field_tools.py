"""Session tools for supervised PE practice."""
from dataclasses import dataclass
import math

@dataclass(frozen=True)
class Timer:
    duration: int
    remaining: float
    started: float | None = None

    @classmethod
    def new(cls, seconds):
        if not 1 <= seconds <= 7200:
            raise ValueError("Invalid duration")
        return cls(seconds, float(seconds))

    def seconds_left(self, now):
        return max(0, math.ceil(self.remaining - (max(0, now-self.started) if self.started is not None else 0)))

    def start(self, now):
        return Timer(self.duration, self.remaining, now) if self.started is None and self.remaining > 0 else self

    def pause(self, now):
        return Timer(self.duration, max(0, self.remaining-max(0, now-self.started))) if self.started is not None else self

def change_count(value, delta):
    return max(0, int(value)+int(delta))

def rotation_assignments(groups, step):
    if not 1 <= groups <= 8:
        raise ValueError("Invalid group count")
    return [(i+step)%groups+1 for i in range(groups)]
