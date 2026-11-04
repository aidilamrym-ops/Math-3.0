import sys
try:
    import flint
except ImportError:
    print("FATAL: Python-Flint library missing from active interpreter path.")
    sys.exit(2)

DEFAULT_PRECISION_BITS = 6000
flint.ctx.prec = DEFAULT_PRECISION_BITS

def get_kernel_precision() -> int:
    return flint.ctx.prec

def allocate_exact_ball(mid_string: str, radius_string: str = "0") -> flint.arb:
    return flint.arb(mid_string) + flint.arb(radius_string)

def verify_zero_leak(acb_ball) -> bool:
    return bool(acb_ball.imag.is_zero())

__all__ = ["DEFAULT_PRECISION_BITS", "get_kernel_precision", "allocate_exact_ball", "verify_zero_leak"]
print(f"MATH 3.0 KERNEL: Native Flint bindings initialized at {DEFAULT_PRECISION_BITS} bits.")