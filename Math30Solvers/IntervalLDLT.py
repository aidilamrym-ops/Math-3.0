import sys
try:
    import flint
except ImportError:
    print("FATAL: python-flint missing.")
    sys.exit(2)


class IntervalLDLTSolver:
    """Sylvester inertia classifier for real-symmetric interval matrices.

    python-flint 0.9.0 exposes no arb_mat.ldl(), so inertia is derived from the
    eigenvalue enclosures returned by arb_mat.eig(nonstop=True). The guard below
    is fail-closed: any eigenvalue whose enclosure cannot be certified to a
    definite sign raises, it is never silently counted.
    """

    def __init__(self, arb_matrix):
        self.A = arb_matrix
        self.dim = arb_matrix.nrows()

    def compute_inertia(self) -> tuple:
        try:
            eigvals = self.A.eig(nonstop=True)
            n_pos, n_neg = 0, 0
            for idx, ev in enumerate(eigvals):
                real_part = ev.real
                imag_part = ev.imag
                # MathEncoding real-axis guard: for a real eigenvalue the imaginary
                # enclosure must contain 0. If 0 is excluded the eigenvalue is
                # provably off the real axis and cannot be classified as real.
                if not imag_part.contains(0):
                    raise UndeterminedPivotException(
                        f"Eigenvalue[{idx}] off real axis: imag={imag_part}"
                    )
                # Strict containment: reject any value ball that straddles zero.
                if real_part.contains(0):
                    raise UndeterminedPivotException(
                        f"Zero-straddling eigenvalue ball at index {idx}: {real_part}"
                    )
                if real_part > 0:
                    n_pos += 1
                elif real_part < 0:
                    n_neg += 1
                else:
                    # contains_zero() was False yet the sign is not certifiable.
                    raise UndeterminedPivotException(
                        f"Eigenvalue[{idx}] cannot be signed with certainty: {real_part}"
                    )
            return n_pos, n_neg, 0
        except UndeterminedPivotException as upe:
            print(f"[RESOLUTION ALARM] {upe}")
            raise ResolutionAlarm("Eigenvalue containment failure. Escalation required.")
        except Exception as e:
            print(f"[RESOLUTION ALARM] Eigenvalue computation failed: {e}")
            raise ResolutionAlarm("Eigenvalue computation failed. Escalation required.")


class UndeterminedPivotException(Exception):
    pass


class ResolutionAlarm(Exception):
    pass