"""Internal typed contracts; deliberately not the patented algorithm implementation."""
from dataclasses import dataclass
from enum import Enum
from math import isfinite
from typing import Tuple

CRITERIA_COUNT = 18


class ConnectionState(str, Enum):
    ONLINE = "online"
    DEGRADED = "degraded"
    OFFLINE = "offline"


@dataclass(frozen=True)
class ContextRequest:
    text: str
    language: str

    def __post_init__(self):
        if not isinstance(self.language, str) or self.language not in {"fr", "ar", "en"}:
            raise ValueError("Language must be fr, ar or en")
        if not isinstance(self.text, str) or not self.text.strip():
            raise ValueError("Request text must be nonempty")


@dataclass(frozen=True)
class CriterionVector:
    values: Tuple[float, ...]

    def __post_init__(self):
        if len(self.values) != CRITERIA_COUNT:
            raise ValueError("Exactly 18 criterion values required")
        if any(isinstance(x, bool) or not isinstance(x, (int, float)) or not isfinite(x) or x < 0 or x > 10 for x in self.values):
            raise ValueError("Criterion values must be finite numbers between 0 and 10")


@dataclass(frozen=True)
class WeightVector:
    values: Tuple[float, ...]

    def __post_init__(self):
        if len(self.values) != CRITERIA_COUNT:
            raise ValueError("Exactly 18 weights required")
        if any(isinstance(x, bool) or not isinstance(x, (int, float)) or not isfinite(x) or x < 0 for x in self.values):
            raise ValueError("Weights must be finite and nonnegative")
        if abs(sum(self.values) - 1.0) > 1e-8:
            raise ValueError("Weights must sum to 1")
