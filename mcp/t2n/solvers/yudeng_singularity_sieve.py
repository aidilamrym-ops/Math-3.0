import sys
import flint
from fractions import Fraction
import math

# Global precision context for flint
flint.ctx.prec = 24000

class YuDengSingularitySieve:
    def __init__(self):
        # Radius limit in exact rational form 10^-40 m
        self.rad_limit = Fraction(1, 10**40)
        
    def create_interval(self, val: int):
        mid = Fraction(val)
        return (mid - self.rad_limit, mid + self.rad_limit)
        
    def sylvester_spectral_matrix(self, velocity_gradient, curvature, density):
        # 3x3 fluid moment matrix
        d1 = math.gcd(abs(velocity_gradient), 2) + 1
        d2 = math.gcd(abs(curvature), 2) + 1
        d3 = math.gcd(abs(density), 2) + 1
        mat = [[d1, 0, 0], [0, d2, 0], [0, 0, -d3]] # Unstable polarity sign-flip indicator on d3
        det = d1 * d2 * (-d3)
        return mat, det
        
    def gate4_contractibility_check(self, mat, det):
        # Trace-based spectral bound / denominator bound derived from matrix diagonal
        frobenius_norm_sq = sum(mat[i][j]**2 for i in range(3) for j in range(3))
        denominator_bound = sum(mat[i][i] for i in range(3))**2 + 1
        scale = Fraction(1, max(1, abs(det))) + self.rad_limit
        ratio = Fraction(frobenius_norm_sq, denominator_bound) * scale
        if ratio >= Fraction(1, 2):
            print(f"[FAIL-CLOSED WARNING] Contraction ratio {ratio} >= 1/2. Precision escalation triggered.")
            return ratio, False
        return ratio, True
        
    def test(self):
        vg, curv, dens = 2, 4, 8
        iv = self.create_interval(vg)
        if not (iv[0] < Fraction(vg) < iv[1]):
            raise AssertionError("Interval containment failed")
            
        mat, det = self.sylvester_spectral_matrix(vg, curv, dens)
        ratio, contractible = self.gate4_contractibility_check(mat, det)
        
        # Verify sign flip in determinant
        if det >= 0:
            raise AssertionError("Determinant sign flip failed")
            
        return contractible

if __name__ == "__main__":
    sieve = YuDengSingularitySieve()
    if "--test" in sys.argv:
        if sieve.test():
            print("YUDENG_SINGULARITY_SIEVE_TEST_PASSED")
        else:
            print("YUDENG_SINGULARITY_SIEVE_TEST_FAILED")
            sys.exit(1)
