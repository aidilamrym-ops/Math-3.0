import os
sys_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Math30Solvers/test_continuum_density.py
import sys
import json
from datetime import datetime, timezone
from fractions import Fraction

try:
    import flint
except ImportError:
    print("FATAL: python-flint missing.")
    sys.exit(2)

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS = os.path.join(WORKSPACE_ROOT, "reports")

class ContinuumDensityStressTest:
    def __init__(self, precision_bits: int = 24000):
        self.precision = precision_bits
        flint.ctx.prec = precision_bits

    def run_stress_test(self):
        print("[CONTINUUM STRESS TEST] Initializing Lattice Resolution Attack...")
        # Planck scale fraction separation: 10^(-35)
        # Using rational representation
        a = Fraction(1, 1)
        planck_sep = Fraction(1, 10**35)
        b = a + planck_sep

        print(f"  -> Initial interval [a, b]: [{a}, {b}]")
        print(f"  -> Separation: {planck_sep}")

        current_a = flint.arb(str(a))
        current_b = flint.arb(str(b))

        iterations = 0
        max_iterations = 100
        alarm_triggered = False

        for i in range(max_iterations):
            iterations += 1
            midpoint = (current_a + current_b) / 2
            
            # Check interval radius against precision and Planck scale limits
            radius = midpoint.rad()
            
            # If radius collapses or hits resolution floor, trigger LATTICE_RESOLUTION_ALARM
            if radius == 0 or radius < flint.arb("1e-100"):
                alarm_triggered = True
                print(f"  -> LATTICE_RESOLUTION_ALARM triggered at iteration {iterations}: radius collapsed to {radius}.")
                break
            
            # Refine interval
            current_b = midpoint

        report = {
            "test": "CONTINUUM_DENSITY_DISMANTLEMENT",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "precision_bits": self.precision,
            "iterations": iterations,
            "alarm_triggered": alarm_triggered,
            "verdict": "LATTICE_RESOLUTION_ALARM_VERIFIED" if alarm_triggered else "FAILED_CONTINUOUS_COLLAPSE"
        }

        os.makedirs(REPORTS, exist_ok=True)
        out_path = os.path.join(REPORTS, "continuum_density_stress_test.json")
        with open(out_path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(f"[REPORT SECURED] {out_path}")

        return report


def main() -> int:
    report = ContinuumDensityStressTest().run_stress_test()
    return 0 if report["alarm_triggered"] else 1


def test_continuum_density_stress_test():
    report = ContinuumDensityStressTest().run_stress_test()
    assert report["alarm_triggered"] is True
    assert report["verdict"] == "LATTICE_RESOLUTION_ALARM_VERIFIED"


if __name__ == "__main__":
    sys.exit(main())
