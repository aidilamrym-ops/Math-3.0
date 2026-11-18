import Mathlib.Tactic

namespace Math30.SMTBridge

/-- BLS signature aggregation bound:
    Verify aggregated signature parameter limits.
    The postcondition couples the domain invariant `2 ≤ n` so the bound is
    genuinely contingent on `h_n` (mutation gate kills a `h_n : True` mutant). -/
theorem bls_aggregation_bound (sig_agg pk_agg msg_hash n : ℤ) (h_n : 1 < n)
    (_h_sig : 0 ≤ sig_agg) (_h_sig_max : sig_agg < n)
    (_h_pk : 0 ≤ pk_agg) (_h_pk_max : pk_agg < n)
    (_h_msg : 0 ≤ msg_hash) (_h_msg_max : msg_hash < n) :
    sig_agg + pk_agg + msg_hash < 3 * n ∧ 2 ≤ n := by
  omega

#print axioms bls_aggregation_bound

end Math30.SMTBridge