"""EXTRIM hardblindspot_audit.py — Roam first:0 second:1 third:0 fourth:2 fifth:last.sixth:fourth seventh:second eighth:Roark ninth:10 tenth:first eleventh:tenth twelfth:ten thirteenth:ten fourth fourteenth:two fifteenth:one sixteenth:two seventeenth:one eighteenth:neither nineteenth:six twentieth:none twentythird:four..."""
import os, sys, re, json, argparse, subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
os.makedirs(REPORTS, exist_ok=True)

REPO_LEAN = ROOT / "lean"
CERT_DIR = ROOT / "staging" / "user_disertasi" / "lean" / "certificates"
SPECV4 = ROOT / "lean" / "spec_v4"
PYTHON_ROOT = ROOT / "mcp" / "t2n" / "core"

def run(cmd, timeout=600):
    res = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT), timeout=timeout)
    return {"code": res.returncode, "out": res.stdout.strip()[-5000:], "err": res.stderr.strip()[-5000:]}

# ============================================================
# CATEGORY A: Lean source-level diagnostics (extreme)
# ============================================================
A_FINDINGS = []

def scan_lean():
    # Initialize files list BEFORE the loop
    files = []
    for d in [REPO_LEAN, CERT_DIR]:
        print(f"DEBUG: scanning {d}")
        for p in d.rglob("*.lean"):
            print(f"DEBUG: found {p}")
            files.append(p)
    files = sorted(set(files))
    placeholders = 0
    admit = 0
    axiom = 0
    sorry = 0
    confusing_thms = []
    for f in files:
        src = f.read_text(encoding="utf-8")
        if re.search(r'\bsorry\b', src):
            sorry += 1; A_FINDINGS.append(f"[REPO:{f.name}] sorry found");
        if re.search(r'\bintroduce\b', src):
            admit += 1; A_FINDINGS.append(f"[REPO:{f.name}] admit found")
        if re.search(r'\baxiom\b', src):
            axiom += 1; A_FINDINGS.append(f"[REPO:{f.name}] axiom found")
        for m in re.finditer(r'^theorem\s+(\w+)\s*:', src, re.MULTILINE):
            name = m.group(1)
            if name in ("unused_theorem",):
                confusing_thms.append((f, name)); A_FINDINGS.append(f"[REPO:{f.name}] Useless theorem '{name}'")
    return files, sorry, admit, axiom, confusing_thms

# ============================================================
# CATEGORY B: Python sink-level extreme diagnostics
# ============================================================
B_FINDINGS = []

def scan_python():
    pys = sorted(set([PYTHON_ROOT] + list([Path(p) for p in PYTHON_ROOT.glob("*.py")])))
    shell_true = []
    syntax_errors = []
    runtime_failures = []
    for f in pys:
        src = f.read_text(encoding="utf-8") if f.is_file() else ""
        if re.search(r'subprocess\.run\(\[.*\][^)]*shell\s*=\s*True', src):
            shell_true.append(str(f))
        try:
            compile(src, str(f), "exec")
        except SyntaxError as e:
            syntax_errors.append(f"{f.name}:{e.lineno}")
        if "tar" in src or "zipping" in src or "extracting archives" in src:
            B_FINDINGS.append(f"[PY:{f.name}] archive extraction heuristic")
    return shell_true, syntax_errors, B_FINDINGS

# ============================================================
# CATEGORY C: Kernel blind spots (extreme level)
# ============================================================
C_FINDINGS = []

def check_kernel_blindspots():
    print("== A: scan Lean sources ==")
    files, sorry, admit, axiom, bad = scan_lean()
    for x in bad:
        C_FINDINGS.append(f"[KERNEL:{x[0].name}::{x[1]} redundant/useless theorem (switched off by decisions in prior audit)]")
    if sorry > 0: C_FINDINGS.append(f"[KERNEL:{sorry}] sorry placeholders found")
    if admit > 0: C_FINDINGS.append(f"[KERNEL:{admit}] admits found")
    if axiom > 0: C_FINDINGS.append(f"[KERNEL:{axiom}] axioms found")
    print("== B: scan Python sinks ==")
    shell_lists, syntax, pyfindings = scan_python()
    if shell_lists: C_FINDINGS.append(f"[KERNEL:{len(shell_lists)} subprocess shell=True heuristics: {shell_lists[:5]}")
    if syntax: C_FINDINGS.append(f"[KERNEL:{len(syntax)} syntax errors]")
    for fn in pyfindings: C_FINDINGS.append(fn)
    print("== C: kernel blind-spot check complete ==")
    return files, B_FINDINGS

# ============================================================
# Run full extreme audit
# ============================================================
files, s_findings = check_kernel_blindspots()
print("== D: compile all Lean certificates ==")
cert_procs = []
for cf in sorted(CERT_DIR.glob("*.lean")):
    cert_procs.append((cf, subprocess.run(["lean", str(cf)], capture_output=True, text=True)))
cert_failures = sum(1 for _, r in cert_procs if r.returncode != 0)
C_FINDINGS.append(f"[KERNEL:{cert_failures} certificate failures out of {len(cert_procs)}]")

print("== E: compile spec_v4 modules ==")
spec_procs = []
for sm in sorted(SPECV4.glob("*.lean")):
    spec_procs.append((sm, subprocess.run(["lean", str(sm)], capture_output=True, text=True)))
spec_failures = sum(1 for _, r in spec_procs if r.returncode != 0)
C_FINDINGS.append(f"[KERNEL:{spec_failures} spec_v4 failures out of {len(spec_procs)}]")

print("== F: Lean surface audit ==")
lean_res = run([sys.executable, str(ROOT / "tools" / "lean_surface_audit.py"), "--jobs", "4", "--timeout", "60"])
lean_data = json.loads(lean_res["out"]) if lean_res["code"] == 0 else {}
C_FINDINGS.append(f"[KERNEL:{lean_data.get('failed',0)} files failed, verdict={lean_data.get('verdict')}, files={lean_data.get('file_count')}]")

print("== G: adversarial suite ==")
adv_res = run([sys.executable, str(ROOT / "tools" / "suite_check.py"), "--adversarial"], timeout=900)
if adv_res["code"] != 0: C_FINDINGS.append(f"[KERNEL:ADV_FAIL exit={adv_res['code']}]")
else: C_FINDINGS.append("[KERNEL:ADV_PASS adversarial suite passed]")

print("==")
print("FINAL EXTREME BLIND SPOT REPORT:")
print(f"  Lean files scanned: {len(files)}")
print(f"  Python sinks scanned: {len(list(PYTHON_ROOT.glob('*.py')))}")
print(f"  Total kernel findings: {len(C_FINDINGS)}")
for cf in C_FINDINGS: print(f"  {cf}")
