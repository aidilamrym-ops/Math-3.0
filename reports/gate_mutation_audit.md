# Gate Mutation Audit

- Generated: 2026-11-11 13:14:20
- Cases: **42**  Passed: **42**  Missed: **0**  Inconclusive: **0**
- Elapsed: 16.5s

| Verdict | Suite | Case | Expected | Observed |
|---|---|---|---|---|
| PASS | token | sorry | DETECT | DETECT |
| PASS | token-strict | sorry | DETECT | DETECT |
| PASS | token | sorryAx | DETECT | DETECT |
| PASS | token-strict | sorryAx | DETECT | DETECT |
| PASS | token | admit | DETECT | DETECT |
| PASS | token-strict | admit | DETECT | DETECT |
| PASS | token | axiom | DETECT | DETECT |
| PASS | token-strict | axiom | DETECT | DETECT |
| PASS | token | private axiom | DETECT | DETECT |
| PASS | token-strict | private axiom | DETECT | DETECT |
| PASS | token | simp-attribute axiom | DETECT | DETECT |
| PASS | token-strict | simp-attribute axiom | DETECT | DETECT |
| PASS | token | constant | DETECT | DETECT |
| PASS | token-strict | constant | DETECT | DETECT |
| PASS | token | opaque | DETECT | DETECT |
| PASS | token-strict | opaque | DETECT | DETECT |
| PASS | token | partial def | DETECT | DETECT |
| PASS | token-strict | partial def | DETECT | DETECT |
| PASS | token | native_decide | DETECT | DETECT |
| PASS | token-strict | native_decide | DETECT | DETECT |
| PASS | token | implemented_by | DETECT | DETECT |
| PASS | token-strict | implemented_by | DETECT | DETECT |
| PASS | token | extern | DETECT | DETECT |
| PASS | token-strict | extern | DETECT | DETECT |
| PASS | token | string separator evasion | DETECT | DETECT |
| PASS | token-strict | string separator evasion | DETECT | DETECT |
| PASS | token | string literal is not a token | DETECT | DETECT |
| PASS | token-strict | string literal is not a token | ALLOW | ALLOW |
| PASS | token | comment is not a token | ALLOW | ALLOW |
| PASS | token-strict | comment is not a token | ALLOW | ALLOW |
| PASS | token | clean file | ALLOW | ALLOW |
| PASS | token-strict | clean file | ALLOW | ALLOW |
| PASS | manifest | clean root | ALLOW | ALLOW |
| PASS | manifest | modified pinned file | DETECT | DETECT |
| PASS | manifest | deleted pinned file | DETECT | DETECT |
| PASS | manifest | unpinned extra file | DETECT | DETECT |
| PASS | manifest | corrupted manifest hash | DETECT | DETECT |
| PASS | manifest | corrupted README seal | DETECT | DETECT |
| PASS | compile | well-typed file | ALLOW | ALLOW |
| PASS | compile | ill-typed file | DETECT | DETECT |
| PASS | theorem | existing theorem name | ALLOW | ALLOW |
| PASS | theorem | nonexistent theorem name | DETECT | DETECT |
