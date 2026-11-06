# EXPORTS DISCLOSURE — Math 3.0 / Masalah #10 and #18

**Document type:** standalone forensic disclosure of on-disk artifacts  
**Generated:** 2026-11-06  
**Workspace:** `D:\Opencode AI Agent\Math 3.0 Tools`  
**Git HEAD at generation:** `f4c23ddff7f3d100002ebf3575b171ae1db7115c`  
**Master ledger:** `manifest.json`, **1,310 rows**  
**Distribution context:** GPL-3.0 / CC-BY-4.0 sovereign toolchain, Math 3.0.2

> **Scope statement.** This document records what exists on disk and what was
> actually executed. It is an artifact-level audit. It is **not** a proof of the
> Beal Conjecture or of finite-time blow-up for the Euler/Navier–Stokes
> equations. Section 5 lists the non-claims explicitly.

---

## 1. Core statement of independent audit

The audit covered the complete local OpenAI-Math manuscript catalogue as
materialised in `staging/openai_math/preprints/` and summarised in
`reports/math30_real_empirical_parameters.json`.

| Metric | Verified value | Source |
|---|---:|---|
| Manuscript families present | 373 | `openai_family_001.json` … `openai_family_373.json` |
| Families with TeX source located | 373 | extraction summary |
| Families with extracted constants | 349 | extraction summary |
| Families using fallback (no regex match) | 24 | extraction summary |
| Families with no TeX source | 0 | extraction summary |
| Master ledger rows | 1,310 | `manifest.json` |
| Lean files scanned for placeholders | 421 | `lean/spec_v4/**/*.lean` |
| Placeholder tokens (`sorry` / `admit` / `axiom` / `Abort`) | 0 | anti-circularity gate, verdict `PASS` |

The end-to-end pipeline is closed in the operational sense: every family has an
artifact record, every extracted value is stored as an exact rational string or
as a verbatim TeX token, and the ledger hash-pins the workspace. This is a
**coverage and reproducibility** result, not a mathematical verification result.

---

## 2. Empirical parameter discovery summary

Source: `reports/math30_real_empirical_parameters.json`  
SHA-256: `7705b0505f4e02d056debf95d79508f7fa920f63ff0a7fe46dab6be5a4c3a855`

| Metric | Exact value | Notes |
|---|---|---|
| Candidate regex matches | 4,434 | raw matches across all patterns |
| Families with numeric primary constant | 198 | of 349 extracted families |
| Families with non-numeric primary token | 151 | e.g. inline TeX expressions |
| Median | `1/100000` (= 10^-5) | exact rational median |
| Minimum | `-2` | exact |
| Maximum | `10^96` | family 140 |
| Second extreme outlier | `613302797399911/6480` | family 266, ≈ 9.465 × 10^10 |
| `log10(abs(x))` range | −35 to 96 | 120 non-zero magnitudes |
| `abs(x) <= 1` | 106 | micro-threshold regime |
| `abs(x) > 10^6` | 2 | isolated extremes |

**Scale separation confirmed.** The central mass of extracted thresholds sits at
or below 10^-5, while two isolated literals sit at 10^96 and ≈ 9.465 × 10^10.
The raw mean (≈ 5.05 × 10^93) and variance are dominated by those two values and
are not meaningful descriptors; the median and the threshold subset are the
defensible statistics.

**Precision note.** The 4,434 figure is the count of **candidate regex
matches**, not 4,434 distinct continuous constants. After parsing, 198 families
carry a numeric primary constant and 151 carry a non-numeric token. Any external
citation must use the parsed count, not the match count.

---

## 3. Independent open-problem fronts secured

### 3.1 Masalah #10 — Beal Conjecture

**Artifacts**

- Solver: `mcp/t2n/solvers/beal_lattice_solver.py`
  (SHA-256 `4f070d0f220916c961e2139d93e42611a69188e33315022b718e3a3efb9a531a`)
- Trial: `reports/beal_conjecture_trial_001.json`
- Certificate: `reports/certificates/beal_conjecture_trial_001_certificate.json`
- Batch summary: `reports/beal_batch_sweep_summary.json`
  (SHA-256 `b67a18492781c10c44096e482ef375be3f912794831a393dcbb41cdbcc659933`)

**Execution result**

| Metric | Value |
|---|---:|
| Exponent range | 3 ≤ x, y, z ≤ 10 |
| Exponent triples | 512 |
| Base triples per window | 4 |
| Total matrices evaluated | **2,048** |
| Anomalies under declared criterion | **0** |
| Precision context | `flint.ctx.prec = 24000` |
| Interval radius | `1/10^40` |

**Case A — adversarial coprime test** `(A,B,C)=(2,3,5)`, `(x,y,z)=(3,3,3)`

```
Sylvester matrix = [[2, 0, 0],
                    [0, 1, 0],
                    [0, 0, 1]]
determinant      = 2
gcd(A,B,C)       = 1
coprime flag     = True
```

**Case B — certified common-factor test** `(A,B,C)=(2,2,2)`, `(x,y,z)=(3,3,4)`

```
Sylvester matrix = [[2, 0, 0],
                    [0, 2, 0],
                    [0, 0, 2]]
determinant      = 8
Gate 4 ratio     = 3/10  (< 1/2)
contractible     = True
```

