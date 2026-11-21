import sys
try:
    import flint
except ImportError:
    print("FATAL: python-flint missing.")
    sys.exit(2)


class IntervalLDLTSolver:
    """
    Certified Sylvester inertia classifier for real-symmetric interval matrices.

    Inertia is emitted only when every eigenvalue enclosure certifies its sign.
    Non-square, non-symmetric, non-isolatable, non-finite, non-real, and
    zero-straddling inputs all fail closed with ResolutionAlarm.
    """

    def __init__(self, arb_matrix):
        self.A = arb_matrix
        self.dim = arb_matrix.nrows()

    def _require_symmetric(self) -> None:
        if self.dim < 0:
            raise UndeterminedPivotException(f"invalid matrix dimension {self.dim}")
        columns = self.A.ncols()
        if self.dim != columns:
            raise UndeterminedPivotException(
                f"matrix must be square, got {self.dim}x{columns}"
            )
        for i in range(self.dim):
            for j in range(i + 1, self.dim):
                left, right = self.A[i, j], self.A[j, i]
                if not (left.contains(right) and right.contains(left)):
                    raise UndeterminedPivotException(
                        f"matrix is not symmetric at ({i}, {j})"
                    )

    def compute_inertia(self) -> tuple:
        try:
            self._require_symmetric()
            eigvals = self.A.eig(multiple=True)
            if len(eigvals) != self.dim:
                raise UndeterminedPivotException(
                    f"expected {self.dim} eigenvalue enclosures, got {len(eigvals)}"
                )
            n_pos, n_neg, n_zero = 0, 0, 0
            for idx, ev in enumerate(eigvals):
                real_part = ev.real
                if real_part.is_nan() or not real_part.is_finite():
                    raise UndeterminedPivotException(
                        f"no certified real eigenvalue enclosure at index {idx}"
                    )
                if not ev.imag.contains(0):
                    raise UndeterminedPivotException(
                        f"non-real eigenvalue enclosure at index {idx}: {ev.imag}"
                    )
                if real_part.contains(0):
                    raise UndeterminedPivotException(
                        f"Zero-straddling eigenvalue at {idx}: {real_part}"
                    )
                if real_part > 0:
                    n_pos += 1
                elif real_part < 0:
                    n_neg += 1
                else:
                    n_zero += 1
            return n_pos, n_neg, n_zero
        except Exception as e:
            raise ResolutionAlarm(f"Inertia computation failed: {e}") from e


class UndeterminedPivotException(Exception):
    pass


class ResolutionAlarm(Exception):
    pass
