#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from logisticlab.core import compare_period_scans, feigenbaum_estimates, scan_periods, scan_superstable_doubling
from logisticlab.gallery import write_gallery

REPORTS = REPO / 'reports'


def write_period_report() -> Path:
    REPORTS.mkdir(parents=True, exist_ok=True)
    scan_rows = scan_periods(3.0, 4.0, samples=820, warmup=2600, keep=256, max_period=64, tol=1e-8)
    points = scan_superstable_doubling(6)
    estimates = feigenbaum_estimates(points)

    counts: dict[int, int] = {}
    chaos = 0
    for row in scan_rows:
        if row.detected_period is None:
            chaos += 1
        else:
            counts[row.detected_period] = counts.get(row.detected_period, 0) + 1

    total = len(scan_rows)
    lines = [
        '# Period windows and Feigenbaum drift',
        '',
        'This report adds a more explicit period-doubling lane to the repo. Instead of only showing the bifurcation picture, it scans the parameter axis directly, detects stable periods from the tail, and then measures the superstable centers of the doubling cascade.',
        '',
        '## Direct period scan',
        '',
        f'- chaotic or unresolved points on this scan: {chaos}/{total} ({chaos / total:.1%})',
    ]
    for period in [1, 2, 4, 8, 16, 32, 64]:
        count = counts.get(period, 0)
        lines.append(f'- detected period {period}: {count}/{total} ({count / total:.1%})')

    lines.extend(
        [
            '',
            'This is not a proof that the whole interval has that exact period. It is a sampled public summary. But it is enough to make the stable windows show up as a real scan object instead of a vague visual impression.',
            '',
            '## Superstable points',
            '',
            'At the center of a stable band, the critical point `x = 0.5` falls back onto itself after one whole cycle. Those are the superstable points used in the lower panels of the new figure.',
            '',
        ]
    )
    for point in points:
        lines.append(f'- period {point.period}: r ≈ {point.r:.12f}')

    lines.extend(['', '## Feigenbaum gap-ratio estimates', ''])
    for estimate in estimates:
        lines.append(f'- using periods {estimate.period // 4}, {estimate.period // 2}, and {estimate.period}: δ ≈ {estimate.delta:.6f}')

    lines.extend(
        [
            '',
            '## Reading',
            '',
            '- the top scan makes the stable windows explicit: low periods occupy wide clean bands, then the doubling cascade compresses as chaos takes over more of the axis',
            '- the superstable sequence climbs toward the chaos onset near `r ≈ 3.57`, which is why the lower-left plot bunches up so quickly',
            '- the δ estimates are still rough because this is a small public calculation, but the drift is already in the right direction and makes the scaling story visible',
            '',
            'Open `assets/period-doubling-atlas.svg`, `assets/period-doubling-atlas.png`, and `notebooks/period_doubling_feigenbaum.ipynb` next.',
        ]
    )

    report_path = REPORTS / 'period-doubling-and-feigenbaum.md'
    report_path.write_text('\n'.join(lines) + '\n')
    return report_path


def write_sensitivity_report() -> Path:
    REPORTS.mkdir(parents=True, exist_ok=True)
    rows = compare_period_scans(3.0, 4.0, samples=820, short_warmup=1200, short_keep=64, deep_warmup=3600, deep_keep=512, max_period=64, tol=1e-8)

    recovered = [row for row in rows if row.recovered_stable]
    shifted = [row for row in rows if row.shifted_period]
    lost = [row for row in rows if row.lost_stable]
    deepest = max((row.deep_row.detected_period or 0) for row in rows)
    earliest_recovered = min(recovered, key=lambda row: row.r) if recovered else None
    latest_recovered = max(recovered, key=lambda row: row.r) if recovered else None

    def short_count(period: int | None) -> int:
        return sum(1 for row in rows if row.short_row.detected_period == period)

    def deep_count(period: int | None) -> int:
        return sum(1 for row in rows if row.deep_row.detected_period == period)

    lines = [
        '# Period-scan sensitivity',
        '',
        'This report asks a narrower question than the main period-doubling atlas: how much of the stable-window picture disappears if the scan tail is too short?',
        '',
        'The comparison keeps the same `r` grid and the same tolerance. Only the scan patience changes:',
        '',
        '- short scan: `warmup = 1200`, `keep = 64`',
        '- deep scan: `warmup = 3600`, `keep = 512`',
        '',
        '## Main read',
        '',
        f'- recovered stable points in the deeper scan: {len(recovered)}/{len(rows)} ({len(recovered) / len(rows):.1%})',
        f'- stable points lost by the deeper scan: {len(lost)}',
        f'- period shifts between two stable detections: {len(shifted)}',
        f'- deepest detected period in the deeper scan: {deepest}',
    ]
    if earliest_recovered is not None and latest_recovered is not None:
        lines.append(
            f'- recovered windows start showing up around `r ≈ {earliest_recovered.r:.6f}` and keep appearing as late as `r ≈ {latest_recovered.r:.6f}`'
        )

    lines.extend([
        '',
        '## Count comparison',
        '',
        f'- period 2: short {short_count(2)}, deep {deep_count(2)}',
        f'- period 4: short {short_count(4)}, deep {deep_count(4)}',
        f'- period 8: short {short_count(8)}, deep {deep_count(8)}',
        f'- period 16: short {short_count(16)}, deep {deep_count(16)}',
        f'- period 32: short {short_count(32)}, deep {deep_count(32)}',
        f'- chaos or unresolved: short {short_count(None)}, deep {deep_count(None)}',
        '',
        '## Reading',
        '',
        '- the short scan does not rewrite the whole picture; it mainly erases the thin stable bands near chaos onset and a few narrower windows farther right',
        '- that means the cutoff problem is selective, not uniform: the wide low-period windows survive, while the narrow ones disappear first',
        '- a deeper tail also resolves some windows to higher periods instead of only flipping chaos to stable, which is why the zoom panel shows orange points climbing above the blue ones',
        '',
        'Open `assets/period-scan-sensitivity.svg`, `assets/period-scan-sensitivity.png`, and `notebooks/period_scan_sensitivity.ipynb` next.',
    ])

    report_path = REPORTS / 'period-scan-sensitivity.md'
    report_path.write_text('\n'.join(lines) + '\n')
    return report_path


def main() -> None:
    for path in write_gallery():
        print(path)
    print(write_period_report())
    print(write_sensitivity_report())


if __name__ == '__main__':
    main()
