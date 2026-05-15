from __future__ import annotations

from dataclasses import dataclass
from html import escape


@dataclass(frozen=True)
class PlotBox:
    left: float
    top: float
    right: float
    bottom: float
    x_min: float
    x_max: float
    y_min: float
    y_max: float

    def sx(self, x: float) -> float:
        return self.left + (x - self.x_min) / (self.x_max - self.x_min) * (self.right - self.left)

    def sy(self, y: float) -> float:
        return self.bottom - (y - self.y_min) / (self.y_max - self.y_min) * (self.bottom - self.top)


def svg_text(
    x: float,
    y: float,
    text: str,
    klass: str,
    anchor: str = "start",
    *,
    transform: str | None = None,
) -> str:
    transform_attr = f' transform="{transform}"' if transform else ""
    return f'<text x="{x:.1f}" y="{y:.1f}" class="{klass}" text-anchor="{anchor}"{transform_attr}>{escape(text)}</text>'


def svg_paragraph(
    x: float,
    y: float,
    lines: list[str],
    klass: str,
    *,
    anchor: str = "start",
    line_height: float = 20.0,
) -> str:
    tspans = [f'<tspan x="{x:.1f}" dy="0">{escape(lines[0])}</tspan>']
    tspans.extend(f'<tspan x="{x:.1f}" dy="{line_height:.1f}">{escape(line)}</tspan>' for line in lines[1:])
    return f'<text x="{x:.1f}" y="{y:.1f}" class="{klass}" text-anchor="{anchor}">{"".join(tspans)}</text>'


def svg_line(x1: float, y1: float, x2: float, y2: float, klass: str) -> str:
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" class="{klass}"/>'
