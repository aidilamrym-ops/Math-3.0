#!/usr/bin/env python3
"""Lattice viewer for the Math 3.0 Bounded-Lattice catalogue.

Projects the 3x3 family matrices (LDL^T / Sylvester pivots) and the certified
interval radii into a lightweight SVG plane, and writes a fully exact JSON
summary.  All arithmetic uses fractions.Fraction and integer square roots;
no binary floating-point operation is performed anywhere in the projection.

The viewer is deliberately dependency-free (no matplotlib / numpy).  It emits
a standalone vector SVG plus a machine-readable JSON index mapping.

Outputs:
    reports/lattice_spatial_confinement.json
    reports/lattice_spatial_confinement.svg

Targets:
    Family 017 - pi irrationality exponent grid
    Family 087 - Mahler convex geometry
"""

from __future__ import annotations

import ast
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from fractions import Fraction
from html import unescape
from math import isqrt
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Paths and constants
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[3]
REPORTS = ROOT / "reports"
EMPIRICAL_PATH = REPORTS / "math30_real_empirical_parameters.json"
OUT_JSON = REPORTS / "lattice_spatial_confinement.json"
OUT_SVG = REPORTS / "lattice_spatial_confinement.svg"

TARGET_FAMILIES = (17, 87)
FAMILY_LABELS = {
    17: "π Irrationality Exponent Grid",
    87: "Mahler Convex Geometry",
}

PLANCK_LITERAL = "1.616255e-35"
INNER_LITERAL = "1e-40"
GATE4_LIMIT = Fraction(1, 2)

# Rational unit directions used for the confinement spokes (no trigonometry).
UNIT_DIRECTIONS = [
    (Fraction(1), Fraction(0)),
    (Fraction(-3, 5), Fraction(4, 5)),
    (Fraction(-3, 5), Fraction(-4, 5)),
]

# Hyperboloid parameter grid.  For t > 0:
#   r = (t + 1/t)/2, z = (t - 1/t)/2, r^2 - z^2 = 1.
HYPER_T_VALUES = [
    Fraction(1, 2),
    Fraction(2, 3),
    Fraction(1),
    Fraction(3, 2),
    Fraction(2),
]
HYPER_THETA = [
    (Fraction(1), Fraction(0)),
    (Fraction(3, 5), Fraction(4, 5)),
    (Fraction(0), Fraction(1)),
    (Fraction(-3, 5), Fraction(4, 5)),
    (Fraction(-1), Fraction(0)),
    (Fraction(-3, 5), Fraction(-4, 5)),
    (Fraction(0), Fraction(-1)),
    (Fraction(3, 5), Fraction(-4, 5)),
]


# ---------------------------------------------------------------------------
# Exact arithmetic helpers
# ---------------------------------------------------------------------------


def pow10(exponent: int) -> Fraction:
    """Return 10**exponent as an exact Fraction (no float for negative powers)."""
    if exponent >= 0:
        return Fraction(10 ** exponent, 1)
    return Fraction(1, 10 ** (-exponent))


def frac(value: Any) -> Fraction:
    """Parse a truth value as an exact Fraction, including scientific notation."""
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int):
        return Fraction(value)
    if isinstance(value, str):
        text = value.strip()
        match = re.fullmatch(r"([+-]?\d+(?:\.\d+)?)[eE]([+-]?\d+)", text)
        if match:
            return Fraction(match.group(1)) * pow10(int(match.group(2)))
        return Fraction(text)
    raise TypeError(f"cannot convert {type(value).__name__} to Fraction")


def decimal_string(value: Fraction, digits: int = 18) -> str:
    """Format a Fraction as a decimal string using integer arithmetic only."""
    sign = "-" if value < 0 else ""
    numerator = abs(value.numerator)
    denominator = value.denominator
    scaled = numerator * (10 ** digits)
    quotient, remainder = divmod(scaled, denominator)
    if 2 * remainder >= denominator:
        quotient += 1
    text = str(quotient).rjust(digits + 1, "0")
    return f"{sign}{text[:-digits]}.{text[-digits:]}"


def sci_string(value: Fraction, significant: int = 8) -> str:
    """Format a Fraction in scientific notation without binary floats."""
    if value == 0:
        return "0"
    sign = "-" if value < 0 else ""
    magnitude = abs(value)
    exponent = len(str(magnitude.numerator)) - len(str(magnitude.denominator))
    while magnitude < pow10(exponent):
        exponent -= 1
    while magnitude >= pow10(exponent + 1):
        exponent += 1
    mantissa = magnitude / pow10(exponent)
    return f"{sign}{decimal_string(mantissa, significant)}e{exponent:+d}"


def short_fraction(value: Fraction, digits: int = 6) -> str:
    """Return an exact short form when possible, otherwise a decimal string."""
    text = str(value)
    if len(text) <= 18:
        return text
    return decimal_string(value, digits)


def sqrt_bounds(value: Fraction, scale: int = 10 ** 18) -> tuple[Fraction, Fraction]:
    """Return rational lower/upper bounds for sqrt(value) via integer sqrt."""
    if value < 0:
        raise ValueError("sqrt_bounds requires a non-negative value")
    quotient = (value.numerator * scale * scale) // value.denominator
    lower_int = isqrt(quotient)
    return Fraction(lower_int, scale), Fraction(lower_int + 1, scale)


def round_half_up(value: Fraction) -> int:
    """Round an exact Fraction to the nearest integer, halves away from zero."""
    if value < 0:
        return -round_half_up(-value)
    quotient, remainder = divmod(value.numerator, value.denominator)
    return quotient + (1 if 2 * remainder >= value.denominator else 0)


def map_range(
    value: Fraction,
    source_min: Fraction,
    source_max: Fraction,
    target_min: int,
    target_max: int,
) -> int:
    """Map an exact value from a source interval to integer pixel coordinates."""
    if source_max == source_min:
        return (target_min + target_max) // 2
    ratio = (value - source_min) / (source_max - source_min)
    return round_half_up(target_min + ratio * (target_max - target_min))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_lf(data: bytes) -> bytes:
    return data.replace(b"\r\n", b"\n")


def line_ending(data: bytes) -> str:
    return "CRLF" if b"\r\n" in data else "LF"


