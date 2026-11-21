from __future__ import annotations

import flint

flint.ctx.prec = 6000

value = flint.arb(123) / (flint.arb(2) ** flint.arb(5))
mid_str = str(value.mid())
rad_str = str(value.rad())
print("value      =", str(value)[:80])
print("mid_str    =", repr(mid_str[:80]))
print("rad_str    =", repr(rad_str[:80]))

for label, fn in [
    ("arb(mid_str, rad_str)", lambda: flint.arb(mid_str, rad_str)),
    ("arb(mid_str)", lambda: flint.arb(mid_str)),
    ("arb(rad_str)", lambda: flint.arb(rad_str)),
    ("arb(0, rad_str)", lambda: flint.arb(0, rad_str)),
    ("arb(0, rad_value)", lambda: flint.arb(0, flint.arb(rad_str))),
    ("arb(0, rad.upper())", lambda: flint.arb(0, flint.arb(rad_str).upper())),
]:
    try:
        out = fn()
        print(f"  {label} -> {str(out)[:100]} rad={str(out.rad())[:40]}")
    except Exception as exc:  # noqa: BLE001
        print(f"  {label} EXC={type(exc).__name__}: {exc}")

print("\n-- copy semantics --")
m = flint.arb_mat(2, 2)
m[0, 0] = 1
for label, fn in [
    ("arb_mat(m)", lambda: flint.arb_mat(m)),
    ("m.__copy__()", lambda: m.__copy__()),
]:
    try:
        c = fn()
        c[0, 0] = 9
        print(f"  {label}: original={m[0,0]} copy={c[0,0]} isolated={m[0,0] == 1}")
    except Exception as exc:  # noqa: BLE001
        print(f"  {label} EXC={type(exc).__name__}: {exc}")

print("\n-- interval eig with zero-straddling diagonal --")
m2 = flint.arb_mat(2, 2)
m2[0, 0] = flint.arb("0", "1e-30")
m2[1, 1] = flint.arb("1", "0")
for kwargs in ({"multiple": True}, {"nonstop": True}):
    try:
        values = m2.eig(**kwargs)
        print(f"  eig({kwargs}) ->")
        for v in values:
            print("    ", v.real, "nan=", v.real.is_nan(), "contains0=", v.real.contains(0))
    except Exception as exc:  # noqa: BLE001
        print(f"  eig({kwargs}) EXC={type(exc).__name__}: {exc}")
