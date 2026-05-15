from __future__ import annotations

from pathlib import Path
import math

from .core import feigenbaum_estimates, invariant_density_r4, logistic, lyapunov_exponent, orbit_density, sample_tail, scan_periods, scan_superstable_doubling
from .svg import PlotBox, export_png_from_svg, svg_line, svg_paragraph, svg_text

REPO = Path(__file__).resolve().parents[1]
ASSETS = REPO / "assets"


def _header(width: int, height: int, title: str, subtitle: str) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">',
        '<defs>',
        '  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">',
        '    <stop offset="0%" stop-color="#081018"/>',
        '    <stop offset="100%" stop-color="#101d2a"/>',
        '  </linearGradient>',
        '  <style>',
        '    .title { font: 700 34px Helvetica, Arial, sans-serif; fill: #e6edf3; }',
        '    .subtitle { font: 500 18px Helvetica, Arial, sans-serif; fill: #9fb3c8; }',
        '    .label { font: 600 18px Helvetica, Arial, sans-serif; fill: #dce7f3; }',
        '    .small { font: 500 15px Helvetica, Arial, sans-serif; fill: #9fb3c8; }',
        '    .axis { stroke: #39516a; stroke-width: 2; }',
        '    .grid { stroke: #223445; stroke-width: 1; opacity: 0.8; }',
        '    .panel { fill: #122131; stroke: #5e7fa3; stroke-width: 2; rx: 18; }',
        '  </style>',
        '</defs>',
        f'<rect width="{width}" height="{height}" fill="url(#bg)"/>',
        svg_text(60, 58, title, 'title'),
        svg_text(60, 88, subtitle, 'subtitle'),
    ]


def bifurcation_svg() -> str:
    width, height = 1380, 920
    box = PlotBox(110, 130, 1290, 820, 2.8, 4.0, 0.0, 1.0)
    parts = _header(width, height, 'Logistic map bifurcation diagram', 'A one-line recurrence that still shows fixed points, period doubling, and chaos.')
    parts.append(f'<rect x="{box.left}" y="{box.top}" width="{box.right - box.left}" height="{box.bottom - box.top}" class="panel"/>')
    for tick in [3.0, 3.2, 3.4, 3.6, 3.8, 4.0]:
        x = box.sx(tick)
        parts.append(svg_line(x, box.top, x, box.bottom, 'grid'))
        parts.append(svg_text(x, 856, f'{tick:.1f}', 'small', 'middle'))
    for tick in [0.0, 0.25, 0.5, 0.75, 1.0]:
        y = box.sy(tick)
        parts.append(svg_line(box.left, y, box.right, y, 'grid'))
        parts.append(svg_text(84, y + 5, f'{tick:.2f}'.rstrip('0').rstrip('.'), 'small', 'end'))
    parts.append(svg_line(box.left, box.bottom, box.right, box.bottom, 'axis'))
    parts.append(svg_line(box.left, box.top, box.left, box.bottom, 'axis'))
    parts.append(svg_text((box.left + box.right) / 2, 884, 'growth parameter r', 'small', 'middle'))
    parts.append(svg_text(34, (box.top + box.bottom) / 2, 'long-run state x', 'small', 'middle', transform=f'rotate(-90 34 {(box.top + box.bottom) / 2:.1f})'))

    colors = {0: '#7dd3fc', 1: '#67e8f9', 2: '#c4b5fd'}
    commands = {key: [] for key in colors}
    samples = 1600
    for idx in range(samples):
        r = box.x_min + (box.x_max - box.x_min) * idx / (samples - 1)
        tail = sample_tail(r, warmup=900, keep=100)
        bucket = 0 if r < 3.55 else 1 if r < 3.86 else 2
        for x in tail:
            commands[bucket].append(f'M {box.sx(r):.2f} {box.sy(x):.2f} h 0.01')
    for bucket, color in colors.items():
        parts.append(f'<path d="{" ".join(commands[bucket])}" stroke="{color}" stroke-opacity="0.45" stroke-width="0.8" stroke-linecap="round" fill="none"/>')
    parts.append('</svg>')
    return '\n'.join(parts) + '\n'


