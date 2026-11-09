import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import subprocess
import os
import json
import time
import sys

# Windows priority flag for BELOW_NORMAL_PRIORITY_CLASS
BELOW_NORMAL_PRIORITY_CLASS = 0x00004000

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REPORTS_DIR = os.path.join(ROOT, "reports")
MANIFEST_FILE = os.path.join(ROOT, "manifest.json")
LOG_ANOMALY = os.path.join(REPORTS_DIR, "autonomous_pipeline_anomalies.json")

def get_row_count():
    with open(MANIFEST_FILE, "r") as f:
        return len(json.load(f))

def run_cmd(cmd):
    # Running child processes with BELOW_NORMAL_PRIORITY_CLASS
    return subprocess.run(
        cmd,
        cwd=ROOT,
        creationflags=BELOW_NORMAL_PRIORITY_CLASS,
        capture_output=True,
        text=True
    )

def audit_family(family_index):
    # Label and paths
    family_str = f"{family_index:03}"
    json_out = os.path.join(REPORTS_DIR, f"openai_family_{family_str}.json")
    
    # Heuristic parameters (using 2, 1 for now as a default for unknown families)
    # In a full suite, this would parse CONTENTS.md to find the specific parameters
    f_mid, g_mid = "2", "1"
    
    # 1. Run Fresh Ball
    cmd_ball = [
        sys.executable, "mcp/t2n/rh_core/fresh_ball_reinit.py",
        "--f-mid", f_mid, "--g-mid", g_mid, "--coupling", "1/1000000",
        "--out", json_out, "--label", f"OPENAI_FAMILY_{family_str}"
    ]
    res = run_cmd(cmd_ball)
    if res.returncode != 0:
        return False, res.stderr

    # 2. Run Certificate Generator
    # (Simplified for the suite)
    # In a full suite, we'd run the report_certificate_generator.py logic here.
    
    # 3. Run Repokeeper
    cmd_repo = [sys.executable, "mcp/t2n/core/repokeeper.py"]
    res = run_cmd(cmd_repo)
    
    return True, None

def main():
    start_index = 198
    end_index = 373
    
    for i in range(start_index, end_index + 1):
        row_count = get_row_count()
        print(f"[Processing Family {i} / 373] | Core Processes: 2 | Manifest Ledger: {row_count} | State: Low-Priority Background Active")
        
        success, err = audit_family(i)
        
        if not success:
            # Anomaly tunneling
            with open(LOG_ANOMALY, "a") as f:
                json.dump({"family": i, "error": err}, f)
                f.write("\n")
        
        # Low priority delay
        time.sleep(1)

if __name__ == "__main__":
    main()