from __future__ import annotations

import math


def logistic(r: float, x: float) -> float:
    return r * x * (1.0 - x)


def iterate(r: float, x0: float, steps: int) -> list[float]:
    x = x0
    values: list[float] = []
    for _ in range(steps):
        x = logistic(r, x)
        values.append(x)
    return values


def sample_tail(r: float, x0: float = 0.217, warmup: int = 900, keep: int = 120) -> list[float]:
    x = x0
    for _ in range(warmup):
        x = logistic(r, x)
    values: list[float] = []
    for _ in range(keep):
        x = logistic(r, x)
        values.append(x)
    return values


def lyapunov_exponent(r: float, x0: float = 0.217, warmup: int = 1200, keep: int = 500) -> float:
    x = x0
    for _ in range(warmup):
        x = logistic(r, x)
    total = 0.0
    for _ in range(keep):
        x = logistic(r, x)
        derivative = abs(r * (1.0 - 2.0 * x))
        total += math.log(max(1e-12, derivative))
    return total / keep
