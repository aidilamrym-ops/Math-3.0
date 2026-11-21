from __future__ import annotations

import flint

print("flint_version=", getattr(flint, "__version__", "?"))
print("ctx.prec=", flint.ctx.prec)

print("\n-- radius constructor semantics --")
for label, fn in [
    ("arb('1.0','0.1')", lambda: flint.arb("1.0", "0.1")),
    ("arb(0,'0.1')", lambda: flint.arb(0, "0.1")),
    ("arb('1.0','-0.1')", lambda: flint.arb("1.0", "-0.1")),
    ("arb('1.0') + arb('0.1')", lambda: flint.arb("1.0") + flint.arb("0.1")),
]:
    try:
        value = fn()
        print(f"  {label} = {value}  rad={value.rad()}  contains0={value.contains(0)}")
    except Exception as exc:  # noqa: BLE001
        print(f"  {label} EXC={type(exc).__name__}: {exc}")

print("\n-- equality semantics --")
a = flint.arb("1.0", "0.1")
b = flint.arb("1.0", "0.1")
c = flint.arb("1.0", "0.2")
d = flint.arb("1.05")
print("  identical ==", a == b)
print("  overlap ==", a == d, " (d inside a?)", a.contains(d))
print("  different rad ==", a == c)

print("\n-- eig behavior --")
for label, rows in [
    ("identity2", [[1, 0], [0, 1]]),
    ("diag_distinct", [[-1, 0, 0], [0, 2, 0], [0, 0, 3]]),
    ("diag_repeat", [[-1, 0, 0], [0, 2, 0], [0, 0, 2]]),
    ("sym_mixed_2", [[2, 3], [3, 2]]),
    ("sym_pd_2", [[2, 1], [1, 2]]),
    ("triangular", [[1, 2], [0, 1]]),
    ("rotation", [[0, 1], [-1, 0]]),
]:
    matrix = flint.arb_mat(rows)
    for kwargs in ({"nonstop": True}, {}):
        try:
            values = matrix.eig(**kwargs)
            real = [str(v.real)[:34] for v in values]
            imag = [str(v.imag)[:34] for v in values]
            any_nan = any(v.real.is_nan() for v in values)
            print(f"  {label} eig({kwargs}) n={len(values)} nan={any_nan} real={real} imag={imag}")
        except Exception as exc:  # noqa: BLE001
            print(f"  {label} eig({kwargs}) EXC={type(exc).__name__}: {exc}")
    try:
        acb = flint.acb_mat(matrix)
        values = acb.eig()
        print(f"  {label} acb_eig n={len(values)} any_nan={any(v.real.is_nan() for v in values)}")
    except Exception as exc:  # noqa: BLE001
        print(f"  {label} acb_eig EXC={type(exc).__name__}: {exc}")
