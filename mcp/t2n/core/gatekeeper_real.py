#!/usr/bin/env python3
"""Real gatekeeper. Runs actual Z3 on ```smt2 fences in a source file.
Prose specs (no SMT fence) get a structural audit instead. No hardcoded verdicts.
Usage: python mcp/t2n/core/gatekeeper_real.py <file> [<file> ...]
"""
import json
import re
import shutil
import sys
from pathlib import Path

import psutil
import z3

FENCE = re.compile(r"```smt2\s*\n(.*?)```", re.S)
INLINE = re.compile(r"(\(set-logic.*?\(check-sat\))", re.S)
REGISTRY = Path("reports/user_certified_blueprints.json")
QUARANTINE = Path("staging/user_disertasi/error_learning_lab")


def _expand(m):
    from decimal import Decimal
    return format(Decimal(m.group(0)), "f") + (".0" if "." not in format(Decimal(m.group(0)), "f") else "")


SCI = re.compile(r"(?<![\d.])(\d+)[eE](\d+)")


def z3_run(script):
    # SMT-LIB2 parser here rejects exponent notation; expand to plain decimals.
    fixed, n = SCI.subn(_expand, script)
    # PDF dumps sometimes embed SMT as TS string-array literals: '...',
    if "'" in fixed:
        fixed = "\n".join(
            ln.strip().strip("'\",").strip()
            for ln in fixed.splitlines()
            if ln.strip().strip("'\",").strip()
        )
    s = z3.Solver()
    s.set("timeout", 20000)
    try:
        s.from_string(fixed)
    except z3.Z3Exception as e:
        return {"error": str(e), "normalized": n}
    return {"result": str(s.check()), "normalized": n}


def audit(path):
    text = path.read_text(encoding="utf-8", errors="ignore")
    checks = {"bytes": len(text.encode("utf-8"))}
    blocks = FENCE.findall(text)
    if not blocks:
        blocks = INLINE.findall(text)

    if blocks:
        runs = [z3_run(b) for b in blocks]
        errors = [r["error"] for r in runs if "error" in r]
        results = [r["result"] for r in runs if "result" in r]
        checks["smt_blocks"] = len(blocks)
        checks["parseable_blocks"] = len(results)
        checks["z3_results"] = results
        checks["unparseable_blocks"] = len(errors)
        checks["z3_errors"] = errors
        checks["smt_normalized_literals"] = sum(r.get("normalized", 0) for r in runs)
        claims_unsat = bool(re.search(r"(?:MACHINE RESULT|HASIL MESIN|RESULT):\s*unsat", text, re.I))
        checks["source_claims_unsat"] = claims_unsat
        # unsat-claims must be refuted-unsat; everything else is a model-existence claim.
        ok = results and (all(r == "unsat" for r in results) if claims_unsat else all(r == "sat" for r in results))
        checks["claim_confirmed"] = bool(ok)
        status = "PASS" if ok else "FAIL"
        kind = "NO_PARSEABLE_SMT" if not results else ("Z3_UNSAT_CONFIRMED" if claims_unsat else "Z3_MODEL_CONFIRMED")
    elif "<immutable_axioms>" in text:
        # every closing tag must have a preceding open; prose mentions are harmless.
        opened, unclosed = set(), []
        for m in re.finditer(r"</?([a-z][a-z0-9_]{2,})>", text):
            name = m.group(1)
            if m.group(0).startswith("</"):
                if name not in opened:
                    unclosed.append(name)
            else:
                opened.add(name)
        checks["has_immutable_axioms"] = "</immutable_axioms>" in text
        checks["unclosed_tags"] = sorted(set(unclosed))
        checks["balanced_tags"] = not unclosed
        checks["axiom_count"] = len(re.findall(r"^\s*\d+\.\s", text, re.M))
        checks["non_empty"] = len(text.strip()) > 0
        ok = checks["has_immutable_axioms"] and checks["balanced_tags"] and checks["non_empty"] and checks["axiom_count"] >= 3
        status = "PASS" if ok else "FAIL"
        kind = "STRUCTURE_PASS"
    else:
        checks["reason"] = "no ```smt2 fence, nothing machine-checkable"
        status = "FAIL"
        kind = "NO_SMT2_BLOCK"

    return {"target": path.stem, "source": str(path), "status": status, "kind": kind, "checks": checks}


def main(paths):
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    records = json.loads(REGISTRY.read_text(encoding="utf-8")) if REGISTRY.exists() else []
    failed = 0

    for p in map(Path, paths):
        r = audit(p)
        print(f"[{r['status']}] {r['target']} :: {r['kind']} :: {json.dumps(r['checks'])}")
        if r["status"] == "FAIL":
            failed += 1
            QUARANTINE.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, QUARANTINE / p.name)
        r.pop("target")
        key = Path(p).stem
        records = [x for x in records if x.get("theorem") != key]
        records.append({"theorem": key, **r})

    REGISTRY.write_text(json.dumps(records, indent=2), encoding="utf-8")
    print(f"[GATEKEEPER] {len(paths) - failed}/{len(list(paths))} passed. Registry rows: {len(records)}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
