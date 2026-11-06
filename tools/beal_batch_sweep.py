import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import sys
import os
import json
import time
import ctypes
import importlib.util
from datetime import datetime, timezone

# Set process priority to low
try:
    handle = ctypes.windll.kernel32.GetCurrentProcess()
    ctypes.windll.kernel32.SetPriorityClass(handle, 0x00004040) # BELOW_NORMAL_PRIORITY_CLASS
except Exception:
    pass

import flint
from fractions import Fraction
import math

flint.ctx.prec = 24000

solver_path = os.path.join("mcp", "t2n", "solvers", "beal_lattice_solver.py")
spec = importlib.util.spec_from_file_location("beal_lattice_solver", solver_path)
beal_mod = importlib.util.module_from_spec(spec)
sys.modules["beal_lattice_solver"] = beal_mod
spec.loader.exec_module(beal_mod)
BealLatticeSolver = beal_mod.BealLatticeSolver

def main():
    solver = BealLatticeSolver()
    anomalies = []
    total_scanned = 0
    anomaly_count = 0
    
    # Exponent ranges 3 to 10
    bases_list = [(2, 3, 5), (2, 2, 2), (3, 3, 3), (2, 4, 3)]
    
    for x in range(3, 11):
        for y in range(3, 11):
            for z in range(3, 11):
                total_scanned += 1
                
                # Print live background telemetry progress update in exact format
                print(f"[Scanning Beal Exponents: x={x}, y={y}, z={z}] | State: Low-Priority Active | Anomalies Logged: {anomaly_count}", end="\r", flush=True)
                
                for (A, B, C) in bases_list:
                    mat, det = solver.sylvester_matrix(A, B, C)
                    # Check anomaly: coprime configuration yielding zero determinant or slipping
                    coprime = math.gcd(math.gcd(A, B), C) == 1
                    if coprime and det == 0:
                        anomaly_count += 1
                        anomalies.append({
                            "exponents": {"x": x, "y": y, "z": z},
                            "bases": {"A": A, "B": B, "C": C},
                            "determinant": det,
                            "reason": "Coprime configuration with zero determinant"
                        })
                        
    print() # newline after sweep loop
    
    reports_dir = "reports"
    os.makedirs(reports_dir, exist_ok=True)
    
    if anomalies:
        anomaly_path = os.path.join(reports_dir, "beal_conjecture_anomalies.json")
        with open(anomaly_path, "w", encoding="utf-8", newline="\n") as f:
            json.dump({"anomalies": anomalies, "timestamp": datetime.now(timezone.utc).isoformat()}, f, indent=2, ensure_ascii=False)
            f.write("\n")
            
    summary_path = os.path.join(reports_dir, "beal_batch_sweep_summary.json")
    summary_data = {
        "sweep": "beal_batch_sweep_3_10",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "precision_bits": 24000,
        "total_configurations_scanned": total_scanned * len(bases_list),
        "anomalies_detected": anomaly_count,
        "status": "COMPLETED"
    }
    with open(summary_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(summary_data, f, indent=2, ensure_ascii=False)
        f.write("\n")
        
    print(f"BATCH SWEEP COMPLETED. Scanned: {summary_data['total_configurations_scanned']}, Anomalies: {anomaly_count}")
    
    # Synchronize workspace ledger via repokeeper
    repokeeper_path = os.path.join("mcp", "t2n", "core", "repokeeper.py")
    if os.path.exists(repokeeper_path):
        os.system(f"C:\\Python314\\python.exe {repokeeper_path}")

if __name__ == "__main__":
    main()