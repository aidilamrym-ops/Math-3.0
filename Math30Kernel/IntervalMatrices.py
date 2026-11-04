import sys
try:
    import flint
except ImportError:
    print("FATAL: python-flint library missing.")
    sys.exit(2)

class IntervalMatrixBuilder:
    def __init__(self, dimension: int, precision_bits: int = 6000):
        self.dim = dimension
        self.prec = precision_bits
        flint.ctx.prec = precision_bits
        self.matrix = flint.arb_mat(dimension, dimension)
        self.threshold = flint.arb("1e-10")

    def set_entry_exact(self, i: int, j: int, mid_str: str, rad_str: str = "0"):
        if i >= self.dim or j >= self.dim or i < 0 or j < 0:
            raise IndexError("Matrix allocation index out of bounds.")
        self.matrix[i, j] = flint.arb(mid_str) + flint.arb(rad_str)

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
        return self.matrix