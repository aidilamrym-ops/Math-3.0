import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import sys
import os
import json
import time
import ctypes
import subprocess
import importlib.util
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Set process priority to low (Windows only; never fatal on other platforms)
if os.name == "nt":
    try:
        handle = ctypes.windll.kernel32.GetCurrentProcess()
        ctypes.windll.kernel32.SetPriorityClass(handle, 0x00004040) # BELOW_NORMAL_PRIORITY_CLASS
    except (AttributeError, OSError) as exc:
        print(f"[WARN] Could not lower process priority: {exc}")

import flint
from fractions import Fraction
import math

flint.ctx.prec = 24000

solver_path = os.path.join("mcp", "t2n", "solvers", "yudeng_singularity_sieve.py")
spec = importlib.util.spec_from_file_location("yudeng_singularity_sieve", solver_path)
yudeng_mod = importlib.util.module_from_spec(spec)
sys.modules["yudeng_singularity_sieve"] = yudeng_mod
spec.loader.exec_module(yudeng_mod)
YuDengSingularitySieve = yudeng_mod.YuDengSingularitySieve

def main():
    sieve = YuDengSingularitySieve()
    anomalies = []
    total_scanned = 0
    singularity_count = 0
    
    # Velocity Gradient: 1 to 50, Curvature: 1 to 50
    for vg in range(1, 51):
        for curv in range(1, 51):
            total_scanned += 1
            dens = 10 # fixed density parameter for sweep
            
            print(f"[Scanning Yu Deng Fluid State: VelocityGradient={vg}, Curvature={curv}] | State: Low-Priority Active | Singularities: {singularity_count}", end="\r", flush=True)
            
            mat, det = sieve.sylvester_spectral_matrix(vg, curv, dens)
            if det < 0: # negative determinant indicates instability / singularity blow-up sign flip
                singularity_count += 1
                anomalies.append({
                    "velocity_gradient": vg,
                    "curvature": curv,
                    "density": dens,
                    "determinant": det,
                    "matrix": mat
                })
                
    print() # newline
    
    reports_dir = os.path.join(ROOT, "reports")
    os.makedirs(reports_dir, exist_ok=True)
    
    summary_path = os.path.join(reports_dir, "yudeng_batch_sweep_summary.json")
    summary_data = {
        "sweep": "yudeng_fluid_sweep_1_50",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "precision_bits": 24000,
        "total_configurations_scanned": total_scanned,
        "singularities_detected": singularity_count,
        "anomalies": anomalies,
        "status": "COMPLETED"
    }
    with open(summary_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(summary_data, f, indent=2, ensure_ascii=False)
        f.write("\n")
        
    print(f"YUDENG FLUID SWEEP COMPLETED. Scanned: {total_scanned}, Singularities: {singularity_count}")
    
    # Synchronize workspace ledger via repokeeper
    repokeeper_path = os.path.join(ROOT, "mcp", "t2n", "core", "repokeeper.py")
    if os.path.exists(repokeeper_path):
        result = subprocess.run(
            [sys.executable, repokeeper_path], cwd=ROOT, capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"[REPOKEEPER FAILED] {result.stderr.strip()}")
            raise SystemExit(1)

if __name__ == "__main__":
    main()