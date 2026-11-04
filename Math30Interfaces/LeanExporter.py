import os
import sys
from fractions import Fraction

class LeanFormalExporter:
    def __init__(self, workspace_root: str):
        self.root = workspace_root
        self.expected_root = r"D:\Opencode AI Agent\Math 3.0 Tools"
        if self.expected_root.lower() not in self.root.lower(): sys.exit(1)

    def format_to_lean_rational(self, value_str: str) -> str:
        frac = Fraction(value_str)
        return f"({frac.numerator} : ℚ) / {frac.denominator}"

    def export_bounds_theorem(self, output_filename: str, theorem_name: str, constants: dict, bounds: dict) -> bool:
        target_path = os.path.join(self.root, "Math30Interfaces", output_filename)
        lean_lines = ["import Mathlib.Tactic.NormNum", "", f"theorem {theorem_name} :"]
        assertions = []
        for key, bound_val in bounds.items():
            const_val = constants.get(key, key)
            assertions.append(
                f"{self.format_to_lean_rational(str(const_val))} ≤ {self.format_to_lean_rational(str(bound_val))}"
            )
        joined = " ∧ ".join(assertions) if assertions else "True"
        lean_lines.append(f"  {joined} :=")
        lean_lines.append("by")
        # ponytail: single assertion closes with norm_num; conjunction via constructor split.
        if len(assertions) <= 1:
            lean_lines.append("  norm_num")
        else:
            lean_lines.append("  refine ⟨?_, ?_⟩ <;> norm_num")
        lean_lines.append("")
        try:
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            with open(target_path, "w", encoding="utf-8") as f: f.write("\n".join(lean_lines))
            return True
        except Exception: return False