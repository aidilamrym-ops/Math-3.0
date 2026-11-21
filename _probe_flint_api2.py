from __future__ import annotations

import flint

flint.ctx.prec = 6000

print("-- eig(multiple=True) --")
for label, rows in [
    ("identity2", [[1, 0], [0, 1]]),
    ("diag_repeat", [[-1, 0, 0], [0, 2, 0], [0, 0, 2]]),
    ("triangular", [[1, 2], [0, 1]]),
    ("singular", [[1, 1, 0], [1, 1, 0], [0, 0, 2]]),
    ("sym_mixed", [[2, 3], [3, 2]]),
    ("rotation", [[0, 1], [-1, 0]]),
]:
    matrix = flint.arb_mat(rows)
    try:
        values = matrix.eig(multiple=True)
        print(f"  {label}: n={len(values)}")
        for value in values:
            print(f"    real={value.real} imag={value.imag} nan={value.real.is_nan()}")
    except Exception as exc:  # noqa: BLE001
        print(f"  {label} EXC={type(exc).__name__}: {exc}")

print("\n-- identity 100 eig(multiple=True) --")
big = flint.arb_mat(100, 100)
for i in range(100):
    big[i, i] = 1
try:
    values = big.eig(multiple=True)
    print("  n=", len(values), "nan=", any(v.real.is_nan() for v in values))
    print("  first=", values[0].real, " last=", values[-1].real)
except Exception as exc:  # noqa: BLE001
    print(f"  EXC={type(exc).__name__}: {exc}")

print("\n-- symmetry containment --")
a = flint.arb("1.0", "0.1")
a2 = flint.arb("1.0", "0.1")
b = flint.arb("1.05")
print("  a contains a2", a.contains(a2), "a2 contains a", a2.contains(a))
print("  a contains a", a.contains(a))
print("  a == a", a == a)
print("  exact 1 == 1", flint.arb(1) == flint.arb(1))
print("  diff == 0", (a - a) == 0, " diff", a - a)

print("\n-- builder edge inputs --")
for label, fn in [
    ("arb_mat(0,0)", lambda: flint.arb_mat(0, 0)),
    ("arb_mat(-1,-1)", lambda: flint.arb_mat(-1, -1)),
    ("arb_mat(2,3)", lambda: flint.arb_mat(2, 3)),
    ("prec=0", lambda: setattr(flint.ctx, "prec", 0)),
    ("prec=-5", lambda: setattr(flint.ctx, "prec", -5)),
    ("arb('abc')", lambda: flint.arb("abc")),
    ("arb(2.5)", lambda: flint.arb(2.5)),
]:
    try:
        out = fn()
        print(f"  {label} -> {out}")
    except Exception as exc:  # noqa: BLE001
        print(f"  {label} EXC={type(exc).__name__}: {exc}")

print("\n-- non-square eig --")
try:
    m = flint.arb_mat(2, 3)
    print("  nrows/ncols", m.nrows(), m.ncols())
    print("  eig", m.eig(nonstop=True))
except Exception as exc:  # noqa: BLE001
    print(f"  EXC={type(exc).__name__}: {exc}")
