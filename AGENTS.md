# AGENTS.md — Math 3.0 Sovereign Engineering & Karpathy Discipline

**Tradeoff:** Bias toward deterministic verification, epistemic honesty, and caution over speed.

## 1. Think Before Coding (Explicit Scope & Zero Fabrication)
- **Never assume or fabricate.** Every claim of `PASS` or `VERIFIED` must be backed by a real terminal exit code (`0`), `#print axioms` output, and a JSON receipt under `reports/`.
- **Surface epistemic boundaries immediately:** Classify every mathematical artifact strictly as `FORMAL_GENERAL_THEOREM`, `FORMAL_FINITE_THEOREM`, or `OPEN`. Never present bounded lattice models as unconditional continuum proofs.
- **Stop when unclear or failing:** If a Lean tactic, interval bound, or audit gate fails, report `FAIL` honestly, archive the flawed draft in `reports/flawed_artifacts/`, and rebuild from first principles.

## 2. Simplicity First (Anti-Bloat & Zero-Trust Lock)
- **Minimum code that solves the problem.** Replace heavy, high-heartbeat tactics with compact, decidable arithmetic (`omega`, `linarith`, `norm_num`) and exact `ℚ` / `Fin N` structures.
- **Zero trust tokens allowed:** Never use `sorry`, `sorryAx`, `admit`, `axiom`, `constant`, `opaque`, `partial def`, `native_decide`, `implemented_by`, or `extern`. Permitted Lean axioms: `[propext, Classical.choice, Quot.sound]` only.
- **Zero float coercion & zero hardcoded receipts:** All numerical validators must compute real `flint.arb` / `flint.arb_mat` intervals and fail closed (`exit != 0`) if `flint` is missing or a zero-straddle occurs.

## 3. Surgical Changes (Ledger & Worktree Hygiene)
- **Touch only target files in the active queue.** Do not alter already-sealed certificates (`manifest.json`) unless fixing a verified soundness bug.
- **Sequential execution (`--workers 1`):** Process and verify at most 2 files per checkpoint before halting for review.
- **Clean up transient artifacts:** Never leave `.log` or `.jsonl` temporary files tracked in Git; always run `python tools/seal_pipeline.py` and `python tools/seal_pipeline.py --check` before committing.

## 4. Goal-Driven Execution (Machine-Checked Verification Loops)
Transform every task into an executable, fail-closed verification loop:
1. **Lean 4 Certificate** → `lake env lean <file>.lean` (`exit 0`, 0 warnings) + `#print axioms` clean.
2. **Substantiveness & Mutation** → `python tools/omega_audit/substantiveness_gate.py` (`0 surviving mutants`, `HIGH=0`, `MEDIUM=0`, `LOW=0`).
3. **Flint Validator & AST Check** → `python tools/audit_hardcoded_nodes.py` (`0 findings`) + negative controls (`indefinite` & `singular` fail-closed).
4. **README & Surface Sync** → `python tools/readme_lean_audit.py` + `python tools/readme_theorem_audit.py` (`0 missing`) + `python tools/seal_pipeline.py`.