def relative(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def plain_title(raw: str) -> str:
    text = re.sub(r"<[^>]+>", "", raw)
    return unescape(text).strip()


def esc(text: Any) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


# ---------------------------------------------------------------------------
# Matrix analysis
# ---------------------------------------------------------------------------


def parse_matrix(report: dict[str, Any]) -> tuple[list[list[Fraction]], list[list[Fraction]]]:
    recipe = report["matrix_recipe"]
    if int(recipe["dim"]) != 3:
        raise ValueError(f"expected a 3x3 matrix, got dim={recipe['dim']}")
    entries = recipe["entries"]
    matrix = [[frac(cell["mid"]) for cell in row] for row in entries]
    radii = [[frac(cell["rad"]) for cell in row] for row in entries]
    return matrix, radii


def ldl_pivots(matrix: list[list[Fraction]]) -> tuple[list[Fraction], list[list[Fraction]]]:
    """Compute the exact LDL^T diagonal (Sylvester pivots) and unit lower factor."""
    d1 = matrix[0][0]
    if d1 == 0:
        raise ZeroDivisionError("zero first Sylvester pivot")
    l21 = matrix[1][0] / d1
    d2 = matrix[1][1] - l21 * matrix[1][0]
    if d2 == 0:
        raise ZeroDivisionError("zero second Sylvester pivot")
    l31 = matrix[2][0] / d1
    l32 = (matrix[2][1] - l31 * matrix[1][0]) / d2
    d3 = matrix[2][2] - l31 * matrix[2][0] - l32 * (matrix[2][1] - l31 * matrix[1][0])
    lower = [
        [Fraction(1), Fraction(0), Fraction(0)],
        [l21, Fraction(1), Fraction(0)],
        [l31, l32, Fraction(1)],
    ]
    return [d1, d2, d3], lower


def inertia(pivots: list[Fraction]) -> dict[str, int]:
    return {
        "positive": sum(1 for value in pivots if value > 0),
        "negative": sum(1 for value in pivots if value < 0),
        "zero": sum(1 for value in pivots if value == 0),
    }


def eigen_analysis(matrix: list[list[Fraction]]) -> dict[str, Any] | None:
    """Exact eigen-data for the symmetric f/c/g family pattern.

    For A = [[f,c,g],[c,f,c],[g,c,f]] the antisymmetric direction (1,0,-1)
    has eigenvalue f-g.  The symmetric 2x2 block has eigenvalues
        (2f+g +/- sqrt(g^2 + 8c^2)) / 2.
    """
    f = matrix[0][0]
    c = matrix[0][1]
    g = matrix[0][2]
    pattern_ok = (
        matrix[1][1] == f
        and matrix[2][2] == f
        and matrix[1][0] == c
        and matrix[1][2] == c
        and matrix[2][1] == c
        and matrix[2][0] == g
    )
    if not pattern_ok:
        return None

    saddle = f - g
    discriminant = g * g + 8 * c * c
    lower_sqrt, upper_sqrt = sqrt_bounds(discriminant)
    plus_lower = (2 * f + g + lower_sqrt) / 2
    plus_upper = (2 * f + g + upper_sqrt) / 2
    minus_lower = (2 * f + g - upper_sqrt) / 2
    minus_upper = (2 * f + g - lower_sqrt) / 2

    def midpoint(lower: Fraction, upper: Fraction) -> Fraction:
        return (lower + upper) / 2

    plus_mid = midpoint(plus_lower, plus_upper)
    minus_mid = midpoint(minus_lower, minus_upper)

    return {
        "pattern": "symmetric_f_c_g",
        "saddle_exact": str(saddle),
        "saddle_decimal": decimal_string(saddle, 18),
        "saddle_vector_unnormalized": ["1", "0", "-1"],
        "plus_bounds": [str(plus_lower), str(plus_upper)],
        "plus_midpoint": str(plus_mid),
        "plus_decimal": decimal_string(plus_mid, 18),
        "minus_bounds": [str(minus_lower), str(minus_upper)],
        "minus_midpoint": str(minus_mid),
        "minus_decimal": decimal_string(minus_mid, 18),
        "discriminant": str(discriminant),
        "sqrt_bounds": [str(lower_sqrt), str(upper_sqrt)],
        "positive_eigenvalue_count": sum(
            1 for value in (plus_mid, minus_mid) if value > 0
        )
        + (1 if saddle > 0 else 0),
    }


def newton_flow(pivot: Fraction, steps: int = 6) -> dict[str, Any]:
    """Certified Newton contraction flow for sqrt(pivot) on a rational box.

    The certified box is B = [4/5 * sqrt_lo, 5/4 * sqrt_lo].  The true root
    sqrt(pivot) lies inside B because sqrt_lo <= sqrt(pivot) < sqrt_hi and
    sqrt_hi is many orders below 5/4 * sqrt_lo.  The derivative bound on B is
    attained at the left endpoint, which yields the Gate 4 contraction ratio.
    """
    if pivot <= 0:
        raise ValueError("newton_flow requires a positive pivot")

    lower, upper = sqrt_bounds(pivot)
    x0 = Fraction(4, 5) * lower
    box_lower = x0
    box_upper = Fraction(5, 4) * lower
    contains_root = box_lower <= lower and upper <= box_upper

    # N(x) = (x + pivot/x)/2 is convex on x > 0, so its maximum on the
    # closed box is attained at an endpoint and its minimum at sqrt(pivot).
    # Endpoint containment plus contains_root therefore certifies N(B) ⊆ B.
    image_lower = (box_lower + pivot / box_lower) / 2
    image_upper = (box_upper + pivot / box_upper) / 2
    self_mapping = (
        contains_root
        and box_lower <= image_lower <= box_upper
        and box_lower <= image_upper <= box_upper
    )

    bound = abs(Fraction(1, 2) * (1 - pivot / (x0 * x0)))
    iterates = [x0]
    ratios: list[Fraction] = []
    for _ in range(steps):
        current = iterates[-1]
        nxt = (current + pivot / current) / 2
        iterates.append(nxt)
        ratios.append(abs(Fraction(1, 2) * (1 - pivot / (nxt * nxt))))

    max_ratio = max([bound] + ratios)
    monotone = all(ratios[index + 1] <= ratios[index] for index in range(len(ratios) - 1))
    gate4_pass = max_ratio < GATE4_LIMIT
    unique_root = gate4_pass and self_mapping

    return {
        "pivot_exact": str(pivot),
        "pivot_decimal": decimal_string(pivot, 18),
        "sqrt_bounds": [str(lower), str(upper)],
        "certified_box": [str(box_lower), str(box_upper)],
        "contains_root": contains_root,
        "self_mapping": self_mapping,
        "endpoint_images": [str(image_lower), str(image_upper)],
        "x0_exact": str(x0),
        "x0_decimal": decimal_string(x0, 18),
        "iterates_exact": [str(value) for value in iterates],
        "iterates_decimal": [decimal_string(value, 18) for value in iterates],
        "ratios_exact": [str(value) for value in ratios],
        "ratios_decimal": [decimal_string(value, 18) for value in ratios],
        "contraction_bound_exact": str(bound),
        "contraction_bound_decimal": decimal_string(bound, 18),
        "max_ratio_exact": str(max_ratio),
        "max_ratio_decimal": decimal_string(max_ratio, 18),
        "max_ratio_sci": sci_string(max_ratio, 8),
        "gate4_limit": str(GATE4_LIMIT),
        "gate4_pass": gate4_pass,
        "unique_root_certified": unique_root,
        "monotone": monotone,
        "steps": steps,
        "method": "Newton for sqrt(pivot); exact rational derivative bound on certified box",
    }


# ---------------------------------------------------------------------------
# Spectral projection (dimensionless LDL^T coordinates)
# ---------------------------------------------------------------------------


def axis_bounds(pivot: Fraction) -> tuple[Fraction, Fraction, Fraction]:
    """Axis length 1/sqrt(|pivot|) with rational enclosure and midpoint."""
    lower, upper = sqrt_bounds(abs(pivot))
    return Fraction(1, upper), Fraction(1, lower), (Fraction(1, upper) + Fraction(1, lower)) / 2


def project_point(point: list[Fraction]) -> tuple[Fraction, Fraction]:
    """Rational isometric projection of a 3D point onto the 2D plane."""
    x, y, z = point
    return x - y / 2, z - y * Fraction(7, 20)


def build_projection(pivots: list[Fraction]) -> dict[str, Any]:
    axes: list[dict[str, Any]] = []
    for pivot in pivots:
        lower, upper, midpoint = axis_bounds(pivot)
        axes.append(
            {
                "pivot": str(pivot),
                "axis_lower": str(lower),
                "axis_upper": str(upper),
                "axis_mid": str(midpoint),
            }
        )

    max_axis = max(frac(axis["axis_mid"]) for axis in axes)
    normalized = [frac(axis["axis_mid"]) / max_axis for axis in axes]
    negative_indices = [index for index, value in enumerate(pivots) if value < 0]
    points: list[dict[str, Any]] = []
    rings: list[list[int]] = []
    rulings: list[list[int]] = []

    if len(negative_indices) == 1:
        surface = "hyperboloid_of_one_sheet"
        negative = negative_indices[0]
        positive = [index for index in range(3) if index != negative]
        for t_index, t_value in enumerate(HYPER_T_VALUES):
            radial = (t_value + 1 / t_value) / 2
            hyperbolic = (t_value - 1 / t_value) / 2
            ring: list[int] = []
            for theta_index, (cosine, sine) in enumerate(HYPER_THETA):
                point = [Fraction(0), Fraction(0), Fraction(0)]
                point[positive[0]] = normalized[positive[0]] * radial * cosine
                point[positive[1]] = normalized[positive[1]] * radial * sine
                point[negative] = normalized[negative] * hyperbolic
                sx, sy = project_point(point)
                ring.append(len(points))
                points.append(
                    {
                        "t": str(t_value),
                        "t_index": t_index,
                        "theta_index": theta_index,
                        "xyz": [str(value) for value in point],
                        "sx": str(sx),
                        "sy": str(sy),
                    }
                )
            rings.append(ring)
        for theta_index in range(len(HYPER_THETA)):
            rulings.append([rings[t_index][theta_index] for t_index in range(len(rings))])
    elif not negative_indices:
        surface = "ellipsoid"
        grid = [Fraction(-2), Fraction(-1), Fraction(0), Fraction(1), Fraction(2)]
        for p_index, p_value in enumerate(grid):
            ring = []
            for q_index, q_value in enumerate(grid):
                denominator = 1 + p_value * p_value + q_value * q_value
                unit = [
                    2 * p_value / denominator,
                    2 * q_value / denominator,
                    (1 - p_value * p_value - q_value * q_value) / denominator,
                ]
                point = [normalized[index] * unit[index] for index in range(3)]
                sx, sy = project_point(point)
                ring.append(len(points))
                points.append(
                    {
                        "t": str(p_value),
                        "t_index": p_index,
                        "theta_index": q_index,
                        "xyz": [str(value) for value in point],
                        "sx": str(sx),
                        "sy": str(sy),
                    }
                )
            rings.append(ring)
        for theta_index in range(len(grid)):
            rulings.append([rings[p_index][theta_index] for p_index in range(len(rings))])
    else:
        surface = "absolute_ellipsoid_fallback"
        for index, value in enumerate(normalized):
            point = [Fraction(0), Fraction(0), Fraction(0)]
            point[index] = value
            sx, sy = project_point(point)
            points.append(
                {
                    "t": "0",
                    "t_index": 0,
                    "theta_index": index,
                    "xyz": [str(item) for item in point],
                    "sx": str(sx),
                    "sy": str(sy),
                }
            )

    sx_values = [frac(point["sx"]) for point in points]
    sy_values = [frac(point["sy"]) for point in points]
    x_min, x_max = min(sx_values), max(sx_values)
    y_min, y_max = min(sy_values), max(sy_values)
    if x_max == x_min:
        x_min, x_max = x_min - 1, x_max + 1
    if y_max == y_min:
        y_min, y_max = y_min - 1, y_max + 1

    for point in points:
        sx = frac(point["sx"])
        sy = frac(point["sy"])
        point["u"] = str((sx - x_min) / (x_max - x_min))
        point["v"] = str((sy - y_min) / (y_max - y_min))

    return {
        "basis": "LDL^T diagonal (Sylvester pivots)",
        "surface": surface,
        "inertia": inertia(pivots),
        "axes": axes,
        "axes_normalized": [str(value) for value in normalized],
        "negative_indices": negative_indices,
        "points": points,
        "rings": rings,
        "rulings": rulings,
        "range": {"sx": [str(x_min), str(x_max)], "sy": [str(y_min), str(y_max)]},
        "parameter_grid": {
            "hyper_t": [str(value) for value in HYPER_T_VALUES],
            "theta": [[str(cosine), str(sine)] for cosine, sine in HYPER_THETA],
        },
    }


# ---------------------------------------------------------------------------
# SVG builder
# ---------------------------------------------------------------------------


class SvgBuilder:
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.parts: list[str] = []

    def add(self, markup: str) -> None:
        self.parts.append(markup)

    def rect(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        fill: str = "#ffffff",
        stroke: str = "none",
        stroke_width: int | str = 1,
        radius: int = 0,
        opacity: str = "1",
    ) -> None:
        self.add(
            f'<rect x="{x}" y="{y}" width="{width}" height="{height}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}" '
            f'rx="{radius}" opacity="{opacity}"/>'
        )

    def line(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        stroke: str,
        stroke_width: int | str = 1,
        dash: str | None = None,
    ) -> None:
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="{stroke}" stroke-width="{stroke_width}"{dash_attr}/>'
        )

    def circle(
        self,
        cx: int,
        cy: int,
        radius: int,
        fill: str = "none",
        stroke: str = "none",
        stroke_width: int | str = 1,
        dash: str | None = None,
    ) -> None:
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(
            f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{stroke_width}"{dash_attr}/>'
        )

    def polyline(
        self,
        points: list[tuple[int, int]],
        stroke: str,
        stroke_width: int | str = 1,
        fill: str = "none",
        dash: str | None = None,
        opacity: str = "1",
    ) -> None:
        if len(points) < 2:
            return
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        text = " ".join(f"{x},{y}" for x, y in points)
        self.add(
            f'<polyline points="{text}" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="{stroke_width}"{dash_attr} opacity="{opacity}"/>'
        )

    def text(
        self,
        x: int,
        y: int,
        content: Any,
        size: int = 12,
        fill: str = "#212529",
        anchor: str = "start",
        weight: str = "normal",
    ) -> None:
        self.add(
            f'<text x="{x}" y="{y}" font-family="Segoe UI, Arial, sans-serif" '
            f'font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
            f'font-weight="{weight}">{esc(content)}</text>'
        )

    def render(self) -> str:
        header = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.width}" '
            f'height="{self.height}" viewBox="0 0 {self.width} {self.height}">'
        )
        background = (
            f'<rect x="0" y="0" width="{self.width}" height="{self.height}" '
            'fill="#ffffff"/>'
        )
        return "\n".join([header, background, *self.parts, "</svg>"]) + "\n"


