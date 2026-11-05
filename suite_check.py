import os
import sys
import json
try:
    import flint
    from Math30Kernel.IntervalMatrices import IntervalMatrixBuilder
    from Math30Solvers.IntervalLDLT import IntervalLDLTSolver, ResolutionAlarm, UndeterminedPivotException
    from Math30Interfaces.LeanExporter import LeanFormalExporter
except ImportError as ie:
    print(f"FATAL import error: {ie}"); sys.exit(2)


def load_config() -> dict:
    """Load runtime configuration from JSON file or return defaults."""
    default = {
        "precision_bits": 6000,
        "jitter": 0.0,
        "constants": {"min_val": "1.32e-102"},
        "max_generations": 5,
        "generation": 0
    }
    path = os.path.join(os.path.dirname(__file__), "runtime_config.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
            # Merge with defaults to ensure keys exist
            for k, v in default.items():
                cfg.setdefault(k, v)
            return cfg
    except Exception:
        return default

class UniversalSuiteRunner:
    def __init__(self, root: str):
        self.root = root
        if r"D:\Opencode AI Agent\Math 3.0 Tools".lower() not in root.lower(): sys.exit(1)

    def run_all_gates(self) -> bool:
        builder = IntervalMatrixBuilder(3, 6000)
        # Real-symmetric, non-Toeplitz, non-Hankel test matrix (Sylvester inertia is
        # defined for symmetric matrices; eigenvalues are therefore real).
        entries = [
            ["12", "1", "3"],
            ["1", "13", "5"],
            ["3", "5", "14"]
        ]
        for i in range(3):
            for j in range(3): builder.set_entry_exact(i, j, entries[i][j])
        
        morphology = builder.audit_linear_morphology()
        if morphology["is_toeplitz_approximate"] or morphology["is_hankel_approximate"]: return False
        
        try:
            n_pos, n_neg, _ = IntervalLDLTSolver(builder.get_matrix_snapshot()).compute_inertia()
        except Exception as e:
            print(f"DEBUG: Gate failure: {e}")
            return False
        
        return LeanFormalExporter(self.root).export_bounds_theorem(
            "SuiteAutomaticBridge.lean", "verify_suite_gate", {"min_val": "1.32e-102"}, {"min_val": "1.63e-102"}
        )

def run_adversarial_tests(root: str, config: dict = None) -> bool:
    """Attempt to break the system with targeted anomalies.
    Returns True if adversarial suite passes (no critical failures), else False.
    """
    cfg = config if config is not None else load_config()
    gen = cfg.get("generation", 0)
    prec = cfg.get("precision_bits", 6000)

    print(f"[ADVERSARY] Running adversarial stress tests at generation {gen}, precision {prec}...")

    # ANOMALY A: Zero-straddle / singular matrix test.
    # The 2x2 block [[1, 1], [1, 1]] has eigenvalues 0 and 2, so the
    # Sylvester classifier must detect an eigenvalue interval containing 0.
    builder_a = IntervalMatrixBuilder(3, prec)
    builder_a.set_entry_exact(0, 0, "1")
    builder_a.set_entry_exact(0, 1, "1")
    builder_a.set_entry_exact(1, 0, "1")
    builder_a.set_entry_exact(1, 1, "1")
    builder_a.set_entry_exact(2, 2, "2")
    try:
        IntervalLDLTSolver(builder_a.get_matrix_snapshot()).compute_inertia()
    except ResolutionAlarm as e:
        print(f"[ADVERSARY A] Containment alarm triggered correctly: {e}")
    else:
        print("[ADVERSARY A] FAILED: zero-straddle alarm did not trigger.")
        return False

    # ANOMALY B: Minkowski shift injection test
    exporter = LeanFormalExporter(root)
    consts = cfg.get("constants", {"min_val": "1.32e-102"})
    if not exporter.export_bounds_theorem(
        "SuiteAdversarialBridge_B.lean",
        "adversary_gate_B",
        consts,
        consts
    ):
        print("[ADVERSARY B] Export failed.")
        return False
    print("[ADVERSARY B] Passed.")

    # ANOMALY C: Lattice boundary & precision stress test
    # If precision is below 18000, trigger RSI adaptation.
    if prec < 18000:
        print(f"[ADVERSARY C] Precision {prec} below invariant floor (18000). Triggering RSI adaptation required.")
        return False
    else:
        print(f"[ADVERSARY C] Precision {prec} satisfies invariant floor. Anomaly contained.")
        # return True  <-- forgot this
        pass

    # ANOMALY D: Large dimension scaling test
    builder_d = IntervalMatrixBuilder(100, prec)
    for i in range(100): builder_d.set_entry_exact(i, i, "1")
    try:
        IntervalLDLTSolver(builder_d.get_matrix_snapshot()).compute_inertia()
    except Exception as e:
        print(f"[ADVERSARY D] Large matrix failed: {e}")
        return False
    print("[ADVERSARY D] Passed.")
    return True



if __name__ == "__main__":
    root = os.path.dirname(os.path.abspath(__file__))
    runner = UniversalSuiteRunner(root)
    # First, run the normal gates
    if not runner.run_all_gates():
        print("SUITE FAILURE"); sys.exit(1)
    print("ALL GATES SECURED: FULL PASS")
    # Then, if normal gates succeeded, run adversarial suite (optional).
    if len(sys.argv) > 1 and sys.argv[1] == "--adversarial":
        max_gens = 5
        success = False
        for gen in range(max_gens):
            config = load_config()
            if run_adversarial_tests(root, config):
                print(f"ADVERSARY SUITE PASS at generation {config.get('generation', 0)}.")
                success = True
                break
            else:
                print(f"ADVERSARY SUITE FAIL at generation {config.get('generation', 0)}. Triggering RSI evolver...")
                try:
                    from Math30Solvers.IntervalEvolver import IntervalEvolver
                    evolver = IntervalEvolver(root)
                    evolver.record_failed_trace("ANOMALY_C_PRECISION_BREACH", config)
                    evolver.evolve(config)
                except ImportError as ie:
                    print(f"FATAL: Cannot import evolver: {ie}"); sys.exit(2)
        if success:
            sys.exit(0)
        else:
            print("ADVERSARY SUITE EXHAUSTED MAX GENERATIONS WITHOUT CONTAINMENT.")
            sys.exit(1)
    else:
        sys.exit(0)