def lyapunov_svg() -> str:
    width, height = 1380, 740
    box = PlotBox(110, 130, 1290, 620, 2.8, 4.0, -1.8, 0.8)
    parts = _header(width, height, 'Lyapunov exponent across the logistic map', 'Negative means nearby orbits collapse together. Positive means they separate exponentially.')
    parts.append(f'<rect x="{box.left}" y="{box.top}" width="{box.right - box.left}" height="{box.bottom - box.top}" class="panel"/>')
    zero = box.sy(0.0)
    parts.append(f'<rect x="{box.left}" y="{box.top}" width="{box.right - box.left}" height="{zero - box.top:.1f}" fill="#0f2d1f" opacity="0.38"/>')
    parts.append(f'<rect x="{box.left}" y="{zero:.1f}" width="{box.right - box.left}" height="{box.bottom - zero:.1f}" fill="#351226" opacity="0.34"/>')
    for tick in [3.0, 3.2, 3.4, 3.6, 3.8, 4.0]:
        x = box.sx(tick)
        parts.append(svg_line(x, box.top, x, box.bottom, 'grid'))
        parts.append(svg_text(x, 646, f'{tick:.1f}', 'small', 'middle'))
    for tick in [-1.5, -1.0, -0.5, 0.0, 0.5]:
        y = box.sy(tick)
        parts.append(svg_line(box.left, y, box.right, y, 'grid'))
        parts.append(svg_text(84, y + 5, f'{tick:.1f}', 'small', 'end'))
    parts.append(svg_line(box.left, zero, box.right, zero, 'axis'))
    parts.append(svg_line(box.left, box.top, box.left, box.bottom, 'axis'))
    parts.append(svg_line(box.left, box.bottom, box.right, box.bottom, 'axis'))
    parts.append(svg_text((box.left + box.right) / 2, 676, 'growth parameter r', 'small', 'middle'))
    parts.append(svg_text(34, (box.top + box.bottom) / 2, 'Lyapunov exponent λ', 'small', 'middle', transform=f'rotate(-90 34 {(box.top + box.bottom) / 2:.1f})'))

    points = []
    samples = 900
    for idx in range(samples):
        r = box.x_min + (box.x_max - box.x_min) * idx / (samples - 1)
        lam = lyapunov_exponent(r)
        points.append(f'{box.sx(r):.2f},{box.sy(lam):.2f}')
    parts.append(f'<polyline points="{" ".join(points)}" fill="none" stroke="#f472b6" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/>')
    parts.append(svg_text(1100, box.top + 36, 'positive λ → chaotic sensitivity', 'small'))
    parts.append(svg_text(1100, zero + 28, 'negative λ → stable / periodic', 'small'))
    parts.append('</svg>')
    return '\n'.join(parts) + '\n'


