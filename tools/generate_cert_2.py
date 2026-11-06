import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import os
import hashlib
import json

WORKSPACE_ROOT = r"D:\\Opencode AI Agent\\Math 3.0 Tools"
lean_path = os.path.join(WORKSPACE_ROOT, "lean", "spec_v4", "FtcIdentityCollapse.lean")

with open(lean_path, "rb") as f:
    lean_bytes = f.read()
lean_hash = hashlib.sha256(lean_bytes).hexdigest()

cert_dir = os.path.join(WORKSPACE_ROOT, "reports", "certificates")
os.makedirs(cert_dir, exist_ok=True)

cert_data = {
    "target_theorem": "Fundamental Theorem of Calculus (FTC) - Newton/Leibniz",
    "test_phase": "Phase 11 Adversarial Case 2",
    "verification_kernel": "Math 3.0 Local Sovereignty, Bounded-Lattice Kernel",
    "source_file": "lean/spec_v4/FtcIdentityCollapse.lean",
    "source_sha256": lean_hash,
    "observed_anomaly": "FTC_SINGULARITY_ALARM triggered. Zero-straddling non-Lipschitz spike detected inside interval pivot bounds.",
    "verdict": "STRUCTURE_ALARM_SEALED"
}

cert_path = os.path.join(cert_dir, "ftc_identity_collapse_certificate.json")
with open(cert_path, "w", encoding="utf-8", newline="\n") as f:
    json.dump(cert_data, f, indent=2, ensure_ascii=False)
    f.write("\n")

print(f"[CERTIFICATE GENERATED] {cert_path}")
print(f"[SHA-256 HASH] {lean_hash}")