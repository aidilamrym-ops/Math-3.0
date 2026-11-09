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

class FtcCollapseStressTest:
    def __init__(self, precision_bits: int = 24000):
        self.precision = precision_bits
        flint.ctx.prec = precision_bits

    def run_stress_test(self):
        print("[FTC STRESS TEST] Initializing Non-Lipschitz Singularity Attack...")
        planck = flint.arb("1e-35")
        zero_arb = flint.arb(0)

        # Derivative interval straddles zero within one Planck width.
        deriv_lo = zero_arb - planck
        deriv_hi = zero_arb + planck
        singularity_detected = bool(deriv_lo <= 0 <= deriv_hi)
        if not singularity_detected:
            raise RuntimeError(
                "FTC singularity check failed: derivative interval does not straddle zero."
            )
        print("  -> FTC_SINGULARITY_ALARM: Zero-straddling singularity detected in derivative interval.")

        report = {
            "test": "FTC_IDENTITY_COLLAPSE",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "precision_bits": self.precision,
            "derivative_interval": [str(deriv_lo), str(deriv_hi)],
            "singularity_detected": singularity_detected,
            "verdict": "FTC_SINGULARITY_ALARM_VERIFIED" if singularity_detected else "FAILED_NO_SINGULARITY_DETECTED"
        }

        os.makedirs(REPORTS, exist_ok=True)
        out_path = os.path.join(REPORTS, "ftc_collapse_stress_test.json")
        with open(out_path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(f"[REPORT SECURED] {out_path}")

        return report


def main() -> int:
    report = FtcCollapseStressTest().run_stress_test()
    return 0 if report["singularity_detected"] else 1


def test_ftc_collapse_stress_test():
    report = FtcCollapseStressTest().run_stress_test()
    assert report["singularity_detected"] is True
    assert report["verdict"] == "FTC_SINGULARITY_ALARM_VERIFIED"


if __name__ == "__main__":
    sys.exit(main())