def cobweb_triptych_svg() -> str:
    width, height = 1320, 660
    parts = _header(width, height, 'Cobweb triptych: stable point, two-cycle, chaos', 'Three values of r are enough to show how the same recurrence changes character.')
    panel_width = 360
    gap = 30
    lefts = [80 + i * (panel_width + gap) for i in range(3)]
    rs = [2.9, 3.2, 3.7]
    subtitles = ['stable fixed point', 'period-two orbit', 'chaotic orbit']

    for idx, (left, r, subtitle) in enumerate(zip(lefts, rs, subtitles)):
        box = PlotBox(left, 170, left + panel_width, 560, 0.0, 1.0, 0.0, 1.0)
        parts.append(f'<rect x="{left}" y="{box.top}" width="{panel_width}" height="{box.bottom - box.top}" class="panel"/>')
        parts.append(svg_text(left, 148, f'r = {r:.1f}', 'label'))
        parts.append(svg_text(left + 110, 148, subtitle, 'small'))
        for tick in [0.0, 0.25, 0.5, 0.75, 1.0]:
            x = box.sx(tick)
            y = box.sy(tick)
            parts.append(svg_line(x, box.top, x, box.bottom, 'grid'))
            parts.append(svg_line(box.left, y, box.right, y, 'grid'))
        parts.append(svg_line(box.left, box.bottom, box.right, box.bottom, 'axis'))
        parts.append(svg_line(box.left, box.top, box.left, box.bottom, 'axis'))
        curve = []
        diagonal = []
        steps = 600
        for step in range(steps + 1):
            x = step / steps
            y = logistic(r, x)
            curve.append(f'{box.sx(x):.2f},{box.sy(y):.2f}')
            diagonal.append(f'{box.sx(x):.2f},{box.sy(x):.2f}')
        parts.append(f'<polyline points="{" ".join(curve)}" fill="none" stroke="#7dd3fc" stroke-width="3"/>')
        parts.append(f'<polyline points="{" ".join(diagonal)}" fill="none" stroke="#94a3b8" stroke-width="2" stroke-dasharray="8 8"/>')
        x = 0.21
        orbit = []
        for _ in range(42):
            y = logistic(r, x)
            orbit.append(f'{box.sx(x):.2f},{box.sy(x):.2f}')
            orbit.append(f'{box.sx(x):.2f},{box.sy(y):.2f}')
            orbit.append(f'{box.sx(y):.2f},{box.sy(y):.2f}')
            x = y
        parts.append(f'<polyline points="{" ".join(orbit)}" fill="none" stroke="#f97316" stroke-width="2.2" stroke-linejoin="round"/>')
    parts.append('</svg>')
    return '\n'.join(parts) + '\n'


def density_contrast_svg() -> str:
    width, height = 1380, 820
    parts = _header(width, height, 'Orbit-density contrast in the logistic map', 'At r = 4 the chaotic invariant measure piles up near the edges. In a period-3 window the mass collapses onto a few bands.')
    panel_width = 540
    gap = 60
    panel_top = 180
    panel_bottom = 690
    lefts = [110, 110 + panel_width + gap]
    boxes = [
        PlotBox(lefts[0], panel_top, lefts[0] + panel_width, panel_bottom, 0.0, 1.0, 0.0, 3.8),
        PlotBox(lefts[1], panel_top, lefts[1] + panel_width, panel_bottom, 0.0, 1.0, 0.0, 14.0),
    ]

    left_density = orbit_density(4.0, keep=50000, bins=64)
    right_density = orbit_density(3.83, keep=24000, bins=64)

    panel_meta = [
        (boxes[0], 'r = 4.0', 'empirical histogram plus exact invariant density', left_density, '#7dd3fc'),
        (boxes[1], 'r = 3.83', 'period-3 window: the orbit keeps revisiting a few narrow bands', right_density, '#c084fc'),
    ]

    for box, label, subtitle, density, color in panel_meta:
        parts.append(f'<rect x="{box.left}" y="{box.top}" width="{box.right - box.left}" height="{box.bottom - box.top}" class="panel"/>')
        parts.append(svg_text(box.left, box.top - 18, label, 'label'))
        parts.append(svg_text(box.left + 95, box.top - 18, subtitle, 'small'))
        for tick in [0.0, 0.25, 0.5, 0.75, 1.0]:
            x = box.sx(tick)
            parts.append(svg_line(x, box.top, x, box.bottom, 'grid'))
            parts.append(svg_text(x, box.bottom + 26, f'{tick:.2f}'.rstrip('0').rstrip('.'), 'small', 'middle'))
        top_tick = int(box.y_max)
        for tick in range(0, top_tick + 1):
            y = box.sy(float(tick))
            parts.append(svg_line(box.left, y, box.right, y, 'grid'))
            if tick < box.y_max + 1e-9:
                parts.append(svg_text(box.left - 20, y + 5, str(tick), 'small', 'end'))
        parts.append(svg_line(box.left, box.bottom, box.right, box.bottom, 'axis'))
        parts.append(svg_line(box.left, box.top, box.left, box.bottom, 'axis'))
        bar_width = (box.right - box.left) / len(density)
        for idx, (_, value) in enumerate(density):
            x0 = box.left + idx * bar_width
            clamped_value = min(box.y_max, value)
            y = box.sy(clamped_value)
            parts.append(
                f'<rect x="{x0 + 1:.2f}" y="{y:.2f}" width="{max(1.0, bar_width - 2):.2f}" height="{box.bottom - y:.2f}" fill="{color}" opacity="0.68"/>'
            )
        parts.append(svg_text((box.left + box.right) / 2, box.bottom + 54, 'state x', 'small', 'middle'))

    theory_points = []
    left_box = boxes[0]
    for step in range(1, 640):
        x = step / 640.0
        y = min(left_box.y_max, invariant_density_r4(x))
        theory_points.append(f'{left_box.sx(x):.2f},{left_box.sy(y):.2f}')
    parts.append(f'<polyline points="{" ".join(theory_points)}" fill="none" stroke="#f97316" stroke-width="3.2" stroke-linejoin="round" stroke-linecap="round"/>')
    parts.append(svg_paragraph(left_box.left + 300, left_box.top + 34, [
        'orange curve = exact density 1 / (π√(x(1-x)))',
        'blue bars = long-run histogram from 50,000 iterates',
    ], 'small'))

    right_box = boxes[1]
    parts.append(svg_paragraph(right_box.left + 278, right_box.top + 34, [
        'the mass collapses into a few spikes because',
        'the orbit falls into a period-3 window',
    ], 'small'))
    parts.append(svg_text(42, (panel_top + panel_bottom) / 2, 'density', 'small', 'middle', transform=f'rotate(-90 42 {(panel_top + panel_bottom) / 2:.1f})'))
    parts.append('</svg>')
    return '\n'.join(parts) + '\n'


