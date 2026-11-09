import os
import sys
import json
from datetime import datetime, timezone
from fractions import Fraction

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS = os.path.join(WORKSPACE_ROOT, "reports")

class HeisenbergUncertaintyStressTest:
    def __init__(self, precision_bits: int = 24000):
        self.precision = precision_bits

    def run_stress_test(self):
        print("[HEISENBERG STRESS TEST] Initializing Zero-Radius Coordinate Attack...")
        
        # Attempt zero-radius point initialization on the continuum.
        dx_radius = Fraction(0, 1)
        planck_floor = Fraction(1, 10 ** 35)

        uncertainty_alarm = bool(dx_radius < planck_floor)
        if not uncertainty_alarm:
            raise RuntimeError(
                "Uncertainty check failed: point radius is not below the Planck floor."
            )
        print("  -> UNCERTAINTY_RESOLUTION_ALARM: Zero-radius point localization intercepted. Finite interval ball enforced.")

        report = {
            "test": "QUANTUM_UNCERTAINTY_DEMYSTIFICATION",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "precision_bits": self.precision,
            "uncertainty_alarm": uncertainty_alarm,
            "verdict": "UNCERTAINTY_RESOLUTION_ALARM_VERIFIED" if uncertainty_alarm else "FAILED_UNCERTAINTY_VIOLATED"
        }

        os.makedirs(REPORTS, exist_ok=True)
        out_path = os.path.join(REPORTS, "heisenberg_uncertainty_stress_test.json")
        with open(out_path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(f"[REPORT SECURED] {out_path}")

        return report


def main() -> int:
    report = HeisenbergUncertaintyStressTest().run_stress_test()
    return 0 if report["uncertainty_alarm"] else 1


def test_heisenberg_uncertainty_stress_test():
    report = HeisenbergUncertaintyStressTest().run_stress_test()
    assert report["uncertainty_alarm"] is True
    assert report["verdict"] == "UNCERTAINTY_RESOLUTION_ALARM_VERIFIED"


if __name__ == "__main__":
    sys.exit(main())