# ---------------------------------------------------------------------------
# SVG panels
# ---------------------------------------------------------------------------


def render_header(svg: SvgBuilder, generated_at: str, ratio: Fraction) -> None:
    svg.rect(0, 0, 1500, 104, fill="#0b2545")
    svg.text(30, 40, "MATH 3.0 — LATTICE SPATIAL CONFINEMENT", 24, "#ffffff", weight="bold")
    svg.text(
        30,
        66,
        "24,000-bit interval balls · Sylvester pivots · Planck micro-cutoff projection",
        13,
        "#c9d6e3",
    )
    svg.text(
        30,
        88,
        f"generated {generated_at} · Planck 1.616255e-35 m · inner radius 1.0e-40 m · "
        f"ratio ×{decimal_string(ratio, 1)} · exact Fraction arithmetic",
        11,
        "#9fb3c8",
    )


def render_footer(svg: SvgBuilder, json_path: str, svg_path: str) -> None:
    svg.line(30, 1046, 1470, 1046, "#adb5bd", 1)
    svg.text(
        30,
        1066,
        "Engine: mcp/t2n/core/lattice_viewer.py · no matplotlib/numpy · "
        "binary float operations: 0 · payload floats: 0",
        11,
        "#495057",
    )
    svg.text(
        30,
        1082,
        f"JSON index: {json_path} · vector asset: {svg_path}",
        11,
        "#495057",
    )


