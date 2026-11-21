import sys
try:
    import flint
except ImportError:
    print("FATAL: python-flint library missing.")
    sys.exit(2)


class IntervalMatrixBuilder:
    """Exact-width arb matrix builder.

    Entries are stored as `python-flint` balls, never as Python floats. The
    radius argument of :meth:`set_entry_exact` is a true radius about the
    midpoint, so `set_entry_exact(i, j, "1", "0.5")` stores `[0.5, 1.5]`.
    """

    def __init__(self, dimension: int, precision_bits: int = 6000):
        if not isinstance(dimension, int) or isinstance(dimension, bool):
            raise TypeError("dimension must be an integer.")
        if dimension < 0:
            raise ValueError("dimension must be nonnegative.")
        if not isinstance(precision_bits, int) or isinstance(precision_bits, bool):
            raise TypeError("precision_bits must be an integer.")
        if precision_bits < 2:
            raise ValueError("precision_bits must be at least 2.")
        self.dim = dimension
        self.prec = precision_bits
        flint.ctx.prec = precision_bits
        self.matrix = flint.arb_mat(dimension, dimension)
        self.threshold = flint.arb("1e-10")

    def set_entry_exact(self, i: int, j: int, mid_str: str, rad_str: str = "0"):
        if i >= self.dim or j >= self.dim or i < 0 or j < 0:
            raise IndexError("Matrix allocation index out of bounds.")
        midpoint = flint.arb(mid_str)
        radius = flint.arb(rad_str)
        if not midpoint.is_finite():
            raise ValueError("mid_str must encode a finite real number.")
        # `radius >= 0` is certainly-true comparison semantics in python-flint:
        # a radius that straddles zero (or is nan) is rejected, not coerced.
        if not radius.is_finite() or not (radius >= 0):
            raise ValueError("rad_str must encode a finite nonnegative radius.")
        self.matrix[i, j] = midpoint + flint.arb(0, radius)

    def audit_linear_morphology(self) -> dict:
        r_toep, r_hank = flint.arb("0"), flint.arb("0")
        for i in range(self.dim - 1):
            for j in range(self.dim - 1):
                diff = abs(self.matrix[i, j] - self.matrix[i+1, j+1])
                if diff > r_toep: r_toep = diff
        for i in range(self.dim - 1):
            for j in range(1, self.dim):
                diff = abs(self.matrix[i, j] - self.matrix[i+1, j-1])
                if diff > r_hank: r_hank = diff
        return {
            "r_toep": r_toep, "r_hank": r_hank,
            "is_toeplitz_approximate": bool(r_toep < self.threshold),
            "is_hankel_approximate": bool(r_hank < self.threshold)
        }

    def get_matrix_snapshot(self) -> flint.arb_mat:
        # arb_mat(other) copies; returning self.matrix would expose the live
        # builder state to callers despite the "snapshot" contract.
        return flint.arb_mat(self.matrix)