def period_doubling_svg() -> str:
    width, height = 1440, 1000
    parts = _header(
        width,
        height,
        'Period windows and Feigenbaum drift',
        'A parameter scan finds stable periods directly, then the superstable points track how the doubling cascade compresses.',
    )

    scan_rows = scan_periods(3.0, 4.0, samples=820, warmup=2600, keep=256, max_period=64, tol=1e-8)
    superstable = scan_superstable_doubling(6)
    estimates = feigenbaum_estimates(superstable)

    top_box = PlotBox(90, 150, 1350, 500, 3.0, 4.0, -0.9, 7.5)
    left_box = PlotBox(90, 610, 690, 890, 0.5, 6.5, 2.96, 3.575)
    right_box = PlotBox(760, 610, 1350, 890, 8.0, 64.0, 4.0, 5.4)

    period_levels = {1: 6, 2: 5, 4: 4, 8: 3, 16: 2, 32: 1, 64: 0}
    period_colors = {
        1: '#7dd3fc',
        2: '#67e8f9',
        4: '#c4b5fd',
        8: '#f9a8d4',
        16: '#f59e0b',
        32: '#f97316',
        64: '#ef4444',
    }

    # top panel
    parts.append(f'<rect x="{top_box.left}" y="{top_box.top}" width="{top_box.right - top_box.left}" height="{top_box.bottom - top_box.top}" class="panel"/>')
    parts.append(svg_text(top_box.left, top_box.top - 18, 'Detected stable periods on a direct r-scan', 'label'))
    parts.append(svg_text(top_box.left + 420, top_box.top - 18, 'negative Lyapunov plus a repeating tail makes the windows explicit', 'small'))
    for tick in [3.0, 3.2, 3.4, 3.6, 3.8, 4.0]:
        x = top_box.sx(tick)
        parts.append(svg_line(x, top_box.top, x, top_box.bottom, 'grid'))
        parts.append(svg_text(x, top_box.bottom + 28, f'{tick:.1f}', 'small', 'middle'))
    labels = [(6, 'period 1'), (5, 'period 2'), (4, 'period 4'), (3, 'period 8'), (2, 'period 16'), (1, 'period 32'), (0, 'period 64'), (-0.65, 'chaos')]
    for y_val, label in labels:
        y = top_box.sy(y_val)
        parts.append(svg_line(top_box.left, y, top_box.right, y, 'grid'))
        parts.append(svg_text(top_box.left - 18, y + 5, label, 'small', 'end'))
    parts.append(svg_line(top_box.left, top_box.bottom, top_box.right, top_box.bottom, 'axis'))
    parts.append(svg_line(top_box.left, top_box.top, top_box.left, top_box.bottom, 'axis'))
    parts.append(svg_text((top_box.left + top_box.right) / 2, top_box.bottom + 58, 'growth parameter r', 'small', 'middle'))

    chaos_points: list[str] = []
    stable_points: dict[int, list[str]] = {period: [] for period in period_levels}
    other_points: list[str] = []
    for row in scan_rows:
        x = top_box.sx(row.r)
        if row.detected_period in stable_points:
            stable_points[row.detected_period].append(f'{x:.2f},{top_box.sy(period_levels[row.detected_period]):.2f}')
        elif row.detected_period is not None and row.lyapunov < 0.0:
            other_points.append(f'{x:.2f},{top_box.sy(6.75):.2f}')
        else:
            chaos_points.append(f'{x:.2f},{top_box.sy(-0.65):.2f}')
    if chaos_points:
        parts.append(f'<polyline points="{" ".join(chaos_points)}" fill="none" stroke="#94a3b8" stroke-opacity="0.35" stroke-width="2.2" stroke-linecap="round"/>')
    if other_points:
        parts.append(f'<polyline points="{" ".join(other_points)}" fill="none" stroke="#f8fafc" stroke-opacity="0.55" stroke-width="2.2" stroke-linecap="round"/>')
    for period, points in stable_points.items():
        if points:
            parts.append(f'<polyline points="{" ".join(points)}" fill="none" stroke="{period_colors[period]}" stroke-opacity="0.72" stroke-width="2.6" stroke-linecap="round"/>')

    parts.append(svg_paragraph(top_box.right - 300, top_box.top + 38, [
        'repeat search up to period 64',
        'otherwise count the point as chaos',
    ], 'small'))

    # bottom left panel: superstable points
    parts.append(f'<rect x="{left_box.left}" y="{left_box.top}" width="{left_box.right - left_box.left}" height="{left_box.bottom - left_box.top}" class="panel"/>')
    parts.append(svg_text(left_box.left, left_box.top - 18, 'Superstable doubling points', 'label'))
    parts.append(svg_text(left_box.left + 280, left_box.top - 18, 'the critical point x = 0.5 lands back on itself at each band center', 'small'))
    for tick in [3.0, 3.2, 3.4, 3.55]:
        y = left_box.sy(tick)
        parts.append(svg_line(left_box.left, y, left_box.right, y, 'grid'))
        parts.append(svg_text(left_box.left - 18, y + 5, f'{tick:.2f}'.rstrip('0').rstrip('.'), 'small', 'end'))
    for exponent in range(1, 7):
        x = left_box.sx(exponent)
        parts.append(svg_line(x, left_box.top, x, left_box.bottom, 'grid'))
        parts.append(svg_text(x, left_box.bottom + 26, str(2**exponent), 'small', 'middle'))
    parts.append(svg_line(left_box.left, left_box.bottom, left_box.right, left_box.bottom, 'axis'))
    parts.append(svg_line(left_box.left, left_box.top, left_box.left, left_box.bottom, 'axis'))
    parts.append(svg_text((left_box.left + left_box.right) / 2, left_box.bottom + 56, 'cycle period', 'small', 'middle'))
    parts.append(svg_text(38, (left_box.top + left_box.bottom) / 2, 'superstable parameter r', 'small', 'middle', transform=f'rotate(-90 38 {(left_box.top + left_box.bottom) / 2:.1f})'))
    coords = [f'{left_box.sx(math.log2(point.period)):.2f},{left_box.sy(point.r):.2f}' for point in superstable]
    parts.append(f'<polyline points="{" ".join(coords)}" fill="none" stroke="#60a5fa" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>')
    for point in superstable:
        x = left_box.sx(math.log2(point.period))
        y = left_box.sy(point.r)
        parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="5.2" fill="#dbeafe" stroke="#60a5fa" stroke-width="2"/>')

    # bottom right panel: Feigenbaum estimates
    parts.append(f'<rect x="{right_box.left}" y="{right_box.top}" width="{right_box.right - right_box.left}" height="{right_box.bottom - right_box.top}" class="panel"/>')
    parts.append(svg_text(right_box.left, right_box.top - 18, 'Gap-ratio estimates for δ', 'label'))
    parts.append(svg_text(right_box.left + 248, right_box.top - 18, 'gap ratios already lean toward the Feigenbaum constant', 'small'))
    for tick in [8, 16, 32, 64]:
        x = right_box.sx(float(tick))
        parts.append(svg_line(x, right_box.top, x, right_box.bottom, 'grid'))
        parts.append(svg_text(x, right_box.bottom + 26, str(tick), 'small', 'middle'))
    for tick in [4.2, 4.6, 5.0, 5.4]:
        y = right_box.sy(tick)
        parts.append(svg_line(right_box.left, y, right_box.right, y, 'grid'))
        parts.append(svg_text(right_box.left - 18, y + 5, f'{tick:.1f}', 'small', 'end'))
    delta_line = right_box.sy(4.6692)
    parts.append(f'<line x1="{right_box.left}" y1="{delta_line:.2f}" x2="{right_box.right}" y2="{delta_line:.2f}" stroke="#f8fafc" stroke-width="2" stroke-dasharray="8 8" opacity="0.85"/>')
    parts.append(svg_text(right_box.right - 36, delta_line - 10, 'Feigenbaum δ ≈ 4.6692', 'small', 'end'))
    parts.append(svg_line(right_box.left, right_box.bottom, right_box.right, right_box.bottom, 'axis'))
    parts.append(svg_line(right_box.left, right_box.top, right_box.left, right_box.bottom, 'axis'))
    parts.append(svg_text((right_box.left + right_box.right) / 2, right_box.bottom + 56, 'target period', 'small', 'middle'))
    estimate_points = [f'{right_box.sx(float(estimate.period)):.2f},{right_box.sy(estimate.delta):.2f}' for estimate in estimates]
    parts.append(f'<polyline points="{" ".join(estimate_points)}" fill="none" stroke="#f97316" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>')
    for estimate in estimates:
        x = right_box.sx(float(estimate.period))
        y = right_box.sy(estimate.delta)
        parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="5.0" fill="#fed7aa" stroke="#f97316" stroke-width="2"/>')
        parts.append(svg_text(x + 12, y - 14, f'{estimate.delta:.4f}', 'small'))

    parts.append(svg_paragraph(92, 940, [
        'Top: direct period detection on a dense r-scan. Bottom left: superstable points where the orbit of 0.5 lands back on 0.5.',
        'Bottom right: successive gap ratios already drift toward δ, even in this small public calculation.',
    ], 'small', line_height=18))
    parts.append('</svg>')
    return '\n'.join(parts) + '\n'


def write_gallery() -> list[Path]:
    ASSETS.mkdir(parents=True, exist_ok=True)
    files = {
        ASSETS / 'logistic-bifurcation.svg': bifurcation_svg(),
        ASSETS / 'lyapunov-sweep.svg': lyapunov_svg(),
        ASSETS / 'cobweb-triptych.svg': cobweb_triptych_svg(),
        ASSETS / 'density-contrast.svg': density_contrast_svg(),
        ASSETS / 'period-doubling-atlas.svg': period_doubling_svg(),
    }
    for path, content in files.items():
        path.write_text(content)
    export_png_from_svg(ASSETS / 'period-doubling-atlas.svg', ASSETS / 'period-doubling-atlas.png', size=1800, dpi=300)
    return list(files)
