import importlib.util, json, os
p = r'D:\Opencode AI Agent\Math 3.0 Tools\mcp\t2n\core\report_certificate_generator.py'
spec = importlib.util.spec_from_file_location('rcg', p)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
root = m.ROOT
for idx in [209, 210]:
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
    print(f'Family {idx} exit {r.returncode}')