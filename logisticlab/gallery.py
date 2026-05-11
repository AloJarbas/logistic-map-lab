from __future__ import annotations

from pathlib import Path

from .core import iterate, logistic, lyapunov_exponent, sample_tail
from .svg import PlotBox, svg_line, svg_text

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
    width, height = 1400, 900
    box = PlotBox(90, 120, 1320, 820, 2.8, 4.0, 0.0, 1.0)
    parts = _header(width, height, 'Logistic map bifurcation diagram', 'A one-line recurrence that still shows fixed points, period doubling, and chaos.')
    parts.append(f'<rect x="{box.left}" y="{box.top}" width="{box.right - box.left}" height="{box.bottom - box.top}" class="panel"/>')
    for tick in [3.0, 3.2, 3.4, 3.6, 3.8, 4.0]:
        x = box.sx(tick)
        parts.append(svg_line(x, box.top, x, box.bottom, 'grid'))
        parts.append(svg_text(x, 856, f'{tick:.1f}', 'small', 'middle'))
    for tick in [0.0, 0.25, 0.5, 0.75, 1.0]:
        y = box.sy(tick)
        parts.append(svg_line(box.left, y, box.right, y, 'grid'))
        parts.append(svg_text(56, y + 5, f'{tick:.2f}'.rstrip('0').rstrip('.'), 'small'))
    parts.append(svg_line(box.left, box.bottom, box.right, box.bottom, 'axis'))
    parts.append(svg_line(box.left, box.top, box.left, box.bottom, 'axis'))
    parts.append(svg_text((box.left + box.right) / 2, 885, 'growth parameter r', 'small', 'middle'))
    parts.append(svg_text(28, (box.top + box.bottom) / 2, 'long-run state x', 'small', 'middle'))

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
    width, height = 1400, 700
    box = PlotBox(90, 120, 1320, 610, 2.8, 4.0, -1.8, 0.8)
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
        parts.append(svg_text(46, y + 5, f'{tick:.1f}', 'small'))
    parts.append(svg_line(box.left, zero, box.right, zero, 'axis'))
    parts.append(svg_line(box.left, box.top, box.left, box.bottom, 'axis'))
    parts.append(svg_line(box.left, box.bottom, box.right, box.bottom, 'axis'))

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
    width, height = 1500, 560
    parts = _header(width, height, 'Cobweb triptych: stable point, two-cycle, chaos', 'Three values of r are enough to show how the same recurrence changes character.')
    panel_width = 420
    gap = 30
    lefts = [80 + i * (panel_width + gap) for i in range(3)]
    rs = [2.9, 3.2, 3.7]
    subtitles = ['stable fixed point', 'period-two orbit', 'chaotic orbit']

    for idx, (left, r, subtitle) in enumerate(zip(lefts, rs, subtitles)):
        box = PlotBox(left, 150, left + panel_width, 500, 0.0, 1.0, 0.0, 1.0)
        parts.append(f'<rect x="{left}" y="{box.top}" width="{panel_width}" height="{box.bottom - box.top}" class="panel"/>')
        parts.append(svg_text(left, 132, f'r = {r:.1f}', 'label'))
        parts.append(svg_text(left + 110, 132, subtitle, 'small'))
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


def write_gallery() -> list[Path]:
    ASSETS.mkdir(parents=True, exist_ok=True)
    files = {
        ASSETS / 'logistic-bifurcation.svg': bifurcation_svg(),
        ASSETS / 'lyapunov-sweep.svg': lyapunov_svg(),
        ASSETS / 'cobweb-triptych.svg': cobweb_triptych_svg(),
    }
    for path, content in files.items():
        path.write_text(content)
    return list(files)
