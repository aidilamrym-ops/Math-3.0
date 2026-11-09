import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import subprocess, os, json

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
python_exe = sys.executable

for idx in range(331, 374):
    f_mid = str(idx * 2 + 1)
    g_mid = str(idx + 5)
    json_out = os.path.join(ROOT, "reports", f"openai_family_{idx:03}.json")
    
    cmd_ball = [
        python_exe, "mcp/t2n/rh_core/fresh_ball_reinit.py",
        "--f-mid", f_mid, "--g-mid", g_mid, "--coupling", "1/1000000",
        "--out", json_out, "--label", f"OPENAI_FAMILY_{idx:03}"
    ]
    res = subprocess.run(cmd_ball, cwd=ROOT, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Family {idx} ball failed:", res.stderr)
        break

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
    
    res_cert = subprocess.run([python_exe, script_path], cwd=ROOT, capture_output=True, text=True)
    os.remove(script_path)
    if res_cert.returncode != 0:
        print(f"Family {idx} cert failed:", res_cert.stderr)
        break

    res_repo = subprocess.run([python_exe, "mcp/t2n/core/repokeeper.py"], cwd=ROOT, capture_output=True, text=True)
    if res_repo.returncode != 0:
        print(f"Family {idx} repokeeper failed:", res_repo.stderr)
        break
    
    print(f"Successfully processed and verified Family {idx}")

print("Batch 331-373 complete!")
with open(os.path.join(ROOT, "manifest.json"), "r") as mf:
    manifest_data = json.load(mf)
print("Manifest rows:", len(manifest_data))