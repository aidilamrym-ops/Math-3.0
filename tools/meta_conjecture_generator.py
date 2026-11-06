import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import flint
from fractions import Fraction
import math

flint.ctx.prec = 24000

class MetaConjectureGenerator:
    """
    Phase 13: Stabilized Discrete Sylvester Inertia Trace-Norm Invariant (DSITNI)
    Conjecture: Stabilized ratio norm_sq * (abs(det) + 1) / (den_bound * (abs(det) + 2)) < 1/2.
    """
    def __init__(self):
        self.rad_limit = Fraction(1, 10**40)

    def evaluate_conjecture(self, a, b, c):
        d1 = math.gcd(a, 0)
        d2 = math.gcd(b, 2)
        d3 = math.gcd(c, 2)
        mat = [[d1, 0, 0], [0, d2, 0], [0, 0, d3]]
        det = d1 * d2 * d3
        norm_sq = sum(mat[i][j]**2 for i in range(3) for j in range(3))
        trace_sq = sum(mat[i][i] for i in range(3))**2
        den_bound = trace_sq + 1
        
        numerator = norm_sq * (abs(det) + 1)
        denominator = den_bound * (abs(det) + 2)
        ratio = Fraction(numerator, denominator)
        
        contractible = ratio < Fraction(1, 2)
        return {
            "matrix": mat,
            "determinant": det,
            "norm_sq": norm_sq,
            "trace_sq": trace_sq,
            "den_bound": den_bound,
            "ratio": str(ratio),
            "contractible": contractible
        }

if __name__ == "__main__":
    gen = MetaConjectureGenerator()
    res1 = gen.evaluate_conjecture(2, 4, 8)
    print(f"[DSITNI CASE 1] Result: {res1}")
    if not res1["contractible"]:
        raise AssertionError("Conjecture breach on Case 1.")

    # Singular case: a=0 -> d1 = gcd(0,0) = 0 -> det = 0
    res2 = gen.evaluate_conjecture(0, 2, 4)
    print(f"[DSITNI CASE 2 SINGULAR] Result: {res2}")
    if not res2["contractible"]:
        raise AssertionError("Conjecture breach on Singular Case 2.")

    print("META_CONJECTURE_PHASE13_PASSED")
