# Substantiveness Gate

- Generated: 2026-11-16T10:29:03Z
- Lean files: **492**  declarations: **2029**  predicates: **19**
- Z3 premise check: **available**
- Findings: HIGH **0**, MEDIUM **0**, LOW **450**
- Waived constant definitions: **4**
- Verdict: **PASS**

## Findings

| Severity | Code | File:Line | Declaration | Detail |
|---|---|---|---|---|
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/ActualInfinityRefutation.lean:61` | `landauer_infinite_energy_contradiction` | hypothesis `h_cost : 1 ≤ cost` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/CollatzBoundedDefeat.lean:39` | `collatz_horizon_defeat` | hypothesis `hn : n ≥ 1` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/CollatzBoundedDefeat.lean:39` | `collatz_horizon_defeat` | hypothesis `hn_max : n ≤ 100` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/DecidableHomotopySphere.lean:69` | `freudenthal_index_lt` | hypothesis `h : n + 1 < k` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/DecidableHomotopySphere.lean:75` | `freudenthal_stability_bound` | hypothesis `h : n + 1 < k` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/DiscreteIndexTheorem.lean:61` | `discreteDirac_off_diagonal` | hypothesis `hpq : p.2 = q.2` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/DiscretePersistentHomology.lean:109` | `betti0_monotone` | hypothesis `hst : s ≤ t` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/DiscretePersistentHomology.lean:114` | `betti1_monotone` | hypothesis `hst : s ≤ t` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/ErdosSzekeresRamsey.lean:20` | `erdos_szekeres_pair` | hypothesis `hne : a ≠ b` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/EvenUnimodularObstruction.lean:95` | `not_two_pow_dvd_one` | hypothesis `hn : 0 < n` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/Gate5RationalBridge.lean:51` | `contains_midpoint` | hypothesis `hr : 0 ≤ r` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/Gate5RationalExtractionValidation.lean:43` | `contains_midpoint` | hypothesis `hr : 0 ≤ r` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/HorizonFrontierTests.lean:101` | `freudenthal_stability_bound` | hypothesis `h : n + 1 < k` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/LandauerBekensteinBound.lean:13` | `landauer_bits_le_energy` | hypothesis `hcost : 1 ≤ cost` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/LatticeInstantonBound.lean:189` | `bps_equality_forces_anti_self_dual_zero` | hypothesis `h : bpsCharge a b = bpsAction a b` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/LatticeInstantonBound.lean:209` | `bps_equality_forces_self_dual_zero` | hypothesis `h : bpsCharge a b = -bpsAction a b` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/UniversalContractionFixedPointTheorem.lean:8` | `convergence_bounded` | hypothesis `hx : x ≤ 10` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/auto_generated_bridge.lean:6` | `auto_generated_unsat` | hypothesis `h1 : r1 ≤ 2` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/auto_generated_bridge.lean:6` | `auto_generated_unsat` | hypothesis `h2 : r2 ≤ 2` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/auto_generated_bridge.lean:6` | `auto_generated_unsat` | hypothesis `h3 : r3 ≤ 2` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/auto_generated_bridge.lean:6` | `auto_generated_unsat` | hypothesis `h4 : r4 ≤ 2` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/auto_generated_bridge.lean:6` | `auto_generated_unsat` | hypothesis `h5 : r5 ≤ 2` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/auto_generated_bridge.lean:6` | `auto_generated_unsat` | hypothesis `h6 : r6 ≤ 2` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/auto_generated_bridge.lean:6` | `auto_generated_unsat` | hypothesis `h7 : 0 ≤ r1` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/auto_generated_bridge.lean:6` | `auto_generated_unsat` | hypothesis `h8 : 0 ≤ r2` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/auto_generated_bridge.lean:6` | `auto_generated_unsat` | hypothesis `h9 : 0 ≤ r3` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/auto_generated_bridge.lean:6` | `auto_generated_unsat` | hypothesis `h10 : 0 ≤ r4` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/auto_generated_bridge.lean:6` | `auto_generated_unsat` | hypothesis `h11 : 0 ≤ r5` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/auto_generated_bridge.lean:6` | `auto_generated_unsat` | hypothesis `h12 : 0 ≤ r6` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/auto_generated_bridge.lean:6` | `auto_generated_unsat` | hypothesis `htot : 13 ≤ r1 + r2 + r3 + r4 + r5 + r6` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/ramsey_clique_bound.lean:15` | `ramsey_clique_bound_unsat` | hypothesis `htotal : 13 ≤ ∑ i, r i` is not referenced in the proof |
| LOW | `SCOPE_UNDECLARED` | `Math30Kernel/BealConjectureDefeat.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `Math30Kernel/QuantumCircuit.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `Math30Kernel/QuantumMultiQubit.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `Math30Kernel/QuantumQft.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `Math30Kernel/RescuedDensity.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `Math30Kernel/RescuedHeisenberg.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/ActualInfinityRefutation.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/CertifiedManifest.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/ContinuityRefutation.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/ContinuumDensityDefeat.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/DecidableHomotopySphere.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/DiscreteLatticeGravityExtension.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/DiscreteLatticePathCounting.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/FtcIdentityCollapse.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/GoedelBoundaryContainment.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/GravitationalSingularityContainment.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/HigherInductivePushout.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/RamseyLatticeEnclosure.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/AbcCensusV3AuditCertificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/AndersonEnclosureBoundsCertificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/BealScale10to18Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/BoxFeasibilityWitnessCertificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/CertificateIndex.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/ConstitutionalLawReceiptCertificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/ContinuumDensityStressTestCertificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/ContractionBoundCertificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/FailedWorldTraceCertificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/FtcCollapseStressTestCertificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/GoedelContainmentStressTestCertificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/GravitationalSingularityStressTestCertificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/HeisenbergUncertaintyStressTestCertificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/IntegrityAuditCertificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/LedgerCrossMultiplicationCertificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/LteSpectralValidationCertificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/MetaBlindspotAuditCertificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/NavierStokesBlowupTraceCertificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily001Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily002Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily003Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily004Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily005Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily006Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily007Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily008Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily009Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily010Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily011Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily012Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily013Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily014Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily015Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily016Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily017Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily018Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily019Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily020Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily021Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily022Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily023Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily024Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily025Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily026Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily027Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily028Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily029Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily030Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily031Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily032Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily033Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily034Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily035Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily036Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily037Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily038Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily039Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily040Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily041Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily042Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily043Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily044Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily045Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily046Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily047Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily048Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily049Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily050Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily051Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily052Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily053Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily054Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily055Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily056Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily057Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily058Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily059Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily060Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily061Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily062Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily063Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily064Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily065Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily066Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily067Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily068Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily069Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily070Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily071Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily072Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily073Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily074Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily075Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily076Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily077Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily078Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily079Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily080Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily081Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily082Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily083Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily084Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily085Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily086Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily087Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily088Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily089Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily090Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily091Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily092Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily093Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily094Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily095Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily096Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily097Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily098Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily099Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily100Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily101Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily102Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily103Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily104Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily105Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily106Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily107Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily108Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily109Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily110Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily111Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily112Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily113Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily114Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily115Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily116Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily117Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily118Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily119Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily120Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily121Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily122Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily123Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily124Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily125Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily126Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily127Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily128Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily129Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily130Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily131Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily132Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily133Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily134Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily135Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily136Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily137Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily138Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily139Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily140Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily141Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily142Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily143Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily144Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily145Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily146Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily147Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily148Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily149Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily150Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily151Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily152Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily153Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily154Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily155Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily156Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily157Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily158Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily159Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily160Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily161Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily162Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily163Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily164Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily165Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily166Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily167Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily168Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily169Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily170Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily171Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily172Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily173Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily174Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily175Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily176Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily177Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily178Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily179Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily180Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily181Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily182Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily183Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily184Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily185Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily186Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily187Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily188Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily189Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily190Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily191Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily192Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily193Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily194Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily195Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily196Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily197Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily198Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily199Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily200Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily201Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily202Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily203Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily204Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily205Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily206Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily207Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily208Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily209Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily210Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily211Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily212Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily213Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily214Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily215Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily216Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily217Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily218Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily219Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily220Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily221Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily222Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily223Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily224Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily225Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily226Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily227Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily228Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily229Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily230Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily231Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily232Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily233Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily234Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily235Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily236Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily237Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily238Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily239Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily240Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily241Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily242Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily243Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily244Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily245Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily246Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily247Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily248Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily249Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily250Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily251Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily252Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily253Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily254Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily255Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily256Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily257Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily258Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily259Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily260Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily261Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily262Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily263Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily264Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily265Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily266Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily267Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily268Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily269Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily270Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily271Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily272Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily273Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily274Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily275Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily276Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily277Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily278Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily279Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily280Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily281Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily282Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily283Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily284Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily285Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily286Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily287Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily288Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily289Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily290Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily291Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily292Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily293Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily294Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily295Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily296Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily297Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily298Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily299Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily300Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily301Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily302Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily303Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily304Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily305Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily306Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily307Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily308Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily309Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily310Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily311Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily312Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily313Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily314Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily315Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily316Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily317Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily318Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily319Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily320Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily321Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily322Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily323Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily324Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily325Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily326Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily327Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily328Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily329Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily330Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily331Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily332Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily333Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily334Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily335Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily336Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily337Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily338Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily339Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily340Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily341Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily342Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily343Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily344Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily345Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily346Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily347Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily348Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily349Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily350Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily351Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily352Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily353Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily354Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily355Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily356Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily357Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily358Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily359Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily360Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily361Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily362Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily363Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily364Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily365Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily366Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily367Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily368Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily369Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily370Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily371Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily372Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiFamily373Certificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/OpenaiRiemannConfrontationCertificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/RawFgInitialEnclosureCertificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/RegressionMasterReportCertificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/RhCriticalLineValidationCertificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/RhExtremeStressTestCertificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/RhSpectralAnomaliesCertificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/SignFlipAbsenceCertificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/TopologicalUniquenessCertificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/TriadStateTransitionsCertificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/certificates/Z3TribunalBoundsCertificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |

## Waived Constant Definitions

| File:Line | Declaration | Reason |
|---|---|---|
| `lean/spec_v4/DiscreteChernSimons.lean:75` | `zeroConnection` | Canonical zero U(1) connection. Its constancy is the definition; the file proves plaquetteFlux_zero, gaugeTransform_zero, and chernSimonsAction_zero from it. |
| `lean/spec_v4/DiscreteHodgeStar.lean:54` | `hodgeStar0` | On the unit-spacing cycle every metric weight equals 1, so the 0-cochain Hodge star is the identity matrix in the chosen basis. The header states this scope explicitly. |
| `lean/spec_v4/DiscreteHodgeStar.lean:59` | `hodgeStar1` | Inverse metric identification on the unit-spacing cycle; again the identity matrix in the chosen basis, with the flat/unit-spaced scope documented in the header. |
| `lean/spec_v4/DiscreteYangMills.lean:132` | `trivialConnection` | Canonical identity gauge field. Its constancy is the definition; plaquette_trivial and wilsonAction_trivial are proved from it. |

