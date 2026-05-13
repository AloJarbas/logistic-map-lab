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


def histogram_density(values: list[float], bins: int = 60, x_min: float = 0.0, x_max: float = 1.0) -> list[tuple[float, float]]:
    width = (x_max - x_min) / bins
    counts = [0] * bins
    for value in values:
        if value < x_min or value > x_max:
            continue
        idx = min(bins - 1, max(0, int((value - x_min) / width)))
        counts[idx] += 1
    total = max(1, sum(counts))
    return [
        (x_min + (idx + 0.5) * width, count / (total * width))
        for idx, count in enumerate(counts)
    ]


def orbit_density(r: float, x0: float = 0.217, warmup: int = 4000, keep: int = 40000, bins: int = 60) -> list[tuple[float, float]]:
    return histogram_density(sample_tail(r, x0=x0, warmup=warmup, keep=keep), bins=bins)


def invariant_density_r4(x: float) -> float:
    clipped = min(1.0 - 1e-12, max(1e-12, x))
    return 1.0 / (math.pi * math.sqrt(clipped * (1.0 - clipped)))


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
