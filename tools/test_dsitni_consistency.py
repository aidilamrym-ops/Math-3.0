"""Gate 4 DSITNI denominator consistency check (no framework).

Verifies that the Beal / Quantum-Topology solvers implement exactly the DSITNI
form certified in `lean/spec_v4/certificates/DiscreteSylvesterInertiaTraceNormInvariant.lean`
and documented in README section 5.3:

    R = ||tau||_F^2 * (|det tau| + 1)
        / (3 * ((tr tau)^2 + 1) * (|det tau| + 2))  <  1/2

The solver integer test is `2*S*(D+1) < 3*(T+1)*(D+2)`, which is exactly
`R < 1/2` after clearing the 2. The Yu-Deng sign-mixed regime is NOT DSITNI and
uses a determinant-scaled variant; we assert DSITNI genuinely fails there so the
separate formula is justified rather than cosmetic.
"""
import importlib.util
import os
from fractions import Fraction

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, rel))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


BealLatticeSolver = _load("beal", "mcp/t2n/solvers/beal_lattice_solver.py").BealLatticeSolver
QuantumTopologySolver = _load("qtop", "mcp/t2n/solvers/quantum_topology_solver.py").QuantumTopologySolver
YuDengSingularitySieve = _load("yd", "mcp/t2n/solvers/yudeng_singularity_sieve.py").YuDengSingularitySieve


def dsitni(S, T, D):
    """R == S*(D+1) / (3*(T+1)*(D+2)); True iff R < 1/2."""
    r = Fraction(S * (D + 1), 3 * (T + 1) * (D + 2))
    return r < Fraction(1, 2), r


def main():
    beal = BealLatticeSolver()
    qtop = QuantumTopologySolver()
    yd = YuDengSingularitySieve()

    # 1. Positive-definite Sylvester grid (Beal / Quantum domain), incl. 10^18.
    vals = [1, 2, 3, 5, 10, 1000, 10**18]
    for a in vals:
        for b in vals:
            for c in vals:
                ok, _ = dsitni(a*a + b*b + c*c, (a+b+c)**2, a*b*c)
                assert ok, ("DSITNI failed", a, b, c)

                # Solver must agree: boolean AND ratio == 2*R_DSITNI.
                contractible, ratio = beal.gate4_contractibility_check(a, b, c)
                assert contractible, ("beal solver disagreed", a, b, c)
                _, r = dsitni(a*a + b*b + c*c, (a+b+c)**2, a*b*c)
                assert ratio == 2 * r, ("beal ratio != 2*DSITNI", a, b, c, ratio, r)

    # 2. Lean certificate sample points must satisfy the same inequality.
    assert dsitni(12, 36, 8)[0]
    assert dsitni(100, 400, 1000)[0]

    # 3. Quantum-Topology Dehn-filling solver must agree with DSITNI form.
    for i in range(0, 200, 7):
        p = i - 100
        q = (i * 3) % 997 + 1
        bounded, ratio, mat, det = qtop.dehn_filling_sylvester_matrix(p, q)
        assert bounded, ("qtop solver disagreed", p, q)
        d = [mat[i][i] for i in range(3)]
        S = sum(x*x for x in d)
        T = sum(d) ** 2
        _, r = dsitni(S, T, abs(det))
        assert ratio == 2 * r, ("qtop ratio != 2*DSITNI", p, q, ratio, r)

    # 4. Sign-mixed Yu-Deng regime: DSITNI fails, so the det-scaled variant is
    #    necessary (not a cosmetic fork).
    d = [3, 3, -3]
    S = sum(x*x for x in d)
    T = sum(d) ** 2
    D = abs(d[0] * d[1] * d[2])
    ok, _ = dsitni(S, T, D)
    assert not ok, "expected DSITNI to fail on sign-mixed matrix"
    # ... while the solver's own gate certifies contraction on its test matrix.
    mat, det = yd.sylvester_spectral_matrix(2, 4, 8)
    ratio, contractible = yd.gate4_contractibility_check(mat, det)
    assert contractible and ratio < Fraction(1, 2)

    print("DSITNI_CONSISTENCY_TEST_PASSED")


if __name__ == "__main__":
    main()
