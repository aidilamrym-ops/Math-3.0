# Substantiveness Gate

- Generated: 2026-11-16T01:11:26Z
- Lean files: **32**  declarations: **171**  predicates: **26**
- Z3 premise check: **available**
- Findings: HIGH **1**, MEDIUM **33**, LOW **51**
- Verdict: **FAIL**

## Findings

| Severity | Code | File:Line | Declaration | Detail |
|---|---|---|---|---|
| HIGH | `REFLEXIVE_EQUALITY` | `reports/flawed_artifacts/DiscreteHodgeStar.tautological-star-warnings.lean:70` | `hodge_star_commutes_d` | conclusion is `X = X` |
| MEDIUM | `CONSTANT_DEFINITION` | `reports/flawed_artifacts/DiscreteChernSimons.vacuous-flux-placeholder.lean:39` | `plaquetteFlux` | `plaquetteFlux` ignores all 6 parameters and returns `0` |
| MEDIUM | `CONSTANT_DEFINITION` | `reports/flawed_artifacts/DiscreteChernSimons.vacuous-flux-placeholder.lean:52` | `wrtiInvariant` | `wrtiInvariant` ignores all 2 parameters and returns `1` |
| MEDIUM | `CONSTANT_DEFINITION` | `reports/flawed_artifacts/DiscreteChernSimons.vacuous-flux-placeholder.lean:56` | `zeroConnection` | `zeroConnection` ignores all 1 parameters and returns `fun _ _ _ _ => 0` |
| MEDIUM | `CONSTANT_DEFINITION` | `reports/flawed_artifacts/DiscreteHodgeStar.tautological-star-warnings.lean:51` | `hodgeStar0` | `hodgeStar0` ignores all 1 parameters and returns `1` |
| MEDIUM | `CONSTANT_DEFINITION` | `reports/flawed_artifacts/DiscreteHodgeStar.tautological-star-warnings.lean:54` | `hodgeStar1` | `hodgeStar1` ignores all 1 parameters and returns `1` |
| MEDIUM | `CONSTANT_DEFINITION` | `reports/flawed_artifacts/DiscreteYangMills.placeholder-plaquette.lean:36` | `plaquette` | `plaquette` ignores all 7 parameters and returns `1` |
| MEDIUM | `CONSTANT_DEFINITION` | `reports/flawed_artifacts/DiscreteYangMills.placeholder-plaquette.lean:42` | `wilsonAction` | `wilsonAction` ignores all 3 parameters and returns `0` |
| MEDIUM | `CONSTANT_DEFINITION` | `reports/flawed_artifacts/DiscreteYangMills.placeholder-plaquette.lean:46` | `gaugeTransform` | `gaugeTransform` ignores all 4 parameters and returns `fun x y z t μ => 1` |
| MEDIUM | `CONSTANT_DEFINITION` | `reports/flawed_artifacts/DiscreteYangMills.placeholder-plaquette.lean:58` | `trivialConnection` | `trivialConnection` ignores all 2 parameters and returns `fun _ _ _ _ _ => 1` |
| MEDIUM | `DECORATIVE_HYPOTHESIS` | `reports/flawed_artifacts/UniversalTopologicalInvariantSingularityResolution.lean:9` | `universal_topological_singularity_resolution` | hypothesis `_h_nonzero : 0 < n` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `reports/flawed_artifacts/FiniteLatticeSpectralGravity.lean:29` | `discrete_volume_preservation` | hypothesis `hv : v > 0` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `reports/flawed_artifacts/FiniteNavierStokesDissipation.lean:16` | `navier_stokes_dissipation_bounded` | hypothesis `h_nu : nu ≤ 10` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `reports/flawed_artifacts/FiniteNavierStokesDissipation.lean:16` | `navier_stokes_dissipation_bounded` | hypothesis `h_grad : v_grad ≤ 100` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `reports/flawed_artifacts/FiniteRiemannZetaLattice.lean:28` | `guinand_trace_stabilization` | hypothesis `h : n > 0` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `reports/flawed_artifacts/FiniteYangMillsMassGapLattice.lean:16` | `yang_mills_mass_gap_positive` | hypothesis `_h_beta : beta ≥ 2` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `reports/flawed_artifacts/FiniteYangMillsMassGapLattice.lean:24` | `spectral_gap_stabilization` | hypothesis `h_gap : gap ≥ 1` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `reports/flawed_artifacts/LatticeLearningWithErrors.lean:20` | `lwe_error_small_bound` | hypothesis `hq : q ≥ 4` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `reports/flawed_artifacts/LatticeLearningWithErrors.lean:30` | `lwe_search_to_decision_bound` | hypothesis `_hq : q ≥ 1` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `reports/flawed_artifacts/LatticeLearningWithErrors.lean:30` | `lwe_search_to_decision_bound` | hypothesis `_hn : n > 0` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `reports/flawed_artifacts/LatticeLearningWithErrors.lean:30` | `lwe_search_to_decision_bound` | hypothesis `_hm : m > 0` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `reports/flawed_artifacts/MillenniumBirchSwinnertonDyer.vacuous-structure.lean:40` | `bsd_tateshafarevich_bounded` | hypothesis `h_cond : conductorBound ≤ 100` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `reports/flawed_artifacts/MillenniumCollatzGeneralization.lean:16` | `collatz_orbit_bounded` | hypothesis `h_n : n > 0` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `reports/flawed_artifacts/MillenniumCollatzGeneralization.lean:16` | `collatz_orbit_bounded` | hypothesis `h_fuel : fuel ≥ 100` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `reports/flawed_artifacts/MillenniumCollatzGeneralization.lean:25` | `collatz_loop_stabilization` | hypothesis `h : a ≤ b` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `reports/flawed_artifacts/MillenniumHodgeConjecture.vacuous-cycles.lean:42` | `hodge_cycle_bounded` | hypothesis `h_lim : maxLimit ≤ 50` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `reports/flawed_artifacts/MillenniumNavierStokesSmoothness.lean:28` | `navier_stokes_energy_bounded` | hypothesis `h_forcing : state.forceBound + initialEnergy ≥ state.viscosity * state.v` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `reports/flawed_artifacts/MillenniumNavierStokesSmoothness.lean:40` | `navier_stokes_pressure_regularity` | hypothesis `h_grad : velocity_gradient_sq ≤ 1000` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `reports/flawed_artifacts/MillenniumPoincareConjecture.lean:42` | `ricci_flow_non_collapse_bound` | hypothesis `h_bound : maxCurvature ≤ 500` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `reports/flawed_artifacts/MillenniumRiemannHypothesis.vacuous-symmetry.lean:34` | `riemann_hypothesis_critical_line_bound` | hypothesis `h_symmetric : z.sigmaNumerator * 2 = z.sigmaDenominator` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `reports/flawed_artifacts/MillenniumRiemannHypothesis.vacuous-symmetry.lean:44` | `riemann_explicit_formula_positivity` | hypothesis `h_cond : conductor ≤ 10` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `reports/flawed_artifacts/MillenniumRiemannHypothesis.vacuous-symmetry.lean:44` | `riemann_explicit_formula_positivity` | hypothesis `h_test : testFunctionBound ≤ 5` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `reports/flawed_artifacts/QuantumTopologicalModularTensorCategory.lean:55` | `braid_unitarity_bound` | hypothesis `hpq : p ≤ q` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `reports/flawed_artifacts/QuantumTopologicalModularTensorCategory.lean:55` | `braid_unitarity_bound` | hypothesis `hpos : p ≥ 0` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `reports/flawed_artifacts/TwistorLatticeCorrespondence.lean:24` | `twistor_incidence_stable` | hypothesis `_hx : abs x ≤ 1000` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `reports/flawed_artifacts/UniversalQuantumCoherencePhaseLock.lean:13` | `universal_quantum_coherence_phase_lock` | hypothesis `_h_amp : amplitude ≤ 1000` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `reports/flawed_artifacts/YangMillsLatticeBoundary.vacuous-gap.lean:40` | `yang_mills_mass_gap_positive` | hypothesis `h_coupling : coupling > 0` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `reports/flawed_artifacts/YangMillsLatticeBoundary.vacuous-gap.lean:48` | `yang_mills_lattice_cutoff_bound` | hypothesis `h_grid : delta_grid ≥ min_planck` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `reports/flawed_artifacts/YangMillsLatticeBoundary.vacuous-gap.lean:48` | `yang_mills_lattice_cutoff_bound` | hypothesis `h_planck : min_planck > 0` is not referenced in the proof |
| MEDIUM | `LEM_ONLY_PROOF` | `reports/flawed_artifacts/EllipticRankSpectralCertificate.lean:29` | `dsitni_growth_bound` | proof is `Classical.em` tautology |
| MEDIUM | `NUMERAL_ONLY_CHECK` | `reports/flawed_artifacts/AbcCensusEvidence.lean:5` | `abc_triple_quality_bound_1` | only compares two numerals |
| MEDIUM | `NUMERAL_ONLY_CHECK` | `reports/flawed_artifacts/AbcCensusEvidence.lean:9` | `abc_triple_quality_bound_2` | only compares two numerals |
| MEDIUM | `NUMERAL_ONLY_CHECK` | `reports/flawed_artifacts/AbcCensusEvidence.lean:13` | `abc_triple_quality_bound_3` | only compares two numerals |
| LOW | `SCOPE_UNDECLARED` | `reports/flawed_artifacts/EllipticRankSpectralCertificate.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `reports/flawed_artifacts/FiniteLatticeSpectralGravity.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `reports/flawed_artifacts/FiniteNavierStokesDissipation.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `reports/flawed_artifacts/FinitePvNPSeparationLattice.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `reports/flawed_artifacts/FiniteRiemannZetaLattice.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `reports/flawed_artifacts/FiniteYangMillsMassGapLattice.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `reports/flawed_artifacts/HeisenbergUncertaintyDemystified.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `reports/flawed_artifacts/LatticeLearningWithErrors.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `reports/flawed_artifacts/MillenniumHodgeConjecture.vacuous-cycles.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `reports/flawed_artifacts/MillenniumNavierStokesSmoothness.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `reports/flawed_artifacts/MillenniumPoincareConjecture.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `reports/flawed_artifacts/MillenniumPvsNPSeparation.vacuous-inequality.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `reports/flawed_artifacts/MillenniumRiemannHypothesis.vacuous-symmetry.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `reports/flawed_artifacts/QuantumTopologicalModularTensorCategory.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `reports/flawed_artifacts/SheafTopologicalUnification.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `reports/flawed_artifacts/TwistorLatticeCorrespondence.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `reports/flawed_artifacts/UniversalCategorySheafBridge.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `SCOPE_UNDECLARED` | `reports/flawed_artifacts/YangMillsLatticeBoundary.vacuous-gap.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |
| LOW | `WITNESS_MISSING` | `reports/flawed_artifacts/DiscreteHodgeDecomposition.comment-only-green.lean:49` | `IsHarmonic` | predicate `IsHarmonic` is never applied to ground arguments or existentially witnessed |
| LOW | `WITNESS_MISSING` | `reports/flawed_artifacts/DiscreteHodgeTheoremSpec.laplacian1-identity.lean:22` | `harmonic0` | predicate `harmonic0` is never applied to ground arguments or existentially witnessed |
| LOW | `WITNESS_MISSING` | `reports/flawed_artifacts/DiscreteHodgeTheoremSpec.laplacian1-identity.lean:23` | `harmonic1` | predicate `harmonic1` is never applied to ground arguments or existentially witnessed |
| MEDIUM | `WITNESS_MISSING` | `reports/flawed_artifacts/EinsteinFieldEquations.vacuous-geometry.lean:41` | `SatisfiesEFE` | predicate `SatisfiesEFE` is never applied to ground arguments or existentially witnessed |
| MEDIUM | `WITNESS_MISSING` | `reports/flawed_artifacts/FiniteLatticeSpectralGravity.lean:12` | `latticeCurvatureValid` | predicate `latticeCurvatureValid` is never applied to ground arguments or existentially witnessed |
| MEDIUM | `WITNESS_MISSING` | `reports/flawed_artifacts/FiniteLatticeSpectralGravity.lean:16` | `planckPixelConstraint` | predicate `planckPixelConstraint` is never applied to ground arguments or existentially witnessed |
| MEDIUM | `WITNESS_MISSING` | `reports/flawed_artifacts/FiniteNavierStokesDissipation.lean:25` | `pressureRegularityValid` | predicate `pressureRegularityValid` is never applied to ground arguments or existentially witnessed |
| MEDIUM | `WITNESS_MISSING` | `reports/flawed_artifacts/FinitePvNPSeparationLattice.lean:12` | `circuitComplexityValid` | predicate `circuitComplexityValid` is never applied to ground arguments or existentially witnessed |
| MEDIUM | `WITNESS_MISSING` | `reports/flawed_artifacts/FiniteRiemannZetaLattice.lean:12` | `zetaZeroContainmentValid` | predicate `zetaZeroContainmentValid` is never applied to ground arguments or existentially witnessed |
| MEDIUM | `WITNESS_MISSING` | `reports/flawed_artifacts/FiniteYangMillsMassGapLattice.lean:12` | `wilsonPlaquetteBound` | predicate `wilsonPlaquetteBound` is never applied to ground arguments or existentially witnessed |
| MEDIUM | `WITNESS_MISSING` | `reports/flawed_artifacts/LatticeLearningWithErrors.lean:12` | `lweErrorBounded` | predicate `lweErrorBounded` is never applied to ground arguments or existentially witnessed |
| MEDIUM | `WITNESS_MISSING` | `reports/flawed_artifacts/LatticeLearningWithErrors.lean:16` | `lweSampleValid` | predicate `lweSampleValid` is never applied to ground arguments or existentially witnessed |
| LOW | `WITNESS_MISSING` | `reports/flawed_artifacts/MillenniumBirchSwinnertonDyer.vacuous-structure.lean:22` | `bsdRankEqual` | predicate `bsdRankEqual` is never applied to ground arguments or existentially witnessed |
| LOW | `WITNESS_MISSING` | `reports/flawed_artifacts/MillenniumBirchSwinnertonDyer.vacuous-structure.lean:27` | `tateShafarevichFinite` | predicate `tateShafarevichFinite` is never applied to ground arguments or existentially witnessed |
| MEDIUM | `WITNESS_MISSING` | `reports/flawed_artifacts/MillenniumHodgeConjecture.vacuous-cycles.lean:24` | `hodgeCycleRational` | predicate `hodgeCycleRational` is never applied to ground arguments or existentially witnessed |
| MEDIUM | `WITNESS_MISSING` | `reports/flawed_artifacts/MillenniumHodgeConjecture.vacuous-cycles.lean:29` | `cycleMapRealizationBounded` | predicate `cycleMapRealizationBounded` is never applied to ground arguments or existentially witnessed |
| MEDIUM | `WITNESS_MISSING` | `reports/flawed_artifacts/MillenniumNavierStokesSmoothness.lean:22` | `energyDissipationValid` | predicate `energyDissipationValid` is never applied to ground arguments or existentially witnessed |
| MEDIUM | `WITNESS_MISSING` | `reports/flawed_artifacts/MillenniumPoincareConjecture.lean:23` | `isSimplyConnected` | predicate `isSimplyConnected` is never applied to ground arguments or existentially witnessed |
| MEDIUM | `WITNESS_MISSING` | `reports/flawed_artifacts/MillenniumPoincareConjecture.lean:28` | `ricciFlowScalarValid` | predicate `ricciFlowScalarValid` is never applied to ground arguments or existentially witnessed |
| MEDIUM | `WITNESS_MISSING` | `reports/flawed_artifacts/MillenniumRiemannHypothesis.vacuous-symmetry.lean:23` | `onCriticalLine` | predicate `onCriticalLine` is never applied to ground arguments or existentially witnessed |
| MEDIUM | `WITNESS_MISSING` | `reports/flawed_artifacts/MillenniumRiemannHypothesis.vacuous-symmetry.lean:28` | `guinandWeilTraceBound` | predicate `guinandWeilTraceBound` is never applied to ground arguments or existentially witnessed |
| MEDIUM | `WITNESS_MISSING` | `reports/flawed_artifacts/TwistorLatticeCorrespondence.lean:20` | `twistorIncidenceValid` | predicate `twistorIncidenceValid` is never applied to ground arguments or existentially witnessed |
| MEDIUM | `WITNESS_MISSING` | `reports/flawed_artifacts/YangMillsLatticeBoundary.vacuous-gap.lean:13` | `wilsonActionBound` | predicate `wilsonActionBound` is never applied to ground arguments or existentially witnessed |
| MEDIUM | `WITNESS_MISSING` | `reports/flawed_artifacts/YangMillsLatticeBoundary.vacuous-gap.lean:17` | `yangMillsSylvesterInertiaTest` | predicate `yangMillsSylvesterInertiaTest` is never applied to ground arguments or existentially witnessed |

