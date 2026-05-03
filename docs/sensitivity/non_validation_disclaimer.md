# Non-validation disclaimer

This repository contains a **computational sensitivity analysis** supporting
the manuscript *Beyond "Magic Numbers": A Threshold Justification Stack for
Clinical AI Governance*. The simulation models how variation in inter-rater
agreement (κ) on the Negative Harm Test would propagate to tier-classification
outcomes under stated modelling assumptions.

**This simulation is not a validation of the Threshold Justification Stack.**

**The simulation does not estimate κ values for any real institutional setting.**

**The simulation makes no claim of applicability to any real institutional context.**

The κ tolerance regime derived from the simulation is *normative-from-analysis*:
it specifies how the tier-classification rule would behave under the stated
modelling assumptions, not how it does behave in practice. The regime is
replaceable by empirical pilot data when available, and that empirical pilot —
not this simulation — is the validation step.

Use of this repository for any claim of empirical validation of the TJS
framework is unsupported. The simulation **does not substitute for human
inter-rater validation** of the Negative Harm Test or of any other component
of the TJS specification.

## What the simulation does

- Models how a tier-classification rule's reliability (κ) propagates to
  governance-outcome quantities (misclassification rates, unsafe-Secondary
  rate, over-escalation rate, documentation burden) under stated rater-model
  assumptions.
- Quantifies the analytical consequences of the manuscript's prespecified
  falsification condition (κ < 0.40) and illustrative target benchmark
  (κ = 0.60), under those modelling assumptions.
- Provides Monte Carlo standard errors on every point estimate.

## What the simulation does not do

- Does not estimate κ values for any institution, rater pool, or
  threshold population.
- Does not establish that the TJS framework reduces clinical harm.
- Does not establish that documentation produces deliberation.
- Does not model the behavioural effects of documentation (ritualistic
  compliance, documentation-as-shield, tier gaming) as outcomes; these are
  acknowledged in the manuscript as failure modes of TJS itself.
- Does not couple κ on the Negative Harm Test with reliability of the
  individual TJS layers (L1–L6).
- Does not model institutional context, leadership commitment, or
  feedback-loop dynamics.

## What the simulation supports

The simulation supports the manuscript's analytical claim that, *if* a
hypothesised κ regime obtains, *then* certain governance outcomes follow under
the modelling assumptions. The hypothetical-conditional form is essential:
the simulation provides a sensitivity-analysis-derived normative recommendation,
not an empirical estimate.

The pilot protocol described in Supplementary Appendix C of the manuscript is
the empirical test against which this simulation's normative regime will be
evaluated.
