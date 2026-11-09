import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import subprocess, os, json, time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
python_exe = sys.executable
BELOW_NORMAL_PRIORITY_CLASS = 0x00004000

def run(cmd):
    return subprocess.run(
        cmd,
        cwd=ROOT,
        capture_output=True,
        text=True,
        creationflags=BELOW_NORMAL_PRIORITY_CLASS,
    )

missing = []
missing += list(range(1, 7))        # Range A: 001-006
missing += list(range(8, 17))       # Range B: 008-016
missing += list(range(18, 87))      # Range C: 018-086
missing += list(range(88, 102))     # Range D: 088-101
missing += list(range(103, 159))    # Range E: 103-158
missing += list(range(160, 197))    # Range F: 160-196

print(f"Recovery sweep initialized: {len(missing)} missing families.")
print("Priority: BELOW_NORMAL_PRIORITY_CLASS | Sequential single-worker loop.")

for idx in missing:
    f_mid = str(idx * 2 + 1)
    g_mid = str(idx + 5)
    json_out = os.path.join(ROOT, "reports", f"openai_family_{idx:03}.json")

    cmd_ball = [
        python_exe, "mcp/t2n/rh_core/fresh_ball_reinit.py",
        "--f-mid", f_mid, "--g-mid", g_mid, "--coupling", "1/1000000",
        "--out", json_out, "--label", f"OPENAI_FAMILY_{idx:03}",
    ]
    res = run(cmd_ball)
    if res.returncode != 0:
        print(f"Family {idx:03} BALL FAILED: {res.stderr.strip()}")
        continue

    script_content = '''import importlib.util, json, os
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mcp', 't2n', 'core', 'report_certificate_generator.py')
spec = importlib.util.spec_from_file_location('rcg', p)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
root = m.ROOT
idx = %d
fn = f'openai_family_{idx}.json'
src = os.path.join(root, 'reports', fn)
raw = open(src, 'rb').read()
cert = m.build_certificate(f'reports/{fn}', raw, m.summarise_json(json.loads(raw.decode('utf-8'))))
cert['source_type'] = 'json'
cp = os.path.join(root, 'reports', 'certificates', f'openai_family_{idx}_certificate.json')
m.write_json(cp, cert)
ch = m.sha256_file(cp)
lp = os.path.join(root, 'lean', 'spec_v4', 'certificates', f'OpenaiFamily{idx}Certificate.lean')
m.write_lean_certificate(lp, f'OpenaiFamily{idx}', f'reports/{fn}', cert['source_sha256'], ch)
r = m.compile_lean(lp)
if r.returncode != 0:
    print(f'Lean compile failed for {idx}: {r.stderr}')
    exit(1)
''' % idx

    script_path = os.path.join(ROOT, f"temp_{idx}.py")
    with open(script_path, "w") as sf:
        sf.write(script_content)

    res_cert = run([python_exe, script_path])
    os.remove(script_path)
    if res_cert.returncode != 0:
        print(f"Family {idx:03} CERT FAILED: {res_cert.stderr.strip()}")
        continue

    res_repo = run([python_exe, "mcp/t2n/core/repokeeper.py"])
    if res_repo.returncode != 0:
        print(f"Family {idx:03} REPOKEEPER FAILED: {res_repo.stderr.strip()}")
        continue

    print(f"[{idx:03}] verified | Lean exit=0 | reports/openai_family_{idx:03}.json | ledger synced")

print("Recovery sweep complete.")
with open(os.path.join(ROOT, "manifest.json"), "r") as mf:
    manifest_data = json.load(mf)
print("Final Master Manifest Rows:", len(manifest_data))