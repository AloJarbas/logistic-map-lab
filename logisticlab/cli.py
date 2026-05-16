from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core import classify_parameter, compare_period_scans, feigenbaum_estimates, scan_periods, scan_superstable_doubling
from .gallery import period_doubling_svg, period_sensitivity_svg
from .svg import export_png_from_svg


def main() -> None:
    parser = argparse.ArgumentParser(description='Logistic map lab utilities')
    subparsers = parser.add_subparsers(dest='command', required=True)

    classify_parser = subparsers.add_parser('classify', help='classify one parameter by Lyapunov sign and detected period')
    classify_parser.add_argument('--r', type=float, required=True)
    classify_parser.add_argument('--warmup', type=int, default=2400)
    classify_parser.add_argument('--keep', type=int, default=256)
    classify_parser.add_argument('--max-period', type=int, default=64)

    scan_parser = subparsers.add_parser('period-scan', help='scan detected stable periods across an r-range')
    scan_parser.add_argument('--r-min', type=float, default=3.0)
    scan_parser.add_argument('--r-max', type=float, default=4.0)
    scan_parser.add_argument('--samples', type=int, default=820)
    scan_parser.add_argument('--warmup', type=int, default=2400)
    scan_parser.add_argument('--keep', type=int, default=256)
    scan_parser.add_argument('--max-period', type=int, default=64)

    superstable_parser = subparsers.add_parser('superstable', help='report superstable doubling points and Feigenbaum estimates')
    superstable_parser.add_argument('--max-power', type=int, default=6)

    render_parser = subparsers.add_parser('render-period-doubling', help='render the period-doubling atlas figure')
    render_parser.add_argument('--output', type=Path, required=True)
    render_parser.add_argument('--png-output', type=Path, default=None)

    sensitivity_parser = subparsers.add_parser('compare-period-scans', help='compare a short and deep period scan and optionally render the sensitivity figure')
    sensitivity_parser.add_argument('--r-min', type=float, default=3.0)
    sensitivity_parser.add_argument('--r-max', type=float, default=4.0)
    sensitivity_parser.add_argument('--samples', type=int, default=820)
    sensitivity_parser.add_argument('--short-warmup', type=int, default=1200)
    sensitivity_parser.add_argument('--short-keep', type=int, default=64)
    sensitivity_parser.add_argument('--deep-warmup', type=int, default=3600)
    sensitivity_parser.add_argument('--deep-keep', type=int, default=512)
    sensitivity_parser.add_argument('--max-period', type=int, default=64)
    sensitivity_parser.add_argument('--tol', type=float, default=1e-8)
    sensitivity_parser.add_argument('--output', type=Path, default=None)
    sensitivity_parser.add_argument('--png-output', type=Path, default=None)

    args = parser.parse_args()

    if args.command == 'classify':
        row = classify_parameter(args.r, warmup=args.warmup, keep=args.keep, max_period=args.max_period)
        print(json.dumps({'r': row.r, 'lyapunov': row.lyapunov, 'detected_period': row.detected_period}, indent=2))
        return

    if args.command == 'period-scan':
        rows = scan_periods(
            args.r_min,
            args.r_max,
            samples=args.samples,
            warmup=args.warmup,
            keep=args.keep,
            max_period=args.max_period,
        )
        payload = [
            {'r': round(row.r, 8), 'lyapunov': round(row.lyapunov, 8), 'detected_period': row.detected_period}
            for row in rows
        ]
        print(json.dumps(payload, indent=2))
        return

    if args.command == 'superstable':
        points = scan_superstable_doubling(args.max_power)
        estimates = feigenbaum_estimates(points)
        print(
            json.dumps(
                {
                    'points': [{'period': row.period, 'r': round(row.r, 12)} for row in points],
                    'estimates': [{'period': row.period, 'delta': round(row.delta, 8)} for row in estimates],
                },
                indent=2,
            )
        )
        return

    if args.command == 'compare-period-scans':
        rows = compare_period_scans(
            args.r_min,
            args.r_max,
            samples=args.samples,
            short_warmup=args.short_warmup,
            short_keep=args.short_keep,
            deep_warmup=args.deep_warmup,
            deep_keep=args.deep_keep,
            max_period=args.max_period,
            tol=args.tol,
        )
        if args.output is not None:
            content = period_sensitivity_svg(
                r_min=args.r_min,
                r_max=args.r_max,
                samples=args.samples,
                short_warmup=args.short_warmup,
                short_keep=args.short_keep,
                deep_warmup=args.deep_warmup,
                deep_keep=args.deep_keep,
                max_period=args.max_period,
                tol=args.tol,
            )
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(content)
            if args.png_output is not None:
                export_png_from_svg(args.output, args.png_output, size=1800, dpi=300)
        payload = {
            'samples': len(rows),
            'recovered_stable': sum(1 for row in rows if row.recovered_stable),
            'lost_stable': sum(1 for row in rows if row.lost_stable),
            'shifted_period': sum(1 for row in rows if row.shifted_period),
        }
        print(json.dumps(payload, indent=2))
        return

    content = period_doubling_svg()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(content)
    if args.png_output is not None:
        export_png_from_svg(args.output, args.png_output, size=1800, dpi=300)
    print(args.output)


if __name__ == '__main__':
    main()
