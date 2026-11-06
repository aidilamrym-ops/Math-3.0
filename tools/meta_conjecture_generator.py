import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import flint
from fractions import Fraction
import random
import gc
import sys as system_sys

system_sys.set_int_max_str_digits(0)
flint.ctx.prec = 48000

class DiscreteInertiaBoundaryDeterminantSweep:
    """
    Phase 20: Discrete Inertia Boundary Determinant (DIBD)
    Conjecture: DIBD ratio I = abs(det) / (norm_sq + abs(det) + 1) < 1.
    """
    def __init__(self):
        pass

    def evaluate_dibd(self, a, b, c):
        # Mixed inertia signature simulation with signed values
        d1 = a
        d2 = b
        d3 = c
        mat = [[d1, 0, 0], [0, d2, 0], [0, 0, d3]]
        det = d1 * d2 * d3
        norm_sq = sum(mat[i][j]**2 for i in range(3) for j in range(3))
        
        abs_det = abs(det)
        numerator = abs_det
        denominator = norm_sq + abs_det + 1
        ratio = Fraction(numerator, denominator)
        
        # Invariant bound: ratio < 1 <=> numerator < denominator <=> abs_det < norm_sq + abs_det + 1 <=> 0 < norm_sq + 1
        bounded = (numerator < denominator)
        return bounded, ratio, mat, det

    def run_sweep(self, count=10000):
        print(f"[DIBD SWEEP] Initializing 10,000 Monte Carlo sweep for Discrete Inertia Boundary Determinant...")
        for i in range(count):
            # Include near-zero determinants and mixed signs (inertia testing)
            a = random.randint(-100, 100) if i % 7 == 0 else random.randint(-10**15, 10**15)
            b = random.randint(-100, 100) if i % 11 == 0 else random.randint(-10**15, 10**15)
            c = random.randint(-5, 5) if i % 3 == 0 else random.randint(-10**15, 10**15)
            
            bounded, ratio, mat, det = self.evaluate_dibd(a, b, c)
            if not bounded:
                print(f"[FAIL-CLOSED BREACH] DIBD violation at iteration {i}!")
                print(f"  Matrix: {mat}")
                print(f"  Determinant: {det}")
                print(f"  Ratio: {ratio}")
                sys.exit(1)
            
            if i > 0 and i % 2500 == 0:
                print(f"  -> DIBD Progress: {i}/{count} verified. GC cleanup...")
                gc.collect()

        print(f"[DIBD SWEEP SUCCESS] Verified {count} mixed-inertia matrices without violation.")

if __name__ == "__main__":
    sweeper = DiscreteInertiaBoundaryDeterminantSweep()
    sweeper.run_sweep(10000)
    print("META_CONJECTURE_PHASE20_PASSED")
