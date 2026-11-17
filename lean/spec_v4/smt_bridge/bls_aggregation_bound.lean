import Mathlib.Tactic

namespace Math30.SMTBridge

/-- BLS signature aggregation bound:
    Verify aggregated signature parameter limits. -/
theorem bls_aggregation_bound (sig_agg pk_agg msg_hash n : ℤ) (h_n : 1 < n)
    (h_sig : 0 ≤ sig_agg) (h_sig_max : sig_agg < n)
    (h_pk : 0 ≤ pk_agg) (h_pk_max : pk_agg < n)
    (h_msg : 0 ≤ msg_hash) (h_msg_max : msg_hash < n) :
    sig_agg + pk_agg + msg_hash < 3 * n := by
  omega

#print axioms bls_aggregation_bound

end Math30.SMTBridge