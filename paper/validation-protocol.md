# Proposed field-validation protocol

**Version 0.2.0 · 21 September 2026 · Prospective plan, not completed experiments**

The aim is to identify whether additional road measurements improve energy prediction and which additions are worth retaining. Freeze the comparison plan before examining the final evaluation set. This document does not prescribe a claim of success or a statistically justified sample size.

## 1. Define the intended use

Choose a vehicle class and a forecasting task. A four-wheel mapping vehicle and a scooter need separate body-motion assumptions. Specify whether the output is grade, effective resistance, battery terminal energy, displayed SOC, or a selected route. Do not substitute one outcome for another.

Define the intended operating envelope: speed, grade, surface types, GNSS visibility, weather, tyre configurations and direction of travel. Describe where the system will abstain or use a simpler fallback.

## 2. Establish independent reference measurements

| Target | Candidate reference | Controls needed |
|---|---|---|
| Road geometry | Independently surveyed profile or calibrated reference survey instrument | Document datum, survey uncertainty and road/lane correspondence; do not grade a reconstruction against the same measurements used to make it |
| Wheel resistance | Calibrated wheel-force/torque system or a justified controlled resistance test | Account for grade, speed, load, wind, braking, bearings and the scope of the effective coefficient |
| Battery energy | Calibrated, signed pack voltage/current logging | Validate units, timestamp alignment, current zero offset, integration bandwidth and treatment of auxiliaries |
| Surface labels | Independent inspection and recorded condition metadata | Record wetness and material without deriving labels from the model being evaluated |

Displayed SOC is generally too indirect to be the sole short-segment energy reference. A coarse percentage display, capacity uncertainty and battery-state estimation can obscure small differences.

Do not derive both calibration targets and evaluation targets from the same unverified force model. If a reference has material uncertainty, propagate it and report it alongside prediction error. A model-reference discrepancy cannot automatically be assigned to the proposed model.

## 3. Calibrate and record each run

Record timestamps, clock synchronization error, mounting transforms, antenna lever arms, tyre model/wear/pressure/temperature, vehicle mass, sensor identifiers and firmware, calibration version, weather and reference-instrument status. Log GNSS fix quality and outages rather than discarding them silently.

Separate static mounting error, sensor bias and suspension motion. Verify height datums before merging reference and production measurements. Keep an independent calibration set for choosing filter parameters, audio features, rejection thresholds and model hyperparameters.

Begin with geometry and energy measurements. Add acoustic sensing only when a numerical resistance target and its uncertainty can be defended. A coastdown label requires known driving/braking conditions; an EV that is regenerating is not freely coasting.

## 4. Select a pilot, then determine the confirmatory sample

Cover distinct routes rather than accumulating many near-identical windows on one road. Include constant-grade sections, changing grades, different surfaces, turning, GNSS obstruction, and both travel directions where the use case permits. Repeat on different days to measure variability.

A pilot estimates between-route and between-day variation, reference uncertainty, data loss and likely effect sizes. Use it to choose a confirmatory sample size for a predeclared confidence-interval width or practical benefit threshold. A fixed count of windows is not a substitute for independent routes or vehicles.

Any intended cross-vehicle claim requires held-out vehicles. Any intended tyre-transfer claim requires held-out tyre configurations. If these are unavailable, limit the conclusion to the tested setup.

## 5. Prevent leakage

Assign whole routes, drives, days and appropriate vehicle groups to training/calibration/validation/test partitions before window extraction. Adjacent audio windows and repeated observations of the same road are correlated. Keep the final test routes separate from tuning decisions.

Choose split boundaries according to the claim. Holding out a day on a known route tests temporal transfer; holding out a route tests geographic transfer. Report both separately when both are studied. A single random sample split cannot establish either.

Keep all transformations learned from data—including normalization, feature selection and probability calibration—inside the training process. Record every final-test exclusion and its reason.

## 6. Compare incremental baselines

| ID | Inputs | Question answered |
|---|---|---|
| B0 | Fixed DEM profile; fixed resistance; declared vehicle model | Baseline prediction quality |
| B1 | Proposed geometry; same resistance and vehicle model | Incremental value of geometry |
| B2 | B1 plus tyre/speed/pressure/weather covariates for resistance | Value of context without audio |
| B3 | B2 plus acoustic features | Incremental value of sound |
| B4 | Add optional LiDAR or repeated-observation aggregation to the chosen baseline | Incremental value of each additional measurement |
| Reference-geometry diagnostic | Independent geometry fed to the same energy model | Whether geometry is actually the limiting error source |

Use identical trips, speed inputs, parameter-calibration budgets and coverage rules for paired comparisons. Report performance both on common valid coverage and on all eligible trips with the declared fallback. Otherwise a method can appear better merely by rejecting difficult roads.

Do not change the geometry model, drivetrain efficiency and audio model simultaneously and attribute the combined difference to one sensor. Record each ablation.

## 7. Distinguish retrospective and prospective evaluation

In a retrospective experiment, observed speed traces can isolate geometry/resistance effects. In a prospective route forecast, only speed, weather and other information available before departure may be used. Report these as different experiments.

Energy prediction does not alone establish better route selection. Route-choice evaluation also needs competing routes, comparable operating conditions, uncertainty in unchosen-route outcomes, travel-time trade-offs and cumulative battery feasibility.

## 8. Metrics and reporting

| Outcome | Report |
|---|---|
| Geometry | Grade MAE/RMSE in degrees and percentage points; vertical bias; along-track error; coverage and rejection rate |
| Resistance | Bias and MAE/RMSE in coefficient units against a declared reference; reference uncertainty; results by tyre/vehicle/condition |
| Surface classification | Per-class precision/recall, macro-F1, confusion matrix and held-out-domain performance; this is separate from resistance accuracy |
| Energy | Bias, MAE and paired error change in Wh/trip; Wh/km; coverage; performance by route, vehicle and weather |
| Intervals | Empirical coverage and width of predictive intervals, including whether abstention is calibrated |
| Cost | Equipment and calibration cost, correction/processing services, repeat collection and maintenance cost per usable kilometre |

Use route/day clusters or a hierarchical analysis reflecting the actual sampling design for uncertainty intervals. Treating every metre or overlapping audio window as an independent observation would make intervals spuriously narrow. Report the experimental unit and resampling procedure.

Relative energy error is unstable near zero net energy, including regenerative descents. Always retain absolute Wh errors and state the denominator/exclusion rule before analysis.

## 9. Decision rules

Before final testing, define a minimum useful reduction in energy error based on the application and reference uncertainty. Retain a sensor only when its incremental benefit is supported within the operating envelope and worth its burden.

Publish negative or negligible results, failed transfers and coverage losses. A reasonable stopping result may be that improved geometry helps but audio does not, or that a simpler model already meets the task's requirements.

## 10. Reproducibility record

Release, where permitted, calibration files, de-identified observation data, route/vehicle split definitions, processing code, model settings, rejection counts, reference uncertainty, all aggregate metrics and the exact code/data versions. Avoid publishing identifiable travel traces or incidental raw audio unnecessarily.

Clearly separate raw observations, derived labels, model predictions and synthetic examples. Preserve upstream dataset terms. The current repository supplies only synthetic calculations and an illustrative data contract; none of these field steps has been completed.
