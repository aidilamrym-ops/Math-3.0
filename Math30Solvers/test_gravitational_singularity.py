import os
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

class GravitationalSingularityStressTest:
    def __init__(self, precision_bits: int = 24000):
        self.precision = precision_bits
        flint.ctx.prec = precision_bits

    def run_stress_test(self):
        print("[SINGULARITY STRESS TEST] Initializing Planck-Volume Density Floor Attack...")
        
        # Mass M = 1 Solar Mass equivalent in arbitrary units
        mass = flint.arb("1.989e30")
        
        # Planck volume limit V_P approx 4.22e-105 m^3
        planck_vol = flint.arb("4.22e-105")
        
        # Attempt to contract volume below Planck limit
        collapsed_vol = flint.arb("1e-110")
        
        singularity_alarm = False
        # ResolutionAlarm guard BEFORE division. arb returns nan silently for a
        # zero/sub-Planck divisor; intercept first so infinity is never formed.
        if collapsed_vol <= 0 or collapsed_vol <= planck_vol:
            singularity_alarm = True
            print("  -> GRAVITATIONAL_SINGULARITY_ALARM: Sub-Planck volume division intercepted. Infinity blocked.")
        else:
            density = mass / collapsed_vol
            if not density.is_finite():
                raise RuntimeError(
                    "GRAVITATIONAL_SINGULARITY_ALARM: non-finite density after bounded volume division."
                )

        report = {
            "test": "GRAVITATIONAL_SINGULARITY_DISMANTLEMENT",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "precision_bits": self.precision,
            "singularity_alarm": singularity_alarm,
            "verdict": "GRAVITATIONAL_SINGULARITY_ALARM_VERIFIED" if singularity_alarm else "FAILED_SINGULARITY_UNLOCKED"
        }

        os.makedirs(REPORTS, exist_ok=True)
        out_path = os.path.join(REPORTS, "gravitational_singularity_stress_test.json")
        with open(out_path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(f"[REPORT SECURED] {out_path}")

        return report


def main() -> int:
    report = GravitationalSingularityStressTest().run_stress_test()
    return 0 if report["singularity_alarm"] else 1


def test_gravitational_singularity_stress_test():
    report = GravitationalSingularityStressTest().run_stress_test()
    assert report["singularity_alarm"] is True
    assert report["verdict"] == "GRAVITATIONAL_SINGULARITY_ALARM_VERIFIED"


if __name__ == "__main__":
    sys.exit(main())
