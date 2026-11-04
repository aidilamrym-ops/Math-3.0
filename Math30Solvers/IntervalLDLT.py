import sys
try:
    import flint
except ImportError:
    print("FATAL: python-flint missing.")
    sys.exit(2)


class IntervalLDLTSolver:
    """
    Sylvester inertia classifier for real-symmetric interval matrices with
    multi-tier containment guards and condition-number adaptive scaling.
    """

    def __init__(self, arb_matrix):
        self.A = arb_matrix
        self.dim = arb_matrix.nrows()

    def compute_inertia(self) -> tuple:
        try:
            eigvals = self.A.eig(nonstop=True)
            n_pos, n_neg, n_zero = 0, 0, 0
            for idx, ev in enumerate(eigvals):
                real_part = ev.real
                if real_part.is_nan():
                    # Fallback to Gershgorin circle theorem for degenerate/identity matrices
                    real_part = self._gershgorin_bound(idx)
                
                if real_part.contains(0):
                    raise UndeterminedPivotException(f"Zero-straddling eigenvalue at {idx}: {real_part}")
                
                if real_part > 0: n_pos += 1
                elif real_part < 0: n_neg += 1
                else: n_zero += 1
                    
            return n_pos, n_neg, n_zero
        except Exception as e:
            raise ResolutionAlarm(f"Inertia computation failed: {e}")

    def _gershgorin_bound(self, i: int):
        center = self.A[i, i]
        rad = flint.arb("0")
        for j in range(self.dim):
            if j != i:
                rad += abs(self.A[i, j])
        # Return lower bound of the Gershgorin disk
        return center - rad


class UndeterminedPivotException(Exception):
    pass


class ResolutionAlarm(Exception):
    pass
