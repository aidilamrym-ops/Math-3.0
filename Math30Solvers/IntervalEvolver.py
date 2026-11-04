import os
import json
import sys

try:
    import flint
    from Math30Kernel.IntervalMatrices import IntervalMatrixBuilder
    from Math30Solvers.IntervalLDLT import IntervalLDLTSolver, ResolutionAlarm, UndeterminedPivotException
    from Math30Interfaces.LeanExporter import LeanFormalExporter
except ImportError as ie:
    print(f"FATAL import error in IntervalEvolver: {ie}")
    sys.exit(2)

class IntervalEvolver:
    """
    Recursive Self-Improvement (RSI) adaptive evolver.
    Observes failed world traces, mutates precision and widening policies,
    and re-tests until anomalies are strictly contained.
    """
    def __init__(self, workspace_root: str):
        self.root = workspace_root
        self.expected_root = r"D:\Opencode AI Agent\Math 3.0 Tools"
        if self.expected_root.lower() not in self.root.lower():
            sys.exit(1)
        self.trace_path = os.path.join(self.root, "failed_world_trace.json")
        self.config_path = os.path.join(self.root, "runtime_config.json")

    def record_failed_trace(self, anomaly_type: str, context: dict):
        trace = {
            "anomaly_type": anomaly_type,
            "context": context,
            "timestamp_generation": context.get("generation", 0)
        }
        with open(self.trace_path, "w", encoding="utf-8") as f:
            json.dump(trace, f, indent=2)
        print(f"[EVOLVER] Failed world trace recorded for {anomaly_type}.")

    def evolve(self, current_config: dict) -> dict:
        print("[EVOLVER] Initiating Discovery Optimization Ramp...")
        prec = current_config.get("precision_bits", 6000)
        jitter = current_config.get("jitter", 0.0)
        gen = current_config.get("generation", 0) + 1

        new_prec = min(prec * 2, 96000)
        new_jitter = jitter + 0.001

        mutated_config = {
            "precision_bits": new_prec,
            "jitter": new_jitter,
            "constants": current_config.get("constants", {"min_val": "1.32e-102"}),
            "max_generations": current_config.get("max_generations", 5),
            "generation": gen
        }

        print(f"[EVOLVER] Mutating policy: precision_bits={new_prec}, jitter={new_jitter}, generation={gen}")
        
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(mutated_config, f, indent=2)

        print("[EVOLVER] Policy updated and frozen. Re-testing container integrity...")
        return mutated_config
