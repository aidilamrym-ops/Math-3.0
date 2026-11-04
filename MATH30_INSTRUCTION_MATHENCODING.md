# Math 3.0 Operational Instruction
## Section 11: MathEncoding Protocols & Absolute Workspace Confinement Rules

---

## 1. Absolute Workspace Confinement Directive

To prevent cross-project contamination, variable leakage, and dependency pollution, **Math 3.0 Tools** must operate in a state of absolute system isolation.

*   **Fixed Root Directory:** The active workspace is strictly restricted to:
    `D:\Opencode AI Agent\Math 3.0 Tools`
*   **Isolation Laws:**
    1.  No files, scripts, configurations, or temporary execution logs from external or older repositories may be mixed into this directory.
    2.  All absolute path pointers utilized inside script definitions, `opencode.jsonc`, or testing matrices must resolve relative to this fixed root.
    3.  The agent is forbidden from scanning, reading, or writing to any directory outside this localized tree structure.

---

## 2. Universal Code Language Rule

*   **Absolute Constraint:** **ALL code blocks, scripts, modules, configuration files (`.json`, `.jsonc`), variables, and documentation authored for Math 3.0 Tools MUST be written exclusively in ENGLISH.**
*   *Rationale:* This guarantees global portability, standardized type-definitions, and exact syntax translation during automated cross-compilation blocks to the `Lean 4` kernel and `Z3 SMT` tribunals. Any non-English string literal or naming convention inside the tools directory will trigger an immediate system verification failure.

---

## 3. The MathEncoding Specification (Zero-Fudging Syntax Layer)

Mathematical expressions inside Math 3.0 are never handled as approximate floating-point representations or plain narrative text. They are encoded via a strict symbolic protocol called **MathEncoding**. Every tool component must enforce this syntax layer to maintain perfect mathematical containment.

### 3.1 Interval Arithmetic Serialization Format
To ensure zero string-to-binary round-trip drift, all interval boundaries (`Arb` / `Acb` balls) serialized into JSON/JSONL artifacts must be formatted as precise decimal or fractional strings enclosed in explicit bounds. Floating-point types are strictly banned from storage:

```json
{
  "matrix_dimension": 201,
  "eigenvalue_index": 0,
  "enclosure": {
    "midpoint": "1.32105051975174632728899314595e-102",
    "radius": "1.63092656759474834688247443633e-104"
  },
  "imaginary_leak": {
    "midpoint": "0",
    "radius": "0"
  }
}
```

### 3.2 LaTeX & Matplotlib Mathematical Token Guard
For any internal rendering blocks, equation generating scripts, or documentation exports, canonical and strict LaTeX syntax is non-negotiable:
*   Use `mathtext` raw strings in Python (e.g., `r'$\alpha \geq \beta$'`).
*   Only use canonical symbols: `\leq` and `\geq` (Do NOT use shortcuts like `\le` or `\ge`).
*   Ample structural macros like `\implies` are barred from basic SMT-LIB2 conversions; constraints must be decomposed into primitive non-linear real arithmetic inequalities (`QF_NRA`).

### 3.3 Strict Containment Verification Overrides
When verifying real-analysis zero-locations or continuous vector fields, equality tests (`==`) are banned. The MathEncoding engine resolves containment using strict logical tracking operators:

| Invariant Relation | Symbolic MathEncoding Syntax | Programmatic Verification Hook |
| :--- | :--- | :--- |
| Exact Zero Containment | \(0 \in [a, b]\) | `ball.contains_zero()` |
| Positive Boundary Lock | \([a, b] > 0 \implies a > 0\) | `ball.is_positive()` |
| Negative Boundary Lock | \([a, b] < 0 \implies b < 0\) | `ball.is_negative()` |
| Strict Sub-Box Inclusion| \(N(B) \subseteq B\) | `initial_box.contains(newton_step)` |

---

## 4. Automated Execution Guard

Every script executing within `D:\Opencode AI Agent\Math 3.0 Tools` must read these parameters before initiating tool pipelines. 

```python
import os
import sys

def verify_workspace_lock():
    """
    Enforces absolute path tracking and directory confinement.
    Fails closed if execution leaks into external projects.
    """
    expected_root = r"D:\Opencode AI Agent\Math 3.0 Tools"
    current_working_dir = os.getcwd()
    
    if expected_root.lower() not in current_working_dir.lower():
        print(f"CRITICAL ERROR: Workspace Violation. Path locked to {expected_root}.")
        sys.exit(1)
        
    print("WORKSPACE LOCK: VERIFIED GENUINE")

if __name__ == "__main__":
    verify_workspace_lock()
```

If the environment audit detects any path overlap, mixed-language tokens, or floating-point leakage inside the core tracking files, `suite_check.py` must drop the build state to `Exit 1` and halt execution to block structural propagation of errors to the per-civilization pipeline.
