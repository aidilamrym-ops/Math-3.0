#!/usr/bin/env python3
"""Fail-closed gatekeeper for TEOREMA_INISIALISASI_SINGULARITAS.

Verdicts are delegated to gatekeeper_real.py, which runs the actual Z3 solver.
Missing sources and unparseable SMT blocks fail closed; no certificate is
invented and no source file is moved.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from gatekeeper_common import run_gatekeeper

THEOREM = 'TEOREMA_INISIALISASI_SINGULARITAS'
TARGET = 'staging/user_disertasi/gnase_theorems/TEOREMA_INISIALISASI_SINGULARITAS.typ'

if __name__ == "__main__":
    sys.exit(run_gatekeeper(TARGET, THEOREM))
