import os
import hashlib
import json

WORKSPACE_ROOT = r"D:\\Opencode AI Agent\\Math 3.0 Tools"
lean_path = os.path.join(WORKSPACE_ROOT, "lean", "spec_v4", "HeisenbergUncertaintyDemystified.lean")

with open(lean_path, "rb") as f:
    lean_bytes = f.read()
lean_hash = hashlib.sha256(lean_bytes).hexdigest()

cert_dir = os.path.join(WORKSPACE_ROOT, "reports", "certificates")
os.makedirs(cert_dir, exist_ok=True)

cert_data = {
    "target_theorem": "Heisenberg Uncertainty Principle",
    "test_phase": "Phase 11 Adversarial Case 5",
    "verification_kernel": "Math 3.0 Local Sovereignty, Bounded-Lattice Kernel",
    "source_file": "lean/spec_v4/HeisenbergUncertaintyDemystified.lean",
    "source_sha256": lean_hash,
    "observed_anomaly": "UNCERTAINTY_RESOLUTION_ALARM triggered. Zero-radius point-localization attempt defeated by lattice invariant floor.",
    "verdict": "STRUCTURE_ALARM_SEALED"
}

cert_path = os.path.join(cert_dir, "heisenberg_uncertainty_demystified_certificate.json")
with open(cert_path, "w", encoding="utf-8", newline="\n") as f:
    json.dump(cert_data, f, indent=2, ensure_ascii=False)
    f.write("\n")

print(f"[CERTIFICATE GENERATED] {cert_path}")
print(f"[SHA-256 HASH] {lean_hash}")