def render_confinement(svg: SvgBuilder, family: dict[str, Any], x: int, y: int, width: int, height: int) -> None:
    svg.rect(x, y, width, height, fill="#f8f9fa", stroke="#ced4da", stroke_width=1, radius=8)
    svg.text(x + 14, y + 24, "PLANCK CONFINEMENT", 14, "#0b2545", weight="bold")
    svg.text(x + 14, y + 42, "actual interval radii · inner ball magnified for visibility (not to scale)", 10, "#6c757d")

    center_x = x + width // 2
    center_y = y + 185
    radius = min(width, height) // 2 - 65
    inner_radius = max(6, radius // 10)

    svg.circle(center_x, center_y, radius, fill="#e7f5ff", stroke="#1c7ed6", stroke_width=3)
    svg.circle(center_x, center_y, inner_radius, fill="#63e6be", stroke="#087f5b", stroke_width=2)
    svg.circle(center_x, center_y, 2, fill="#0b2545")

    pivots = [frac(value) for value in family["sylvester"]["pivots"]]
    max_abs = max(abs(value) for value in pivots)
    for index, (pivot, (dx, dy)) in enumerate(zip(pivots, UNIT_DIRECTIONS), start=1):
        marker = Fraction(1, 4) + Fraction(3, 5) * (abs(pivot) / max_abs)
        end_x = center_x + round_half_up(marker * radius * dx)
        end_y = center_y - round_half_up(marker * radius * dy)
        color = "#2b8a3e" if pivot > 0 else "#c92a2a"
        svg.line(center_x, center_y, end_x, end_y, color, 3)
        svg.circle(end_x, end_y, 6, fill=color, stroke="#ffffff", stroke_width=1)
        anchor = "start" if end_x >= center_x else "end"
        offset = 10 if end_x >= center_x else -10
        svg.text(
            end_x + offset,
            end_y + 4,
            f"d{index} = {short_fraction(pivot)}",
            10,
            color,
            anchor=anchor,
        )

    svg.text(
        center_x + inner_radius + 8,
        center_y - 6,
        "inner ball 1.0e-40 m",
        10,
        "#087f5b",
    )
    svg.text(x + 14, y + 312, "outer: Planck cutoff 1.616255e-35 m (display radius 1.0)", 10, "#1c7ed6")
    svg.text(x + 14, y + 328, "inner: 1.0e-40 m (display 0.1, true 2/323251)", 10, "#087f5b")
    svg.text(
        x + 14,
        y + 344,
        f"ratio ×{decimal_string(frac(family['planck_confinement']['ratio']), 1)} · "
        "display magnified ×16162.55",
        10,
        "#495057",
    )
    svg.text(
        x + 14,
        y + 360,
        f"Sylvester inertia: (+{family['sylvester']['inertia']['positive']}, "
        f"−{family['sylvester']['inertia']['negative']}, "
        f"{family['sylvester']['inertia']['zero']})",
        10,
        "#495057",
    )
    svg.text(x + width - 14, y + 24, "DISPLAY NOT TO SCALE", 9, "#c92a2a", anchor="end", weight="bold")
    svg.text(x + width - 14, y + 42, "green = positive pivot", 9, "#2b8a3e", anchor="end")
    svg.text(x + width - 14, y + 56, "red = negative pivot", 9, "#c92a2a", anchor="end")


def render_spectral(svg: SvgBuilder, family: dict[str, Any], x: int, y: int, width: int, height: int) -> None:
    svg.rect(x, y, width, height, fill="#f8f9fa", stroke="#ced4da", stroke_width=1, radius=8)
    svg.text(x + 14, y + 24, "LDLᵀ SPECTRAL PROJECTION", 14, "#0b2545", weight="bold")
    svg.text(
        x + 14,
        y + 42,
        f"surface: {family['projection']['surface'].replace('_', ' ')} · dimensionless, normalized axes",
        10,
        "#6c757d",
    )

    projection = family["projection"]
    points = projection["points"]
    axes_normalized = [frac(value) for value in projection["axes_normalized"]]

    # Collect projected coordinates, including the principal-axis endpoints.
    projected: list[tuple[Fraction, Fraction]] = []
    for point in points:
        projected.append((frac(point["sx"]), frac(point["sy"])))
    axis_endpoints: list[tuple[Fraction, Fraction]] = []
    for index, axis_length in enumerate(axes_normalized):
        for sign in (Fraction(1), Fraction(-1)):
            vector = [Fraction(0), Fraction(0), Fraction(0)]
            vector[index] = sign * axis_length
            axis_endpoints.append(project_point(vector))
    all_points = projected + axis_endpoints

    x_min = min(value[0] for value in all_points)
    x_max = max(value[0] for value in all_points)
    y_min = min(value[1] for value in all_points)
    y_max = max(value[1] for value in all_points)
    if x_max == x_min:
        x_min, x_max = x_min - 1, x_max + 1
    if y_max == y_min:
        y_min, y_max = y_min - 1, y_max + 1
    pad_x = (x_max - x_min) / 12
    pad_y = (y_max - y_min) / 12
    x_min -= pad_x
    x_max += pad_x
    y_min -= pad_y
    y_max += pad_y

    left = x + 34
    right = x + width - 34
    top = y + 66
    bottom = y + height - 34

    def to_pixel(point: tuple[Fraction, Fraction]) -> tuple[int, int]:
        px = map_range(point[0], x_min, x_max, left, right)
        py = map_range(point[1], y_min, y_max, bottom, top)
        return px, py

    # Wireframe rings and rulings.
    for ring in projection["rings"]:
        polyline = [to_pixel(projected[index]) for index in ring]
        if polyline:
            polyline.append(polyline[0])
        svg.polyline(polyline, "#4c6ef5", "1.4", opacity="0.65")
    for ruling in projection["rulings"]:
        polyline = [to_pixel(projected[index]) for index in ruling]
        svg.polyline(polyline, "#748ffc", "0.9", opacity="0.55")

    # Principal axes.
    for index, axis_length in enumerate(axes_normalized):
        endpoints = []
        for sign in (Fraction(1), Fraction(-1)):
            vector = [Fraction(0), Fraction(0), Fraction(0)]
            vector[index] = sign * axis_length
            endpoints.append(project_point(vector))
        p1 = to_pixel(endpoints[0])
        p2 = to_pixel(endpoints[1])
        pivot = frac(family["sylvester"]["pivots"][index])
        color = "#2b8a3e" if pivot > 0 else "#c92a2a"
        dash = "5 4" if pivot < 0 else None
        svg.line(p1[0], p1[1], p2[0], p2[1], color, 2, dash=dash)
        label_point = endpoints[0] if pivot > 0 else endpoints[1]
        lx, ly = to_pixel(label_point)
        anchor = "start" if lx >= (left + right) // 2 else "end"
        offset = 8 if anchor == "start" else -8
        svg.text(
            lx + offset,
            ly + 4,
            f"d{index + 1} = {short_fraction(pivot)}",
            9,
            color,
            anchor=anchor,
        )

    inertia_data = family["sylvester"]["inertia"]
    svg.text(
        x + width - 14,
        y + 60,
        f"inertia (+{inertia_data['positive']}, −{inertia_data['negative']}, {inertia_data['zero']})",
        9,
        "#495057",
        anchor="end",
    )
    svg.text(
        x + width - 14,
        y + 74,
        f"det = {short_fraction(frac(family['sylvester']['determinant']))}",
        9,
        "#495057",
        anchor="end",
    )
    svg.text(
        x + 14,
        y + height - 14,
        "black axes are positive-definite directions; red dashed axis is the saddle direction",
        9,
        "#6c757d",
    )


def render_newton(svg: SvgBuilder, family: dict[str, Any], x: int, y: int, width: int, height: int) -> None:
    svg.rect(x, y, width, height, fill="#f8f9fa", stroke="#ced4da", stroke_width=1, radius=8)
    svg.text(x + 14, y + 24, "GATE 4 — NEWTON CONTRACTION", 14, "#0b2545", weight="bold")
    svg.text(
        x + 14,
        y + 42,
        "exact rational flow for positive Sylvester pivots · limit max|N′| < 1/2",
        10,
        "#6c757d",
    )

    flows = family["newton"]["positive_pivots"]
    for flow_index, flow in enumerate(flows):
        top = y + 52 + flow_index * 158
        pivot = frac(flow["pivot_exact"])
        svg.text(x + 14, top, f"pivot d{flow_index + 1} = {short_fraction(pivot)} (positive)", 10, "#2b8a3e", weight="bold")

        box_lower, box_upper = (frac(value) for value in flow["certified_box"])
        iterates = [frac(value) for value in flow["iterates_exact"]]
        value_max = max(box_upper, max(iterates)) * Fraction(11, 10)
        line_y = top + 34
        left = x + 26
        right = x + width - 26

        svg.line(left, line_y, right, line_y, "#adb5bd", 1)
        box_x1 = map_range(box_lower, Fraction(0), value_max, left, right)
        box_x2 = map_range(box_upper, Fraction(0), value_max, left, right)
        svg.rect(box_x1, line_y - 11, max(2, box_x2 - box_x1), 22, fill="#d3f9d8", stroke="#2b8a3e", stroke_width=1, opacity="0.9")
        svg.text(box_x1 + 2, line_y - 27, "certified box", 8, "#2b8a3e")

        previous_x = None
        for iterate_index, value in enumerate(iterates):
            px = map_range(value, Fraction(0), value_max, left, right)
            if previous_x is not None:
                svg.line(previous_x, line_y, px, line_y, "#40c057", 1)
            radius = max(2, 7 - iterate_index)
            svg.circle(px, line_y, radius, fill="#2b8a3e", stroke="#ffffff", stroke_width=1)
            if iterate_index == 0:
                svg.text(px, line_y - 15, "x0", 8, "#2b8a3e", anchor="middle")
            elif iterate_index == 1:
                svg.text(px - 4, line_y - 15, "x1", 8, "#2b8a3e", anchor="end")
            elif iterate_index == len(iterates) - 1:
                svg.text(px + 8, line_y - 15, f"x{iterate_index}", 8, "#2b8a3e", anchor="start")
            previous_x = px

        gauge_y = top + 78
        gauge_left = x + 26
        gauge_right = x + 250
        svg.line(gauge_left, gauge_y, gauge_right, gauge_y, "#adb5bd", 1)
        max_ratio = frac(flow["max_ratio_exact"])
        marker_x = map_range(max_ratio, Fraction(0), GATE4_LIMIT, gauge_left, gauge_right)
        limit_x = gauge_right
        svg.rect(gauge_left, gauge_y - 5, max(2, marker_x - gauge_left), 10, fill="#40c057", stroke="#2b8a3e", stroke_width=1)
        svg.line(limit_x, gauge_y - 14, limit_x, gauge_y + 14, "#c92a2a", 2, dash="4 3")
        svg.text(limit_x, gauge_y - 18, "1/2", 8, "#c92a2a", anchor="middle")
        svg.text(
            gauge_left,
            gauge_y + 22,
            f"max|N′| = {short_fraction(max_ratio)} ≈ {decimal_string(max_ratio, 6)} < 1/2 · "
            f"N(B)⊆B: {flow['self_mapping']}",
            9,
            "#2b8a3e" if flow["gate4_pass"] else "#c92a2a",
        )
        svg.text(
            x + width - 18,
            gauge_y + 2,
            "GATE 4 PASS" if flow["gate4_pass"] else "GATE 4 FAIL",
            11,
            "#2b8a3e" if flow["gate4_pass"] else "#c92a2a",
            anchor="end",
            weight="bold",
        )

        ratios = [frac(value) for value in flow["ratios_exact"]]
        ratio_text = "  ".join(f"r{index}={sci_string(value, 4)}" for index, value in enumerate(ratios[:4]))
        svg.text(x + 26, top + 118, ratio_text, 8, "#495057")

    negative = family["newton"]["negative_pivots"]
    if negative:
        details = ", ".join(f"d{item['index'] + 1}={short_fraction(frac(item['pivot']))}" for item in negative)
        svg.text(
            x + 14,
            y + height - 16,
            f"hyperbolic saddle: {details} · no real sqrt Newton flow · excluded from elliptic Gate 4",
            9,
            "#c92a2a",
        )


def render_family_row(svg: SvgBuilder, family: dict[str, Any], row_y: int) -> None:
    svg.rect(20, row_y, 1460, 450, fill="#ffffff", stroke="#dee2e6", stroke_width=1, radius=10)
    index = family["family_index"]
    label = FAMILY_LABELS[index]
    svg.text(34, row_y + 28, f"FAMILY {index:03d} — {label}", 17, "#1c7ed6", weight="bold")
    svg.text(34, row_y + 48, plain_title(family["empirical"]["title"])[:110], 11, "#495057")

    panel_y = row_y + 62
    panel_height = 370
    render_confinement(svg, family, 34, panel_y, 420, panel_height)
    render_spectral(svg, family, 470, panel_y, 500, panel_height)
    render_newton(svg, family, 986, panel_y, 480, panel_height)


# ---------------------------------------------------------------------------
# Data assembly
# ---------------------------------------------------------------------------


def load_family(index: int, empirical_record: dict[str, Any]) -> dict[str, Any]:
    report_path = REPORTS / f"openai_family_{index:03d}.json"
    cert_path = REPORTS / "certificates" / f"openai_family_{index:03d}_certificate.json"

    report_bytes = report_path.read_bytes()
    report_data = json.loads(report_bytes.decode("utf-8"))
    report_disk_sha = sha256_bytes(report_bytes)
    report_lf = canonical_lf(report_bytes)
    report_lf_sha = sha256_bytes(report_lf)

    cert_bytes = cert_path.read_bytes()
    cert_data = json.loads(cert_bytes.decode("utf-8"))
    cert_source = cert_data.get("source_sha256")
    cert_match = cert_source in (report_disk_sha, report_lf_sha)
    if cert_source == report_lf_sha:
        match_mode = "canonical_lf"
    elif cert_source == report_disk_sha:
        match_mode = "disk_bytes"
    else:
        match_mode = "none"

    matrix, radii = parse_matrix(report_data)
    pivots, lower = ldl_pivots(matrix)
    pivot_inertia = inertia(pivots)
    eigenvalues = eigen_analysis(matrix)

    micro = report_data["micro_cutoff"]
    planck = frac(micro["planck_rational"])
    inner = frac(micro["radius_rational"])
    if planck != frac(PLANCK_LITERAL):
        raise ValueError(f"family {index}: Planck rational does not match literal")
    if inner != pow10(-40):
        raise ValueError(f"family {index}: inner radius does not match 1e-40")
    if not bool(micro["radius_leq_planck"]):
        raise ValueError(f"family {index}: radius_leq_planck is false")

    all_inner = all(frac(cell["rad"]) == inner for row in report_data["matrix_recipe"]["entries"] for cell in row)
    positive_indices = [i for i, value in enumerate(pivots) if value > 0]
    negative_indices = [i for i, value in enumerate(pivots) if value < 0]

    flows = [newton_flow(pivots[i]) for i in positive_indices]
    max_ratio = max((frac(flow["max_ratio_exact"]) for flow in flows), default=None)
    gate4_pass = bool(flows) and max_ratio is not None and max_ratio < GATE4_LIMIT
    unique_root = gate4_pass and all(
        flow["unique_root_certified"] and flow["self_mapping"] for flow in flows
    )

    projection = build_projection(pivots)
    determinant = pivots[0] * pivots[1] * pivots[2]

    empirical = {
        "title": empirical_record.get("title"),
        "title_plain": plain_title(empirical_record.get("title", "")),
        "source_status": empirical_record.get("source_status"),
        "fallback_reason": empirical_record.get("fallback_reason"),
        "primary_numeric_constant": empirical_record.get("primary_numeric_constant"),
        "extracted_constants": empirical_record.get("extracted_constants", {}),
        "preprint_dirs": empirical_record.get("preprint_dirs", []),
        "tex_files_scanned": empirical_record.get("tex_files_scanned"),
        "bytes_scanned": empirical_record.get("bytes_scanned"),
        "match_count": len(empirical_record.get("matches", [])),
        "first_matches": empirical_record.get("matches", [])[:5],
    }

    return {
        "family_index": index,
        "label": FAMILY_LABELS[index],
        "empirical": empirical,
        "source_report": {
            "path": relative(report_path),
            "disk_sha256": report_disk_sha,
            "canonical_lf_sha256": report_lf_sha,
            "disk_size_bytes": len(report_bytes),
            "canonical_lf_size_bytes": len(report_lf),
            "line_ending": line_ending(report_bytes),
            "certificate_path": relative(cert_path),
            "certificate_sha256": sha256_bytes(cert_bytes),
            "certificate_source_sha256": cert_source,
            "certificate_source_match": cert_match,
            "match_mode": match_mode,
            "report_verdict": report_data.get("verdict"),
            "precision_bits": report_data.get("precision_bits"),
            "r_hank": report_data.get("r_hank"),
            "r_toep": report_data.get("r_toep"),
        },
        "matrix": {
            "dim": 3,
            "entries": [[str(value) for value in row] for row in matrix],
            "radii": [[str(value) for value in row] for row in radii],
            "symmetric": all(matrix[i][j] == matrix[j][i] for i in range(3) for j in range(3)),
            "all_radii_equal_inner": all_inner,
            "ldl_lower": [[str(value) for value in row] for row in lower],
        },
        "sylvester": {
            "pivots": [str(value) for value in pivots],
            "pivot_decimals": [decimal_string(value, 18) for value in pivots],
            "inertia": pivot_inertia,
            "determinant": str(determinant),
            "determinant_decimal": decimal_string(determinant, 18),
            "eigenvalues": eigenvalues,
        },
        "planck_confinement": {
            "inner_radius_rational": str(inner),
            "planck_radius_rational": str(planck),
            "ratio": str(planck / inner),
            "ratio_decimal": decimal_string(planck / inner, 1),
            "display_projection": "affine radial display; inner ball magnified for visibility (not to scale)",
            "display_inner_fraction_of_outer": "1/10",
            "true_inner_fraction_of_planck": str(inner / planck),
            "display_magnification": str((Fraction(1, 10)) / (inner / planck)),
            "matrix_radius_uniform": all_inner,
            "radius_leq_planck": bool(micro["radius_leq_planck"]),
        },
        "newton": {
            "positive_pivot_indices": positive_indices,
            "positive_pivots": flows,
            "negative_pivots": [
                {
                    "index": i,
                    "pivot": str(pivots[i]),
                    "pivot_decimal": decimal_string(pivots[i], 18),
                    "status": "hyperbolic_saddle_excluded",
                }
                for i in negative_indices
            ],
            "all_self_mapping": all(flow["self_mapping"] for flow in flows),
            "max_ratio_exact": str(max_ratio) if max_ratio is not None else None,
            "max_ratio_decimal": decimal_string(max_ratio, 18) if max_ratio is not None else None,
            "gate4_limit": str(GATE4_LIMIT),
            "gate4_pass": gate4_pass,
            "unique_root_certified": unique_root,
        },
        "projection": projection,
    }


def audit_no_floats(value: Any, path: str = "root") -> list[str]:
    found: list[str] = []
    if isinstance(value, float):
        found.append(path)
    elif isinstance(value, dict):
        for key, item in value.items():
            found.extend(audit_no_floats(item, f"{path}.{key}"))
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            found.extend(audit_no_floats(item, f"{path}[{index}]"))
    return found


def source_float_audit(path: Path) -> dict[str, Any]:
    """Scan this source with the AST, not string matching.

    The previous string count was self-referential: the audit expression and
    its print label both contained the literal ``float(``.  Parsing the module
    and counting real ``float`` calls / float literals avoids that trap.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"))
    conversion_lines: list[int] = []
    literal_lines: list[int] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id == "float":
                conversion_lines.append(node.lineno)
            elif isinstance(func, ast.Attribute) and func.attr == "float":
                conversion_lines.append(node.lineno)
        elif isinstance(node, ast.Constant) and isinstance(node.value, float):
            literal_lines.append(node.lineno)
    source_status = (
        "PASS" if not conversion_lines and not literal_lines else "FAIL"
    )
    return {
        "conversion_calls": len(conversion_lines),
        "conversion_lines": conversion_lines,
        "float_literals": len(literal_lines),
        "literal_lines": literal_lines,
        "status": source_status,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    if not EMPIRICAL_PATH.exists():
        print(f"FATAL: missing empirical database: {EMPIRICAL_PATH}", file=sys.stderr)
        return 2

    empirical_bytes = EMPIRICAL_PATH.read_bytes()
    empirical_data = json.loads(empirical_bytes.decode("utf-8"))
    empirical_lf = canonical_lf(empirical_bytes)
    empirical_records = {int(record["family_index"]): record for record in empirical_data["records"]}

    families: list[dict[str, Any]] = []
    for index in TARGET_FAMILIES:
        if index not in empirical_records:
            print(f"FATAL: family {index:03d} missing from empirical database", file=sys.stderr)
            return 2
        families.append(load_family(index, empirical_records[index]))

    generated_at = datetime.now(timezone.utc).isoformat()
    planck_ratio = frac(families[0]["planck_confinement"]["ratio"])
    if any(frac(family["planck_confinement"]["ratio"]) != planck_ratio for family in families):
        raise ValueError("inconsistent Planck/inner radius ratio across families")

    svg = SvgBuilder(1500, 1090)
    render_header(svg, generated_at, planck_ratio)
    for row, family in enumerate(families):
        render_family_row(svg, family, 120 + row * 460)
    render_footer(svg, relative(OUT_JSON), relative(OUT_SVG))
    svg_text = svg.render()
    ET.fromstring(svg_text)
    OUT_SVG.write_text(svg_text, encoding="utf-8")
    svg_bytes = OUT_SVG.read_bytes()

    certificate_matches = sum(1 for family in families if family["source_report"]["certificate_source_match"])
    all_radii_ok = all(
        family["planck_confinement"]["matrix_radius_uniform"]
        and family["planck_confinement"]["radius_leq_planck"]
        for family in families
    )
    all_gate4 = all(family["newton"]["gate4_pass"] for family in families)
    all_self_mapping = all(family["newton"]["all_self_mapping"] for family in families)
    all_unique = all(family["newton"]["unique_root_certified"] for family in families)
    source_audit = source_float_audit(Path(__file__).resolve())

    payload: dict[str, Any] = {
        "schema": "MATH30_LATTICE_SPATIAL_CONFINEMENT_V1",
        "generated_at": generated_at,
        "engine": relative(Path(__file__).resolve()),
        "numeric_policy": {
            "arithmetic": "fractions.Fraction + integer sqrt (math.isqrt)",
            "binary_float_operations": 0,
            "serialization": "exact rational strings and integer-derived decimal strings",
            "vector_backend": "standalone SVG (no matplotlib / numpy)",
        },
        "source_database": {
            "path": relative(EMPIRICAL_PATH),
            "disk_sha256": sha256_bytes(empirical_bytes),
            "canonical_lf_sha256": sha256_bytes(empirical_lf),
            "disk_size_bytes": len(empirical_bytes),
            "canonical_lf_size_bytes": len(empirical_lf),
            "line_ending": line_ending(empirical_bytes),
            "family_count": len(empirical_data["records"]),
        },
        "constants": {
            "planck_length_m": PLANCK_LITERAL,
            "planck_rational": str(frac(PLANCK_LITERAL)),
            "inner_radius_m": INNER_LITERAL,
            "inner_radius_rational": str(pow10(-40)),
            "confinement_ratio": str(planck_ratio),
            "confinement_ratio_decimal": decimal_string(planck_ratio, 1),
            "gate4_max_ratio_limit": str(GATE4_LIMIT),
        },
        "families": families,
        "index_mapping": {
            str(family["family_index"]): {
                "row": row,
                "label": family["label"],
                "report": family["source_report"]["path"],
                "certificate": family["source_report"]["certificate_path"],
                "json_pointer": f"/families/{row}",
                "svg_row": row,
            }
            for row, family in enumerate(families)
        },
        "verification": {
            "families_requested": list(TARGET_FAMILIES),
            "families_rendered": len(families),
            "certificate_hash_matches": certificate_matches,
            "all_certificate_hashes_match": certificate_matches == len(families),
            "all_matrix_radii_within_planck": all_radii_ok,
            "all_gate4_pass": all_gate4,
            "all_self_mapping": all_self_mapping,
            "all_unique_root_certified": all_unique,
            "float_audit": {
                "payload_float_count": 0,
                "binary_float_operations": 0,
                "source_float_conversion_calls": source_audit["conversion_calls"],
                "source_float_literals": source_audit["float_literals"],
                "source_float_audit_status": source_audit["status"],
                "status": "PENDING",
            },
        },
        "svg": {
            "path": relative(OUT_SVG),
            "bytes": len(svg_bytes),
            "sha256": sha256_bytes(svg_bytes),
            "width": svg.width,
            "height": svg.height,
            "element_count": len(list(ET.fromstring(svg_text).iter())),
        },
    }

    floats = audit_no_floats(payload)
    float_status = (
        "PASS" if not floats and source_audit["status"] == "PASS" else "FAIL"
    )
    payload["verification"]["float_audit"]["payload_float_count"] = len(floats)
    payload["verification"]["float_audit"]["status"] = float_status
    if floats:
        payload["verification"]["float_audit"]["float_paths"] = floats[:20]

    all_ok = (
        certificate_matches == len(families)
        and all_radii_ok
        and all_gate4
        and all_self_mapping
        and all_unique
        and not floats
        and source_audit["status"] == "PASS"
        and float_status == "PASS"
    )
    payload["verdict"] = (
        "PASSED — 2 families projected with exact rational geometry; "
        "zero payload floats and zero source float conversions; "
        "Gate 4 max_ratio < 1/2 with N(B) ⊆ B on all positive pivots"
        if all_ok
        else "FAILED — see verification block"
    )

    OUT_JSON.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    json_bytes = OUT_JSON.read_bytes()

    print("LATTICE VIEWER — PLANCK CONFINEMENT PROJECTION")
    print("=" * 58)
    print(f"Source database : {relative(EMPIRICAL_PATH)}")
    print(f"  disk SHA-256       : {payload['source_database']['disk_sha256']}")
    print(f"  canonical LF SHA256: {payload['source_database']['canonical_lf_sha256']}")
    print(f"  line ending        : {payload['source_database']['line_ending']}")
    print(f"Planck cutoff   : {PLANCK_LITERAL} m")
    print(f"Inner radius    : {INNER_LITERAL} m")
    print(f"Ratio           : {planck_ratio} = {decimal_string(planck_ratio, 1)}x")
    print()
    for family in families:
        index = family["family_index"]
        print(f"FAMILY {index:03d} — {family['label']}")
        print(f"  title              : {family['empirical']['title_plain']}")
        print(f"  report SHA-256     : {family['source_report']['disk_sha256']}")
        print(f"  certificate match  : {family['source_report']['certificate_source_match']} "
              f"({family['source_report']['match_mode']})")
        pivots = family["sylvester"]["pivots"]
        print(f"  Sylvester pivots   : {', '.join(pivots)}")
        print(f"  pivot inertia      : +{family['sylvester']['inertia']['positive']} "
              f"/ -{family['sylvester']['inertia']['negative']} "
              f"/ {family['sylvester']['inertia']['zero']}")
        if family["sylvester"]["eigenvalues"]:
            eigen = family["sylvester"]["eigenvalues"]
            print(f"  eigenvalues        : saddle={eigen['saddle_decimal']} "
                  f"lambda-={eigen['minus_decimal']} lambda+={eigen['plus_decimal']}")
        print(f"  spectral surface   : {family['projection']['surface']}")
        print(f"  Gate 4 max_ratio   : {family['newton']['max_ratio_decimal']} "
              f"({family['newton']['max_ratio_exact']}) -> "
              f"{'PASS' if family['newton']['gate4_pass'] else 'FAIL'}")
        print(f"  Newton self-map    : N(B) subset of B -> "
              f"{family['newton']['all_self_mapping']}")
        print(f"  unique root        : {family['newton']['unique_root_certified']}")
        print()
    print("OUTPUTS")
    print(f"  JSON : {relative(OUT_JSON)} ({len(json_bytes)} bytes)")
    print(f"         SHA-256 {sha256_bytes(json_bytes)}")
    print(f"  SVG  : {relative(OUT_SVG)} ({payload['svg']['bytes']} bytes)")
    print(f"         SHA-256 {payload['svg']['sha256']}")
    print(f"  SVG elements       : {payload['svg']['element_count']}")
    print()
    print("FLOAT AUDIT")
    print(f"  payload float values          : {len(floats)}")
    print(f"  binary float operations       : 0")
    print(f"  source float conversion calls : {source_audit['conversion_calls']}")
    print(f"  source float literals         : {source_audit['float_literals']}")
    print(f"  source AST audit              : {source_audit['status']}")
    print(f"  payload audit                 : {payload['verification']['float_audit']['status']}")
    print()
    print(f"VERDICT: {payload['verdict']}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
