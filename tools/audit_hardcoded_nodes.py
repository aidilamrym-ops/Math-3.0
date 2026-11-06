import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import ast
import os
import sys

TARGETS = [
    "mcp/t2n/solvers/beal_lattice_solver.py",
    "mcp/t2n/solvers/yudeng_singularity_sieve.py",
    "mcp/t2n/rh_core/rh_krypton_solver.py"
]

class HardcodedReturnAuditor(ast.NodeVisitor):
    def __init__(self, filename):
        self.filename = filename
        self.findings = []
        self.current_func = None

    def visit_FunctionDef(self, node):
        old_func = self.current_func
        self.current_func = node.name
        self.generic_visit(node)
        self.current_func = old_func

    def visit_Return(self, node):
        if isinstance(node.value, ast.Constant):
            self.findings.append((self.filename, self.current_func, f"Constant return: {node.value.value}"))
        elif isinstance(node.value, (ast.Tuple, ast.List)):
            # Check if all elements are constants or simple values
            all_const = all(isinstance(elt, ast.Constant) for elt in node.value.elts)
            if all_const:
                vals = [elt.value for elt in node.value.elts]
                self.findings.append((self.filename, self.current_func, f"Static collection return: {vals}"))
        self.generic_visit(node)

def main():
    print("[AST AUDITOR] Scanning core solver modules for hardcoded returns...")
    all_findings = []
    for path in TARGETS:
        if not os.path.exists(path):
            print(f"[WARNING] Target file not found: {path}")
            continue
        with open(path, "r", encoding="utf-8") as f:
            code = f.read()
        try:
            tree = ast.parse(code, filename=path)
            auditor = HardcodedReturnAuditor(path)
            auditor.visit(tree)
            all_findings.extend(auditor.findings)
        except Exception as e:
            print(f"[ERROR] Failed parsing {path}: {e}")

    if all_findings:
        print(f"[AUDIT ALERT] Found {len(all_findings)} hardcoded/static returns:")
        for f in all_findings:
            print(f"  File: {f[0]} | Function: {f[1]} | Detail: {f[2]}")
        sys.exit(1)
    else:
        print("[AUDIT SUCCESS] No uncalculated static returns detected across target files.")
        sys.exit(0)

if __name__ == "__main__":
    main()