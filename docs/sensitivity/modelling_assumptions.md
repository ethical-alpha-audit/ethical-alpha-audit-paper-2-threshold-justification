# Modelling assumptions

This document discloses the full set of assumptions that the simulation
encodes. Any inference drawn from the simulation outputs is conditional
on these assumptions.

## 1. Synthetic threshold population

- **Sample size:** *n = 1,000* synthetic thresholds per scenario.
- **Latent true tier:** drawn from a Bernoulli distribution with parameter
  π_Primary (the base-rate prior for a threshold being latent-true Primary
  Safety). Tested base rates: π ∈ {0.05, 0.10, 0.20, 0.50}.
- **No covariates.** The synthetic threshold has only a latent true tier;
  no clinical, contextual, or technical covariates are modelled.
- **Independence.** Each threshold's latent tier is drawn independently;
  no correlation structure is modelled.

## 2. Rater model

- **Two independent raters.** Each rater classifies each threshold once.
- **Rater output alphabet:** {"Primary", "Secondary", "Uncertain"}.
- **Marginal Uncertain rate:** held constant at 2% per rater across all
  scenarios. This rate is held fixed so that κ variation across scenarios
  is driven by classification-error variation alone, not by Uncertain-rate
  variation. The 2% value is the smallest non-trivial Uncertain rate that
  still preserves the structural meaning of the default-to-Primary rule;
  with u = 0 the rule has no effect.
- **Symmetric error model:** when not Uncertain, the rater is correct with
  probability (1 − e) and produces the opposite tier with probability e.
  The two error directions are symmetric (no rater bias toward Primary or
  Secondary). The error rate e is calibrated by numerical inversion to
  achieve the target κ at the given base rate.
- **Per-rater independence:** the two raters are conditionally independent
  given the latent true tier; no shared bias is modelled.
- **Maximum achievable κ.** The Uncertain probability bounds the maximum
  achievable κ below 1.0. At π = 0.05, the model's analytical maximum κ
  is approximately 0.71 (with u = 0.02), which means at π = 0.05 a target
  κ of 0.80 cannot be exactly realised; the simulation converges to the
  ceiling. This is documented in the rater_model_verification.csv output.
- **No partial Uncertain.** A rater either is Uncertain or makes a
  classification; there is no continuous confidence parameter.

## 3. Adjudication

- **Default-to-Primary rule:** the adjudicated classification is Secondary
  *only if* both raters output "Secondary." Any output combination
  involving "Primary" or "Uncertain" produces an adjudicated classification
  of "Primary." This matches the main manuscript Methods §"Threshold
  classification."
- **No third-rater arbitration in the simulation.** The default-to-Primary
  rule is the entire adjudication procedure.
- **No iterative re-classification.** A threshold is classified once;
  reclassification on new evidence is not modelled.

## 4. Outcome computation

- **Misclassification rates** are computed pre-adjudication on the raw
  rater outputs.
- **Net-Primary, unsafe-Secondary, over-escalation rates** are computed
  post-adjudication.
- **Documentation burden** uses indicative time figures from the manuscript
  Supplementary Appendix C: 67.5 minutes for a Primary Safety record
  (midpoint of 45–90 minutes) and 17.5 minutes for a Secondary Operational
  record (midpoint of 10–25 minutes). Burden delta = 50 minutes per
  over-escalated threshold. These times are themselves indicative and
  pilot-testable; the simulation does not estimate them.

## 5. Monte Carlo

- **R = 100 replicates per scenario.** Independent random streams derived
  from a master seed via `numpy.random.SeedSequence`'s spawn mechanism.
- **MCSE** computed as sample SD / √R with ddof = 1.
- **Master seed:** declared in `inputs/seed.txt` and reported in
  `outputs/run_metadata.json`.

## 6. What is not modelled

- Any real institutional κ value.
- Coupling between κ on the Negative Harm Test and reliability of any
  individual TJS layer (L1–L6).
- Behavioural effects of documentation (ritualistic compliance,
  documentation-as-shield, tier gaming).
- Institutional-context effects (leadership commitment, deliberation
  infrastructure quality, feedback loops).
- Cross-institutional κ variation.
- Time evolution: the simulation is cross-sectional.
- Cost beyond the indicative documentation-time figures.
- Patient-level outcomes.
- Any of the failure modes the manuscript names for the TJS itself.

## 7. Implications for inference

Because of the assumptions above, the simulation outputs **support**
analytical claims of the form:

> *Under the stated modelling assumptions and at the specified κ value,
> the tier-classification rule produces governance outcomes of the
> following magnitudes.*

The simulation outputs **do not support the following claim types (including both affirmative formulations and explicit negations of validation claims):**

> *In real institutions, tier classifications produce these outcomes.*

> *The TJS framework has not been empirically validated.*

> *Empirical κ values of [X] are achievable.*

> *The Negative Harm Test is reliable.*

The latter set of claims requires the empirical pilot specified in the
manuscript Supplementary Appendix C addendum.
