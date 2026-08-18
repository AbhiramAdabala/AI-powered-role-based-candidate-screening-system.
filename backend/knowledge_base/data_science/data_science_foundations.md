# Applied Data Science Foundations

An experiment estimates causal impact by comparing randomized groups under a predeclared analysis plan. Sample size, minimum detectable effect, guardrail metrics, and stopping rules should be set before results are observed. Statistical significance does not guarantee practical value.

Missing data can be missing completely at random, missing at random conditional on observed variables, or missing not at random. The mechanism determines whether deletion, imputation, explicit missingness features, or sensitivity analysis is appropriate. Data leakage occurs when a feature contains information unavailable at decision time.

Precision and recall express different error costs. Threshold selection belongs to the product decision, not the model in isolation. Calibration matters when predicted probabilities drive resource allocation or risk decisions. Segment-level metrics can expose harmful average performance.

Analysis should begin with a decision, define its target metric and guardrails, and document assumptions. Reproducible work keeps transformations, evaluation code, and source definitions versioned so another analyst can audit the result.
