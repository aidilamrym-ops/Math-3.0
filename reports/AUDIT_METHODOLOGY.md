# Math 3.0 — Audit Methodology Against Vacuous Proofs

This document records the adversarial controls that every batch must satisfy
before a compiled Lean certificate is reported as substantive.  A green
`lake env lean` exit only proves that the kernel accepted the term; it does
not prove that the statement is non-vacuous, that its premises are inhabited,
or that the file is not a proxy for a stronger claim it never establishes.

## 1. Inhabited-premise check

*Tool:* `tools/omega_audit/substantiveness_gate.py` (Z3 premise encoding).

Every hypothesis set is translated to linear integer arithmetic and handed to
Z3.  The translation inlines `Prop`-valued predicate definitions (for example
`wilsonPlaquetteBound beta a m`) so that the actual constraints, not the name,
are checked.

* `UNSAT` → `EMPTY_PREMISE` (HIGH).  The implication is vacuous.
* `SAT` → the solver model is recorded in `reports/substantiveness_gate.json`
  as a constructive inhabitant witness.
* The conclusion `False` is exempt: there an unsatisfiable premise is the
  intended refutation certificate (for example
  `smt_bridge/auto_generated_bridge.lean`).

## 2. Counter-model generation

*Tool:* same gate, Z3 model printing.

The gate asks for a model of the premises and records it.  A reviewer can read
the model instead of trusting prose.  For linear fragments this is a complete
decision procedure; for non-linear or abstract premises the theorem is marked
`UNSUPPORTED` and remains subject to manual audit.

## 3. Mutation testing

*Tool:* same gate, `--mutate`.

For each theorem with a `Prop` hypothesis, the first hypothesis is weakened to
`True` and the file is recompiled.

* `KILLED` → the proof genuinely depends on the hypothesis (good).
* `SURVIVED` → `PREMISE_MUTATION_SURVIVED` (HIGH): the hypothesis was
  decorative and the theorem is weaker than advertised.

Mutation runs are opt-in because each mutant costs a kernel compile.  Batch
receipts record the mutants and their verdicts.

## 4. Non-trivial boundary and constant-definition scan

*Tool:* same gate, static rules.

* `CONSTANT_DEFINITION` — a parameterised definition returns the same literal
  for every input (the `plaquette := 1`, `wilsonAction := 0` failure mode).
* `TAUTOLOGICAL_DEFINITION` — a `Prop`-valued definition whose body is `True`
  or ends in `→ True`; this is the `isSheaf := ... → True` failure mode.
* `TRUE_CONCLUSION`, `TRIVIAL_TRUE_CONSEQUENCE`, `TRIVIAL_CONJUNCT` — the
  statement is `True`, has a `True` conjunct, or a vacuous `True` codomain.
* `TRIVIAL_DISJUNCT` — the conclusion has a top-level `∨` disjunct that is
  `True` or a reflexive `X = X`, so the disjunction is vacuous.
* `REFLEXIVE_EQUALITY`, `REFLEXIVE_CONJUNCT` — the statement or one of its
  conjuncts is `X = X`.
* `DECORATIVE_HYPOTHESIS` / `UNUSED_HYPOTHESIS` — a named hypothesis is never
  referenced (usage is downgraded when `omega`/`simp`/`linarith` may consume
  the context implicitly).
* `NUMERAL_ONLY_CHECK`, `LEM_ONLY_PROOF`, `TRIVIAL_EXISTENTIAL` — the proof is
  arithmetic on numerals, `Classical.em`, or a bare-numeral witness.
* `WITNESS_MISSING` — a `Prop` predicate is never applied to ground arguments
  and never existentially witnessed.  A ground application is an application
  where at least one argument is a numeral or a zero-parameter definition; this
  catches `EvenForm hyperbolic` and `DiscreteMorseFunction intervalMorseFunction
  IntervalGraph`, not only literal numerals.

### Waived constant definitions

Some constant definitions are the intended mathematical object: the zero
connection, the identity gauge field, and the identity Hodge star on a
unit-spaced cycle.  These may be waived through
`reports/substantiveness_waivers.json`, subject to three rules:

1. only the `CONSTANT_DEFINITION` code is waivable;
2. each entry names the file, declaration, and a written justification;
3. waived findings remain in the JSON receipt under `waivers_applied` and in
   the Markdown report, but do not count toward the active MEDIUM/HIGH totals.

The gate refuses to load a waiver with any other code.

## 5. Pure theorem versus bounded model

*Tool:* same gate, `reports/model_scope_manifest.json`.

Every file is classified from its header:

* `pure-theorem` — a general mathematical statement; no scale restriction.
* `bounded-model` — a finite lattice/proxy model of a continuum theory; the
  file must declare `Scope:`, `Cakupan:`, `Batas klaim:` or `Claim limits:`.
  Missing declaration → `SCOPE_UNDECLARED` (LOW; documentation debt tracked in
  the manifest).

Reports must state both classes separately.  A bounded-model certificate can
never be cited as a proof of the corresponding continuum conjecture.

## Commands

```text
python tools/omega_audit/substantiveness_gate.py
python tools/omega_audit/substantiveness_gate.py --surface reports/flawed_artifacts --regression --label regression
python tools/omega_audit/substantiveness_gate.py --mutate --mutation-limit 0 --label mutation
```

Exit codes: `0` PASS (no HIGH), `1` FAIL, `2` NOT RUN (no files matched).

When `--label mutation` is used the gate writes
`reports/substantiveness_gate_mutation.json` and `.md` and records the
`mutation_summary` block: total mutants, KILLED, SURVIVED, and survival rate.
`--mutation-limit 0` means "all candidates".

## Receipts

* `reports/substantiveness_gate.json` — full surface baseline.
* `reports/substantiveness_gate_mutation.json` — full mutation campaign.
* `reports/substantiveness_gate_regression.json` — negative control over
  `reports/flawed_artifacts/`; the gate must detect the archived vacuous files.
* `reports/model_scope_manifest.json` — per-file scope class and declaration.
* `reports/substantiveness_waivers.json` — reviewed exceptions (constant
  definitions only).

## Known limitations

* Z3 encoding covers linear integer arithmetic with predicate inlining; it
  does not encode `abs`, division, non-linear multiplication, or quantifiers.
  Unsupported premises are reported as `UNSUPPORTED`, never silently passed.
* Witness detection is syntactic: a ground application in any declaration
  counts.  It proves inhabitance is *exhibited*, not that the witness is
  mathematically meaningful.
* Mutation is limited to hypotheses of the shape `(h : P)` whose binder type
  looks propositional (comparisons/logical operators or a known `Prop`
  predicate); data hypotheses such as `(h : ℤ)` are skipped. One mutant per
  theorem is a signal, not a complete proof of premise relevance.
* `CONSTANT_DEFINITION` can be legitimate (unit sections, volume forms such as
  `hodgeStar0 = 1`); the finding is MEDIUM and requires an explicit waiver
  entry with a written justification.
* A bounded numeric fact must not be relabeled as a resolution of an open
  problem. `ContinuumOmegaLimitDefeat.lean` was archived in Batch 16 because
  `2 ^ k ≤ 1024` for `k ≤ 10` was presented as a resolution of the continuum
  hypothesis; the finite arithmetic did not support that claim.

These limits are why the automated gate is paired with the batch-by-batch
adversarial audit and the archival of defective certificates under
`reports/flawed_artifacts/`.
