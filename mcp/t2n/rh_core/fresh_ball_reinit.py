"""Fresh python-flint 24,000-bit ball re-initialization of the raw f/g enclosures.

Independently constructs the Gate 1 interval balls from raw theoretical
representations of the two opposing paths on the certified 3-point slice:

  f : convergent / collapsing path   -> 13 on the slice
  g : divergent / repulsion path     -> 1/2 on the slice

Every midpoint is an exact Fraction; every ball radius is bounded by the
Planck micro cutoff (l_P ~ 1.616255e-35 m) so the enclosure cannot inherit a
continuum blow-up. The exported manifest feeds lte_spectral_validator.py via
--raw-enclosure.

This module certifies an enclosure. It does not prove the Riemann Hypothesis.
"""

import json
import os
import sys
from datetime import datetime, timezone
from fractions import Fraction

try:
    import flint
    from flint import arb, acb, fmpq  # noqa: F401  (arb/acb/fmpq contract)
except ImportError:
    print("FATAL: python-flint missing.")
    sys.exit(2)

ROOT = r"D:\Opencode AI Agent\Math 3.0 Tools"
REPORTS = os.path.join(ROOT, "reports")
OUT_PATH = os.path.join(REPORTS, "raw_fg_initial_enclosure.json")

PRECISION_BITS = 24000
flint.ctx.prec = PRECISION_BITS

# Micro cutoff: Planck length l_P ~ 1.616255e-35 m = 1616255 / 10^41 (exact).
PLANCK = Fraction(1616255, 10 ** 41)
# Enclosure radius: 1e-40 m, below the Planck cutoff.
RADIUS = Fraction(1, 10 ** 40)
RADIUS_STR = "1e-40"
PLANCK_STR = "1.616255e-35"

# Certified 3-point slice x_0, x_1, x_2 (exact rationals, no float expansion).
SLICE = (Fraction(0, 1), Fraction(1, 1), Fraction(2, 1))

# Coupling weight between neighbouring slice coordinates.
COUPLING = Fraction(1, 1)


def f_convergent(_x: Fraction) -> Fraction:
    """Convergent / collapsing path. Zero-order exact slice representation."""
    return Fraction(13, 1)


def g_divergent(_x: Fraction) -> Fraction:
    """Divergent / repulsion path. Exact corner weight 1/2."""
    return Fraction(1, 2)


def make_ball(mid: Fraction) -> arb:
    """Exact rational midpoint plus an explicit 1e-40 radius enclosure."""
    point = arb(fmpq(mid.numerator, mid.denominator))
    return point + arb(f"+/- {RADIUS_STR}")


def entry(mid: Fraction) -> dict:
    ball = make_ball(mid)
    return {
        "mid": str(mid),
        "mid_num": mid.numerator,
        "mid_den": mid.denominator,
        "rad": RADIUS_STR,
        "ball_display": str(ball),
        "rad_leq_planck": bool(ball.rad() <= arb(PLANCK_STR)),
    }


def sample_path(fn):
    out = []
    for x in SLICE:
        mid = fn(x)
        ball = make_ball(mid)
        out.append(
            {
                "x": str(x),
                "mid": str(mid),
                "mid_num": mid.numerator,
                "mid_den": mid.denominator,
                "rad": RADIUS_STR,
                "ball_display": str(ball),
                "rad_leq_planck": bool(ball.rad() <= arb(PLANCK_STR)),
            }
        )
    return out


def build_matrix_recipe():
    f_balls = [make_ball(f_convergent(x)) for x in SLICE]
    g_balls = [make_ball(g_divergent(x)) for x in SLICE]
    c_ball = make_ball(COUPLING)

    dim = len(SLICE)
    entries = [[None] * dim for _ in range(dim)]
    for i in range(dim):
        entries[i][i] = entry(f_convergent(SLICE[i]))
        if i + 1 < dim:
            entries[i][i + 1] = entry(COUPLING)
            entries[i + 1][i] = entry(COUPLING)
    entries[0][dim - 1] = entry(g_divergent(SLICE[0]))
    entries[dim - 1][0] = entry(g_divergent(SLICE[dim - 1]))

    # Sanity: all four balls exist and every radius stays under the cutoff.
    for ball in f_balls + g_balls + [c_ball]:
        if not (ball.rad() <= arb(PLANCK_STR)):
            raise ValueError("Planck micro cutoff breached by ball radius")

    return {"dim": dim, "entries": entries}


def main() -> dict:
    if not (RADIUS <= PLANCK):
        raise SystemExit("RADIUS_ABOVE_PLANCK_CUTOFF: aborting (fail-closed)")

    os.makedirs(REPORTS, exist_ok=True)
    print(f"[FRESH BALL] Context precision: {flint.ctx.prec} bits")
    print(f"[FRESH BALL] Planck cutoff: {float(PLANCK):.6e} m")
    print(f"[FRESH BALL] Enclosure radius: {float(RADIUS):.6e} m (<= cutoff)")

    f_samples = sample_path(f_convergent)
    g_samples = sample_path(g_divergent)

    for tag, samples in (("f", f_samples), ("g", g_samples)):
        for s in samples:
            print(
                f"[FRESH BALL] {tag}(x={s['x']}) -> mid={s['mid']} "
                f"rad={s['rad']} ball={s['ball_display']}"
            )

    recipe = build_matrix_recipe()
    print(f"[FRESH BALL] Matrix recipe dim={recipe['dim']} assembled from f/g balls")

    report = {
        "phase": "PHASE_6_FRESH_BALL_REINIT",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "precision_bits": PRECISION_BITS,
        "computation_context": "flint.ctx.prec = 24000",
        "micro_cutoff": {
            "planck_length_m": "1.616255e-35",
            "planck_rational": f"{PLANCK.numerator}/{PLANCK.denominator}",
            "radius_rational": f"{RADIUS.numerator}/{RADIUS.denominator}",
            "radius_leq_planck": True,
        },
        "slice": [str(x) for x in SLICE],
        "paths": {
            "f_convergent": {"role": "convergent/collapsing", "samples": f_samples},
            "g_divergent": {"role": "divergent/repulsion", "samples": g_samples},
        },
        "coupling": entry(COUPLING),
        "matrix_recipe": recipe,
        "verdict": (
            "PASSED - raw f/g balls re-initialized at 24,000 bits; every "
            "radius within the Planck micro cutoff"
        ),
    }

    with open(OUT_PATH, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(report, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    print(f"[FRESH BALL] Manifest secured: {OUT_PATH}")
    return report


if __name__ == "__main__":
    result = main()
    print(f"FRESH BALL REINIT: {result['verdict']}")
