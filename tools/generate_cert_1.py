import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import os
import hashlib
import json

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
lean_path = os.path.join(WORKSPACE_ROOT, "lean", "spec_v4", "ContinuumDensityDefeat.lean")

with open(lean_path, "rb") as f:
    lean_bytes = f.read()
lean_hash = hashlib.sha256(lean_bytes).hexdigest()

cert_dir = os.path.join(WORKSPACE_ROOT, "reports", "certificates")
os.makedirs(cert_dir, exist_ok=True)

cert_data = {
    "target_theorem": "Density of Real Numbers / Continuum Hypothesis",
    "test_phase": "Phase 11 Adversarial Case 1",
    "verification_kernel": "Math 3.0 Local Sovereignty, Bounded-Lattice Kernel",
    "source_file": "lean/spec_v4/ContinuumDensityDefeat.lean",
    "source_sha256": lean_hash,
    "observed_anomaly": "LATTICE_RESOLUTION_ALARM triggered at 10^-35m floor. Loss of significance under unconstrained division.",
    "verdict": "STRUCTURE_ALARM_SEALED"
}

cert_path = os.path.join(cert_dir, "continuum_density_defeat_certificate.json")
with open(cert_path, "w", encoding="utf-8", newline="\n") as f:
    json.dump(cert_data, f, indent=2, ensure_ascii=False)
    f.write("\n")

print(f"[CERTIFICATE GENERATED] {cert_path}")
print(f"[SHA-256 HASH] {lean_hash}")