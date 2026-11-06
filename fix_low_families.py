import importlib.util, json, os, subprocess

ROOT = r"D:\Opencode AI Agent\Math 3.0 Tools"
python_exe = r"C:\Python314\python.exe"
BELOW_NORMAL_PRIORITY_CLASS = 0x00004000

low_missing = []
low_missing += list(range(1, 7))
low_missing += list(range(8, 17))
low_missing += list(range(18, 87))
low_missing += list(range(88, 100))

p = os.path.join(ROOT, "mcp", "t2n", "core", "report_certificate_generator.py")
spec = importlib.util.spec_from_file_location("rcg", p)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

print(f"Low-index certificate repair: {len(low_missing)} families.")

for idx in low_missing:
    idx_str = f"{idx:03d}"
    fn = f"openai_family_{idx_str}.json"
    src = os.path.join(ROOT, "reports", fn)
    if not os.path.exists(src):
        print(f"[{idx_str}] MISSING SOURCE JSON: {fn}")
        continue

    raw = open(src, "rb").read()
    cert = m.build_certificate(
        f"reports/{fn}",
        raw,
        m.summarise_json(json.loads(raw.decode("utf-8"))),
    )
    cert["source_type"] = "json"

    cp = os.path.join(ROOT, "reports", "certificates", f"openai_family_{idx_str}_certificate.json")
    m.write_json(cp, cert)
    ch = m.sha256_file(cp)

    lp = os.path.join(ROOT, "lean", "spec_v4", "certificates", f"OpenaiFamily{idx_str}Certificate.lean")
    m.write_lean_certificate(lp, f"OpenaiFamily{idx_str}", f"reports/{fn}", cert["source_sha256"], ch)
    r = m.compile_lean(lp)
    if r.returncode != 0:
        print(f"[{idx_str}] LEAN FAILED: {r.stderr.strip()}")
        continue

    res_repo = subprocess.run(
        [python_exe, "mcp/t2n/core/repokeeper.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        creationflags=BELOW_NORMAL_PRIORITY_CLASS,
    )
    if res_repo.returncode != 0:
        print(f"[{idx_str}] REPOKEEPER FAILED: {res_repo.stderr.strip()}")
        continue

    print(f"[{idx_str}] verified | Lean exit=0 | reports/{fn} | ledger synced")

print("Low-index repair complete.")
with open(os.path.join(ROOT, "manifest.json"), "r") as mf:
    manifest_data = json.load(mf)
print("Final Master Manifest Rows:", len(manifest_data))
