# Substantiveness Gate

- Generated: 2026-11-19T12:53:20Z
- Lean files: **1**  declarations: **6**  predicates: **3**
- Z3 premise check: **available**
- Findings: HIGH **0**, MEDIUM **0**, LOW **2**
- Waived constant definitions: **0**
- Verdict: **PASS**

## Findings

| Severity | Code | File:Line | Declaration | Detail |
|---|---|---|---|---|
| LOW | `WITNESS_MISSING` | `lean/spec_v4/certificates/NewConjectureBatchI.lean:29` | `IsOppermannWitness` | predicate `IsOppermannWitness` is never applied to ground arguments or existentially witnessed |
| LOW | `WITNESS_MISSING` | `lean/spec_v4/certificates/NewConjectureBatchI.lean:35` | `SatisfiesOppermann` | predicate `SatisfiesOppermann` is never applied to ground arguments or existentially witnessed |

## Mutation Results

- Mutants: **3**  KILLED: **3**  SURVIVED: **0**  survival rate: **0.0**

| File | Declaration | Hypothesis | Verdict |
|---|---|---|---|
| `lean/spec_v4/certificates/NewConjectureBatchI.lean` | `oppermann_bounded_up_to_100` | `hn` | **KILLED** |
| `lean/spec_v4/certificates/NewConjectureBatchI.lean` | `cousin_prime_witnesses_below_1000` | `hp` | **KILLED** |
| `lean/spec_v4/certificates/NewConjectureBatchI.lean` | `sexy_prime_witnesses_below_1000` | `hp` | **KILLED** |

