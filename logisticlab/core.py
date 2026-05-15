from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class PeriodScanRow:
    r: float
    lyapunov: float
    detected_period: int | None


@dataclass(frozen=True)
class SuperstablePoint:
    period: int
    r: float


@dataclass(frozen=True)
class FeigenbaumEstimate:
    period: int
    r_prev_prev: float
    r_prev: float
    r_curr: float
    delta: float


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


def detect_period(values: list[float], max_period: int = 64, tol: float = 1e-8, repeats: int = 4) -> int | None:
    if max_period < 1:
        raise ValueError("max_period must be positive")
    for period in range(1, max_period + 1):
        needed = (repeats + 1) * period
        if len(values) < needed:
            break
        ok = True
        for repeat in range(1, repeats + 1):
            for idx in range(period):
                if abs(values[-1 - idx] - values[-1 - idx - repeat * period]) > tol:
                    ok = False
                    break
            if not ok:
                break
        if ok:
            return period
    return None


def classify_parameter(
    r: float,
    *,
    x0: float = 0.217,
    warmup: int = 2400,
    keep: int = 256,
    max_period: int = 64,
    tol: float = 1e-8,
) -> PeriodScanRow:
    tail = sample_tail(r, x0=x0, warmup=warmup, keep=keep)
    return PeriodScanRow(
        r=r,
        lyapunov=lyapunov_exponent(r, x0=x0, warmup=warmup, keep=max(keep, 400)),
        detected_period=detect_period(tail, max_period=max_period, tol=tol),
    )


def scan_periods(
    r_min: float,
    r_max: float,
    *,
    samples: int = 720,
    x0: float = 0.217,
    warmup: int = 2400,
    keep: int = 256,
    max_period: int = 64,
    tol: float = 1e-8,
) -> list[PeriodScanRow]:
    if samples < 2:
        raise ValueError("samples must be at least 2")
    rows: list[PeriodScanRow] = []
    for idx in range(samples):
        r = r_min + (r_max - r_min) * idx / (samples - 1)
        rows.append(
            classify_parameter(
                r,
                x0=x0,
                warmup=warmup,
                keep=keep,
                max_period=max_period,
                tol=tol,
            )
        )
    return rows


def superstable_error(r: float, period: int) -> float:
    x = 0.5
    for _ in range(period):
        x = logistic(r, x)
    return x - 0.5


def find_superstable_point(
    period: int,
    *,
    r_min: float,
    r_max: float,
    scan_steps: int = 8000,
    tol: float = 1e-12,
    max_iter: int = 80,
) -> float:
    if period < 1:
        raise ValueError("period must be positive")
    left_r = r_min
    left_value = superstable_error(left_r, period)
    for step in range(1, scan_steps + 1):
        right_r = r_min + (r_max - r_min) * step / scan_steps
        right_value = superstable_error(right_r, period)
        if left_value == 0.0:
            root = left_r
        elif left_value * right_value > 0.0:
            left_r, left_value = right_r, right_value
            continue
        else:
            a, b = left_r, right_r
            fa, fb = left_value, right_value
            for _ in range(max_iter):
                mid = 0.5 * (a + b)
                fm = superstable_error(mid, period)
                if abs(fm) <= tol or abs(b - a) <= tol:
                    root = mid
                    break
                if fa * fm <= 0.0:
                    b, fb = mid, fm
                else:
                    a, fa = mid, fm
            else:
                root = 0.5 * (a + b)
        row = classify_parameter(root, x0=0.5, warmup=max(4 * period, 1200), keep=max(8 * period, 128), max_period=max(period, 64))
        if row.detected_period == period:
            return root
        left_r, left_value = right_r, right_value
    raise ValueError(f"could not bracket a superstable point for period {period}")


def scan_superstable_doubling(max_power: int = 6) -> list[SuperstablePoint]:
    if max_power < 1:
        raise ValueError("max_power must be at least 1")
    points: list[SuperstablePoint] = []
    left = 3.0
    for power in range(1, max_power + 1):
        period = 2**power
        right = 3.57 if power >= 4 else 4.0
        root = find_superstable_point(period, r_min=left + 1e-6, r_max=right)
        points.append(SuperstablePoint(period=period, r=root))
        left = root
    return points


def feigenbaum_estimates(points: list[SuperstablePoint]) -> list[FeigenbaumEstimate]:
    if len(points) < 3:
        return []
    estimates: list[FeigenbaumEstimate] = []
    for idx in range(2, len(points)):
        prev_prev = points[idx - 2]
        prev = points[idx - 1]
        curr = points[idx]
        numerator = prev.r - prev_prev.r
        denominator = curr.r - prev.r
        estimates.append(
            FeigenbaumEstimate(
                period=curr.period,
                r_prev_prev=prev_prev.r,
                r_prev=prev.r,
                r_curr=curr.r,
                delta=numerator / denominator,
            )
        )
    return estimates
