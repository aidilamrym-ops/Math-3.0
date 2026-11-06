import os
import shutil
import sys

TARGET_FILES = [
    "z3_tribunal.py",
    "audit_hardcoded_nodes.py",
    "autonomous_suite.py",
    "beal_batch_sweep.py",
    "fix_low_families.py",
    "lte_spectral_validator.py",
    "meta_blindspot_hunter.py",
    "newton_box_validator.py",
    "phase7_stress_test.py",
    "reports_to_lean.py",
    "rigorous_adversarial_suite.py",
    "run_regression_tests.py",
    "suite_check.py",
    "yudeng_fluid_sweep.py",
    "batch_missing_blocks.py",
    "batch_331_373.py",
    "batch_291_330.py",
    "batch_251_290.py",
    "batch_211_250.py",
    "generate_cert_1.py",
    "generate_cert_2.py",
    "generate_cert_3.py",
    "generate_cert_4.py",
    "generate_cert_5.py",
    "gen_certs_204_205.py",
    "gen_certs_206_207.py",
    "gen_certs_209_210.py"
]

ROOT = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.join(ROOT, "tools")
os.makedirs(TOOLS_DIR, exist_ok=True)

print("[REFACTOR] Relocating utility scripts to tools/...")

for filename in TARGET_FILES:
    src = os.path.join(ROOT, filename)
    dst = os.path.join(TOOLS_DIR, filename)
    if os.path.exists(src):
        with open(src, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        
        # Adjust path checks and roots if needed
        # Inject sys.path adjustment for parent directory module imports
        sys_path_inject = "import sys, os\nsys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))\n"
        if "sys.path.insert" not in content and "sys.path.append" not in content:
            # Insert after initial imports or at top
            lines = content.splitlines()
            insert_idx = 0
            for i, line in enumerate(lines):
                if line.startswith("import ") or line.startswith("from "):
                    insert_idx = i
                    break
            lines.insert(insert_idx, sys_path_inject.strip())
            content = "\n".join(lines)

        # Adjust runtime_config.json path if referenced locally
        content = content.replace('os.path.dirname(__file__), "runtime_config.json"', 'os.path.join(os.path.dirname(__file__), "../runtime_config.json")')
        content = content.replace('os.path.dirname(__file__), "manifest.json"', 'os.path.join(os.path.dirname(__file__), "../manifest.json")')

        with open(dst, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
        os.remove(src)
        print(f"  -> Moved & updated: {filename} -> tools/{filename}")
    else:
        print(f"  -> Warning: {filename} not found in root.")

print("[REFACTOR] Relocation complete.")
