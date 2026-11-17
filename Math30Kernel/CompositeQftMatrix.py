import sys
import flint
from Math30Kernel.IntervalMatrices import IntervalMatrixBuilder

def synthesize_qft_interval_matrix(a00_re: int, a00_im: int,
                                   a01_re: int, a01_im: int,
                                   a10_re: int, a10_im: int,
                                   a11_re: int, a11_im: int,
                                   scale: int) -> IntervalMatrixBuilder:
    """
    Synthesizes a 2x2 density matrix / state operator over arbitrary-precision ball arithmetic
    from discrete 2-qubit integer components and normalization scale.
    """
    prec = 6000
    flint.ctx.prec = prec
    
    denom = flint.arb(2) ** flint.arb(scale)
    builder = IntervalMatrixBuilder(dimension=2, precision_bits=prec)
    
    # Real components divided by denom
    c00 = flint.arb(a00_re) / denom
    c01 = flint.arb(a01_re) / denom
    c10 = flint.arb(a10_re) / denom
    c11 = flint.arb(a11_re) / denom

    builder.set_entry_exact(0, 0, str(c00.mid()), str(c00.rad()))
    builder.set_entry_exact(0, 1, str(c01.mid()), str(c01.rad()))
    builder.set_entry_exact(1, 0, str(c10.mid()), str(c10.rad()))
    builder.set_entry_exact(1, 1, str(c11.mid()), str(c11.rad()))
    
    return builder

if __name__ == "__main__":
    builder = synthesize_qft_interval_matrix(1, 0, 1, 0, 1, 0, 1, 0, scale=2)
    morphology = builder.audit_linear_morphology()
    print("COMPOSITE OPERATOR SYNTHESIS SUCCESS:")
    print(f"Matrix Snapshot:\n{builder.get_matrix_snapshot()}")
    print(f"Morphology Audit: {morphology}")