**Disclosure.** The matrix diagonal is `gcd(base, 2)`; the determinant therefore
encodes base parity, not the Diophantine equation `A^x + B^y = C^z`. The sweep
does not evaluate that equation and does not search counterexamples over
arbitrary bases. The zero-anomaly result is a statement about the declared
Sylvester-parity criterion only. The Lean certificate at
`lean/spec_v4/certificates/BealConjectureTrial001Certificate.lean` proves
`True := by trivial`; it is a linkage seal, not a proof of Beal.

### 3.2 Masalah #18 — Yu Deng hydrodynamic singularity sieve

**Artifacts**

- Solver: `mcp/t2n/solvers/yudeng_singularity_sieve.py`
  (SHA-256 `034e09d866e5354ef453d8dcb7e9f675b26d1217aed779fa7fe9d0a94ce6036b`)
- Batch summary: `reports/yudeng_batch_sweep_summary.json`
  (SHA-256 `0756599e86eef027c4b0a84db76d4f663c575b56ed7a9b5a4c174bdaccce3d56`)

**Execution result**

| Metric | Value |
|---|---:|
| Velocity-gradient range | 1 … 50 |
| Curvature range | 1 … 50 |
| Total coordinates | **2,500** |
| Coordinates flagged unstable | **2,500** |
| Gate 4 ratio | `4/10` (< 1/2) |
| Precision context | `flint.ctx.prec = 24000` |
| Interval radius | `1/10^40` |

Representative coordinate `(velocity_gradient, curvature, density) = (1,1,10)`:

```
matrix      = [[2, 0, 0],
               [0, 2, 0],
               [0, 0, -3]]
determinant = -12
```

**Disclosure.** The third diagonal is constructed as `-(gcd(density,2)+1)`;
with the sweep fixing `density = 10`, every determinant is negative by
construction. The reported 2,500/2,500 instability count therefore reflects the
chosen sign convention, not a detected finite-time blow-up. The Gate 4 ratio is
the constant `4/10` returned by the validator; it is not computed from the
coordinate data. No Euler or Navier–Stokes PDE is integrated, and no singularity
time is estimated. This front is an interface and data-shape test.

---

## 4. Absolute replicability seals

| Seal | Value |
|---|---|
| Master ledger | `manifest.json`, **1,310 rows** |
| Ledger SHA-256 | `feb9575c849db500f00aa410975ef19ecf7570efe01b8f34e36bda1d2ec4a96b` |
| Empirical database SHA-256 | `7705b0505f4e02d056debf95d79508f7fa920f63ff0a7fe46dab6be5a4c3a855` |
| Beal commit pushed to `origin/main` | `f4c23dd` |
| Precision lock | 24,000 bits |
| Interval radius lock | `1/10^40` m |
| Lean placeholder scan | **PASS**, 421 files, 0 tokens |
| Exact arithmetic policy | `fractions.Fraction` and `math.gcd`; no `float()` in solver sources |

The Lean gate was executed with:

```
python C:\Users\usER\.config\opencode\skills\anti-circularity\scripts\gate.py lean lean\spec_v4
```

Output:

```
ANTI-CIRCULARITY GATE [lean]
  result: FAIL=0  NOT_RUN=0  SKIP=0
  verdict: PASS
```

This certifies the absence of placeholder tokens. It does **not** certify the
strength or truth of any theorem statement; the kernel remains the authority.

---

## 5. Non-claims and limitations

1. No solution or disproof of the Beal Conjecture is claimed.
2. No proof of finite-time blow-up for Euler or Navier–Stokes is claimed.
3. The Beal sweep evaluates a gcd-parity matrix, not `A^x + B^y = C^z`.
4. The Yu Deng sweep assigns a fixed negative third diagonal and a fixed
   contraction ratio; its flags are structural.
5. The Lean certificates are `True := by trivial` linkage seals.
6. The upstream Git remote is not usable: `https://github.com` is a domain, not
   a repository. No OpenAI refs were fetched. Nothing in this document depends
   on that remote.
7. The 4,434 count is candidate matches; the parsed numeric count is 198.

---

## 6. Reproduction commands

```powershell
# Beal self-test and batch sweep
C:\Python314\python.exe mcp/t2n/solvers/beal_lattice_solver.py --test
C:\Python314\python.exe beal_batch_sweep.py

# Yu Deng self-test and fluid sweep
C:\Python314\python.exe mcp/t2n/solvers/yudeng_singularity_sieve.py --test
C:\Python314\python.exe yudeng_fluid_sweep.py

# Ledger synchronisation
C:\Python314\python.exe mcp/t2n/core/repokeeper.py

# Placeholder gate
C:\Python314\python.exe C:\Users\usER\.config\opencode\skills\anti-circularity\scripts\gate.py lean lean\spec_v4
```

---

## 7. Operational completion log

```
[2026-11-06] Beal solver compiled; self-test PASSED; zero float conversions.
[2026-11-06] Beal trial 001 generated; SHA-256 sealed; Lean certificate linked.
[2026-11-06T05:19:56Z] Beal batch sweep COMPLETED: 2,048 matrices, 0 anomalies.
[2026-11-06] Commit f4c23dd pushed to origin/main.
[2026-11-06] Yu Deng sieve compiled; self-test PASSED; zero float conversions.
[2026-11-06T05:43:00Z] Yu Deng fluid sweep COMPLETED: 2,500 coordinates, 2,500 structural flags.
[2026-11-06] manifest.json synchronized at 1,310 rows.
[2026-11-06] Anti-circularity Lean gate PASS: 421 files, 0 placeholders.
[2026-11-06] EXPORTS_DISCLOSURE.md written to exports/.
```
