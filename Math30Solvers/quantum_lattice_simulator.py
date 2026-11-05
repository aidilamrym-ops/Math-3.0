import math
import random
from fractions import Fraction

class GaussianRational:
    """Exact Gaussian Rational z = a + bi where a, b in Q."""
    def __init__(self, real, imag=0):
        self.real = Fraction(real)
        self.imag = Fraction(imag)

    def norm_sq(self):
        return self.real**2 + self.imag**2

    def __add__(self, other):
        return GaussianRational(self.real + other.real, self.imag + other.imag)

    def __sub__(self, other):
        return GaussianRational(self.real - other.real, self.imag - other.imag)

    def __mul__(self, other):
        return GaussianRational(
            self.real * other.real - self.imag * other.imag,
            self.real * other.imag + self.imag * other.real
        )

    def __repr__(self):
        return f"({self.real} + {self.imag}i)"

class DiscreteQubit:
    """
    Math 3.0 Discrete Qubit State.
    State is |psi> = 1/sqrt(2^scale) * (alpha |0> + beta |1>)
    where alpha, beta in Z[i].
    """
    def __init__(self, a_re, a_im, b_re, b_im, scale=0):
        self.a_re = int(a_re)
        self.a_im = int(a_im)
        self.b_re = int(b_re)
        self.b_im = int(b_im)
        self.scale = int(scale)
        self.verify_norm()

    def verify_norm(self):
        """Pure integer identity: |a|^2 + |b|^2 = 2^scale."""
        lhs = self.a_re**2 + self.a_im**2 + self.b_re**2 + self.b_im**2
        rhs = 2**self.scale
        if lhs != rhs:
            raise ValueError(f"LATTICE_NORM_VIOLATION: {lhs} != {rhs}")

    def apply_x(self):
        """Pauli-X: bit flip."""
        self.a_re, self.b_re = self.b_re, self.a_re
        self.a_im, self.b_im = self.b_im, self.a_im
        # Norm is invariant, scale unchanged.

    def apply_h(self):
        """Discrete Hadamard: |0> -> (|0>+|1>)/sqrt(2), |1> -> (|0>-|1>)/sqrt(2)."""
        new_a_re = self.a_re + self.b_re
        new_a_im = self.a_im + self.b_im
        new_b_re = self.a_re - self.b_re
        new_b_im = self.a_im - self.b_im
        
        self.a_re, self.a_im = new_a_re, new_a_im
        self.b_re, self.b_im = new_b_re, new_b_im
        self.scale += 1
        self.verify_norm()

    def measure(self, seed=None):
        """
        Deterministic measurement with Planck resolution alarm.
        Resolution limit: scale <= 128 (arbitrary threshold for 'Planck' depth).
        """
        if self.scale > 128:
            print("QUANTUM_SIMULATION_ALARM: Precision depth breaches Planck lattice resolution.")
            return None

        if seed is not None:
            random.seed(seed)
        
        prob_0_num = self.a_re**2 + self.a_im**2
        prob_total = 2**self.scale
        
        # Check for non-decidable state (near 0.5 with high scale)
        if self.scale > 60 and abs(prob_0_num * 2 - prob_total) < 100:
             print("QUANTUM_SIMULATION_ALARM: Indeterminate state at lattice resolution limit.")
             return None

        r = random.getrandbits(self.scale) if self.scale > 0 else 0
        if prob_0_num > r:
            return 0
        return 1

if __name__ == "__main__":
    # Test: Hadamard on |0>
    q = DiscreteQubit(1, 0, 0, 0, 0) # |0>
    print(f"Initial: {q.a_re}, {q.b_re}, scale={q.scale}")
    q.apply_h()
    print(f"After H: {q.a_re}, {q.b_re}, scale={q.scale}")
    q.verify_norm()
    res = q.measure(seed=42)
    print(f"Measured: {res}")
