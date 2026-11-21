# Flawed artifact archive — interval inertia soundness (2026-11-21)

Batch C, Pair 1 of the OMEGA recursive audit. The two files below were replaced
in place; the exact pre-repair bytes are preserved here as `.orig`.

| Archived file | SHA-256 of `.orig` |
|---|---|
| `IntervalMatrices.py.orig` | `1db7bb7cb82a217c8e65a2e30752bdec8045345bb6f253b77b9c835e67ce2780` |
| `IntervalLDLT.py.orig` | `4a9ba36e9dc073654944a7af1b513760cbcf9a410dd0ddf9045beb08ac51b48a` |

`pre_repair_probe.json` is the machine-generated receipt produced by executing
the archived modules before any edit. It records the raw behaviour cited below.

## Findings repaired

### F1 — HIGH — Gershgorin fallback fabricates an inertia signature

`IntervalLDLTSolver.compute_inertia` replaced a `nan` eigenvalue enclosure with
`_gershgorin_bound(idx)`, the *lower edge of the i-th Gershgorin disk*, then
classified that number as the i-th eigenvalue. Gershgorin's theorem does not
identify disk `i` with eigenvalue `i`; a disk edge is not an eigenvalue
enclosure. Reproducer from the receipt:

* `[[1, 2], [0, 1]]` is non-symmetric, its only eigenvalue is `+1` with
  algebraic multiplicity two, yet the archived code returns `(1, 1, 0)`.
* `eig(nonstop=True)` returns `nan` for every repeated spectrum, so the
  fallback was the *primary* path for identity matrices, diagonal matrices with
  repeated entries, and singular matrices — not an exotic branch.
* The singular matrix `[[1,1,0],[1,1,0],[0,0,2]]` raised an alarm only because
  the last diagonal entry happened to be `0`; the first two rows were already
  misclassified as negative by the disk-edge heuristic.

Repair: delete `_gershgorin_bound`; request `eig(multiple=True)`, which the
`python-flint` diagnostic itself recommends for repeated eigenvalues; raise
`UndeterminedPivotException` (wrapped as `ResolutionAlarm`) on any `nan`,
non-finite, non-real, or zero-straddling enclosure.

### F2 — HIGH — `rad_str` was added to the midpoint instead of widening about it

`set_entry_exact(i, j, mid, rad)` executed `arb(mid) + arb(rad)`. For
`mid = 1`, `rad = 0.5` the archived module stores the point `1.5` (radius `0`),
not the interval `[0.5, 1.5]`. The live caller
`Math30Kernel/CompositeQftMatrix.py` passes a genuine `.rad()` value, so its
QFT density-matrix entries were translated to their upper endpoint instead of
being enclosed. This also made a zero-straddling interval impossible to
construct through the public builder API.

Repair: store `mid + arb(0, radius)`, i.e. a true ball of the requested radius
about the midpoint.

### F3 — MEDIUM — negative dimensions silently accepted

`flint.arb_mat(-1, -1)` does not raise; it returns an object whose `nrows()`
and `ncols()` are both `-1` and which has no entries. The archived builder
forwarded that object unchecked. Repair: reject negative dimensions and
non-integer dimensions at construction.

### F4 — MEDIUM — negative and non-finite radii silently coerced

`flint.arb("1", "-0.5")` takes the absolute value of the radius, so the
archived builder silently turned a negative radius into `+0.5`. It also had no
guard against `nan`/`inf` midpoints or radii. Repair: require a finite midpoint
and a finite, certainly non-negative radius.

### F5 — HIGH — no symmetry or squareness gate before reporting inertia

The class documents real-symmetric input but never checked it. A non-square
matrix reached `eig` and failed with an opaque `ValueError`; a non-symmetric
matrix could be assigned an "inertia" that has no Sylvester meaning. Repair:
check squareness and two-way ball containment of `A[i,j]` and `A[j,i]` before
any eigen computation; fail closed otherwise.

### F6 — LOW — `get_matrix_snapshot` returned the live matrix, not a snapshot

Callers could mutate the builder's matrix through the returned object. Repair:
return `flint.arb_mat(self.matrix)`, which copies (verified by mutating the
returned object and re-reading the builder).

## Reproduction

Run from the repository root with the archived files restored:

```text
python _capture_batchC_pair1.py
```

The script writes `pre_repair_probe.json` next to itself. The post-repair
receipt is `reports/omega_audit/batchC_pair1/post_repair_probe.json`.
