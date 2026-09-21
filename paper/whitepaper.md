# Road Geometry and Surface-Resistance Mapping for EV Energy Prediction

## A Sensor Architecture and Validation Framework

**Author:** Ajinkya Kawade

**Version:** 0.2.0 · **Revision date:** 21 September 2026

**Original concept draft:** July 2026

**Status:** Independent technical whitepaper; proposed architecture plus synthetic numerical demonstration. No field validation or peer review is claimed.

[Plain-language overview](../README.md) · [Validation protocol](validation-protocol.md) · [Source notes](references.md) · [Revision provenance](provenance.md)

## Abstract

Road geometry and tyre–surface interactions can influence electric-vehicle energy use, but the usefulness of measuring them at finer spatial scales depends on vehicle dynamics, sensor uncertainty and the energy model. This whitepaper proposes a mapping-fleet architecture combining GNSS and inertial observations with optional LiDAR, barometry and tyre audio. It separates the estimation of road geometry from the estimation of vehicle-conditioned resistance. Body pitch is distinguished from road grade; acoustic surface recognition is treated as a possible predictor requiring independent resistance labels. The energy formulation distinguishes signed wheel work, conversion losses, regeneration limits and auxiliary consumption. A reproducible synthetic experiment examines coarse profile sampling across 324 parameter combinations, with analytical tests and a numerical refinement check. These calculations illustrate a mechanism and do not demonstrate sensor accuracy, field energy savings or superiority to a particular elevation product. The contribution is an auditable design and validation framework: defined quantities, source-linked assumptions, uncertainty propagation, a proposed segment record, and staged comparisons against simpler baselines. Field measurements are required to determine whether additional sensors produce transferable improvements at a defensible cost.

**Keywords:** electric vehicles; road grade; mobile mapping; rolling resistance; energy prediction; uncertainty; sensor fusion.

## 1. Problem definition and boundaries

The research question is whether additional road information reduces **out-of-sample battery-energy prediction error**, and whether the improvement is worth the sensing and maintenance effort.

A terrain map, a road-surface profile and an energy-cost map describe different things. A road may lie on a bridge, in a cutting or beneath vegetation. Copernicus DEM is a surface model including structures and vegetation; its GLO-30 product has approximately 30-m spacing. SRTM also has a global 1-arc-second product. Neither grid spacing nor a product-wide vertical statistic establishes the accuracy of a particular road segment. [R1](references.md#r1--copernicus-elevation-product), [R2](references.md#r2--srtm-product)

This paper does not assume that all navigation services use one elevation source or ignore grade. It also does not establish that elevation resolution is the dominant cause of range-prediction error. Speed, stops, wind, load, thermal conditions, auxiliary demand and battery behaviour can be equally important confounders.

“Micro-gradient” here means **short longitudinal changes in road slope over metre-to-tens-of-metres scales**. It is a working project term, not a claim that these scales are absent from existing surveying. It must not be confused with pavement microtexture, nor with high-frequency tyre deformation that a rigid point-mass model cannot describe.

| Quantity | Meaning | What it is not |
|---|---|---|
| Longitudinal grade | Height change per horizontal distance along the road's plan-view centreline | Chassis pitch during acceleration |
| Crossfall/bank | Transverse orientation of the road plane | Vehicle body roll or a motorcycle's lean |
| Surface class | A label such as asphalt or concrete, with confidence and context | A measured numerical rolling-resistance coefficient |
| Effective resistance | A fitted, vehicle-conditioned loss term under stated assumptions | A universal property of a road |
| Battery terminal energy | Integral of signed voltage × current over a trip | A direct measurement of usable battery capacity or displayed SOC |

## 2. Related work and the proposed contribution

| Earlier work | Relevant finding or capability | Implication for this project |
|---|---|---|
| Gupta et al., 2020 [R3](references.md#r3--mobile-road-grade-estimation) | Mobile grade estimation using smartphone sensors and aggregation; reported 90% of errors below 0.3° on an approximately 9-km route | Mobile grade mapping is established related work; reproduce an appropriate baseline before claiming improvement |
| Wood et al., 2014 [R4](references.md#r4--road-grade-and-vehicle-energy) | Combined elevation information, driving traces and vehicle models to study grade-related energy use | Evaluate energy as well as geometric accuracy |
| Andersen et al., 2015 [R5](references.md#r5--rolling-resistance-measurement-and-modelling) | Measurement and modelling context for rolling resistance | Independent labels and a declared measurement method are necessary |
| Yang et al., 2024 [R6](references.md#r6--acoustic-road-terrain-classification) | Tyre-audio classification across several terrain categories | Supports investigating audio features; classification does not establish numerical resistance |
| Valhalla documentation [R9](references.md#r9--routing-architecture) | Runtime costing uses road attributes | A working integration requires engineering beyond publishing a JSON example |

The proposed contribution is the **integration and evaluation framework**: geometry and resistance are kept distinct; uncertain observations have provenance; energy effects are tested under explicit assumptions; and incremental sensor value is measured against simpler alternatives. No claim of first invention of GNSS/IMU/LiDAR fusion, acoustic road classification or energy-aware routing is made. A wider literature and patent search would be needed to assess novelty.

Three hypotheses guide future work:

1. Better road-grade observations improve held-out energy predictions beyond a fixed DEM baseline when the same vehicle model and speed information are used.
2. Acoustic features add predictive information about independently measured effective resistance beyond tyre, speed, pressure and weather covariates.
3. LiDAR and repeated fleet observations add enough accuracy or coverage to justify their incremental cost.

A finding of negligible improvement is informative. The [validation protocol](validation-protocol.md) specifies comparisons without presupposing success.

## 3. Physical model

### 3.1 Coordinates, grade and force

Let $x$ be horizontal chainage along the plan-view road path, $z(x)$ its height, and $s$ three-dimensional path length. On a straight local segment:

$$
q=\frac{dz}{dx},\qquad
\theta=\arctan q,\qquad
\mathrm{grade}_{\%}=100q,\qquad
ds=\sqrt{dx^2+dz^2}.
$$

Grade ratio, grade percentage and slope angle are distinct. For example, a 10% grade means $q=0.10$ and $\theta\approx5.71^\circ$.

A simplified longitudinal tractive-force balance for forward travel is

$$
F_{\mathrm{tr}}=
m_{\mathrm{eff}}a+
mg\sin\theta+
C_{rr,\mathrm{eff}}\,mg\cos\theta+
\frac12\rho C_dA\,u|u|+
F_{\mathrm{other}}.
$$

Here $v=ds/dt$ is ground speed, $a=dv/dt$, and $u=v-w_\parallel$ is a one-dimensional relative-air speed with positive $w_\parallel$ denoting tailwind. The signed drag expression allows a sufficiently strong tailwind to assist motion. Crosswind aerodynamics require a fuller model. $m_{\mathrm{eff}}$ can include equivalent rotational inertia.

The normal-load approximation $N\approx mg\cos\theta$ neglects vertical curvature, banking and suspension dynamics. It should not be used without qualification at sharp crests, dips or on rough roads. Likewise, an effective resistance coefficient must have a stated scope: losses absorbed into it must not be counted again in $F_{\mathrm{other}}$.

### 3.2 Wheel power, battery energy and regeneration

Wheel power is $P_w=F_{\mathrm{tr}}v$. Positive power propels the vehicle; negative power requires braking to maintain the specified motion.

For constant driving efficiency $\eta_d$, regeneration efficiency $\eta_r$, auxiliary demand $P_{\mathrm{aux}}$, and a **battery-side** recovered-power cap $P_{\mathrm{cap}}$, the demonstration uses

$$
P_{\mathrm{bat}}=
\begin{cases}
P_w/\eta_d+P_{\mathrm{aux}}, & P_w\ge0,\\
-\min(\eta_r(-P_w),P_{\mathrm{cap}})+P_{\mathrm{aux}}, & P_w<0.
\end{cases}
$$

$$
E_{\mathrm{bat}}=\int P_{\mathrm{bat}}\,dt.
$$

Positive battery energy means net discharge. Mechanical braking not accepted by regeneration becomes friction-brake heat. Auxiliary demand continues during braking. The cap applies to recovered traction power before auxiliary demand is deducted.

This is a simplified terminal-energy accounting model. A practical predictor needs efficiency maps, motor torque/power constraints, battery temperature and SOC-dependent charge acceptance, braking strategy and usable capacity. Infeasible speed traces must be flagged. An energy divided by capacity calculation is only an approximate SOC conversion, not a battery-state estimator.

### 3.3 Why finer grade information may—or may not—matter

Gravitational work satisfies

$$
\int mg\sin\theta\,ds=mg(z_{\mathrm{end}}-z_{\mathrm{start}}).
$$

Thus, a lossless vehicle with unlimited reversible energy recovery expends no net gravitational energy on a closed elevation loop. Sampling an incline more finely does not change that identity.

Interior grade changes can nevertheless affect battery energy through conversion losses, regeneration limits, friction braking, speed choices, path length and power-dependent efficiency. A route can also have a different peak power requirement without a proportionate change in total energy. The size of the effect must be computed and measured; this project does not infer it from spatial resolution alone.

### 3.4 Banking and cornering

Road banking changes the orientation of contact forces and can change tyre loading and slip. It does not create an automatic extra uphill energy term. In ideal uniform circular motion, centripetal force is perpendicular to velocity and does no work. Real cornering can incur losses, but these require a tyre/dynamics model or independent measurements. [R8](references.md#r8--circular-motion-mechanics)

The vector containing only pitch and bank angles in the earlier draft is replaced by geometric quantities with defined frames. A pair of angles is not a gravitational-force vector. The included demonstration excludes cornering and banking; storing a bank angle does not imply its energy contribution has been validated.

## 4. Proposed sensing architecture

Sensor rates below are **initial design targets for a pilot**, not demonstrated performance or mandatory purchasing specifications. Select hardware after setting a spatial-error budget and testing the mounting arrangement.

| Measurement | Initial acquisition target | Role and limitation |
|---|---|---|
| GNSS position/velocity | Receiver-supported 5–20 Hz, plus raw observations if available | Position/height constraints; record fix state, corrections age, covariance and outages |
| Rigidly mounted 6-axis IMU | Approximately 100–200 Hz | Specific force and angular rate; requires bias, alignment and temperature calibration |
| Wheel speed and longitudinal dynamics | Available validated rate, preferably tens of Hz | Helps separate acceleration from gravity; wheel slip and CAN latency need treatment |
| Barometric pressure + temperature | Approximately 1–10 Hz | Optional relative-height/weather information; pressure is affected by weather and airflow |
| LiDAR | Approximately 10–20 frames/s, with per-point timing | Optional local road plane and crossfall; requires road segmentation, de-skewing and extrinsic calibration |
| Wheel-proximate microphone | 44.1 or 48 kHz raw audio with timestamps | Optional surface features; no direct resistance label |
| Battery voltage/current or wheel force/torque | Sufficient bandwidth to integrate the selected test dynamics | Independent energy/resistance reference with calibration and uncertainty |
| Tyre/load/environment metadata | At each run, with changes logged | Tyre model, wear, pressure, temperature, vehicle mass, weather and configuration |

GNSS precision specifications do not guarantee road-surface accuracy. For example, the u-blox F9P data sheet reports different horizontal and vertical statistics under stated baseline/antenna conditions; these cannot be read as an unconditional ±2-cm bound in motion. [R7](references.md#r7--rtk-receiver-specification)

Raw sample spacing $v/f_s$ is not the same as independent spatial resolution. At 15 m/s, a 200-Hz IMU produces samples 0.075 m apart, but sensor dynamics, filtering, chassis motion and timing errors can make useful resolution much coarser. A proposed 5-ms timing error already corresponds to 0.075 m of along-track misalignment at that speed.

Air density should not be reconstructed from a stored historical pressure alone. A first dry-air approximation is $\rho=p/(R_dT)$; humidity and contemporary weather may matter. Historical barometry belongs in observation provenance, while route forecasts should use relevant environmental inputs.

### 4.1 Processing relationships

~~~mermaid
flowchart TD
    K["GNSS, IMU and speed"] --> F["Calibration and trajectory estimation"]
    L["Optional LiDAR"] --> F
    F --> G["Road geometry with uncertainty"]
    A["Audio and tyre context"] --> C["Candidate resistance predictor"]
    E["Independent force or energy reference"] --> C
    C --> V["Held-out validation"]
    G --> V
    V --> D["Versioned segment records"]
    D --> R["Candidate-route energy scoring"]
~~~

The acoustic path remains experimental. Geometry may be useful even if audio fails to add predictive value. LiDAR can be introduced only after evaluating a lower-cost GNSS/IMU baseline.

### 4.2 Road attitude versus body attitude

An IMU measures its own motion, not the road plane. Body pitch contains road slope, suspension pitch, mounting offset and dynamic effects. Acceleration and braking can rotate the body relative to the road, a problem also discussed in existing mobile-grade work. [R3](references.md#r3--mobile-road-grade-estimation)

A future implementation should calibrate sensor-to-body transforms and model or independently observe body-to-road attitude. An IMU/GNSS filter alone does not guarantee that these quantities are separately observable. Useful checks include repeat traversals, low-dynamic windows, independent survey profiles and, where justified, LiDAR road-plane estimates.

On two-wheelers, rider movement and lean add further differences from a rigid four-wheel mapping platform. Transfer to scooters therefore requires its own calibration and evaluation.

## 5. Estimation and uncertainty

### 5.1 An implementable specification for future fusion

A possible navigation state is

$$
\mathbf{x}=
[\mathbf{p},\mathbf{v},\mathbf{q},\mathbf{b}_a,\mathbf{b}_g,b_p],
$$

containing position, velocity, attitude quaternion, accelerometer and gyroscope biases, and barometer bias. Road-plane orientation and body-to-road motion require additional states or measurements with explicit observability assumptions.

An error-state filter or an offline smoother could propagate IMU observations and use GNSS position/velocity, barometry and road-plane residuals. A generic measurement update has the form

$$
\mathbf{y}_k=\mathbf{h}(\mathbf{x}_k)+\boldsymbol{\nu}_k,
\qquad
\boldsymbol{\nu}_k\sim(0,\mathbf{R}_k).
$$

This is a design outline, not an implemented EKF. A reproducible implementation must specify frames, process equations, state/error dimensions, sensor models, noise parameters, timing, gates, initialization and failure recovery. Gyroscopes provide angular rate; accelerometers provide specific force. “Pitch acceleration” is not a substitute for either measurement model.

Before merging heights:

1. Correct antenna/IMU/LiDAR lever arms using attitude and measured mounting geometry.
2. Account for ride height and suspension motion when relating sensor height to pavement height.
3. Reconcile vertical datums. Ellipsoidal height $h$ and orthometric height $H$ satisfy $H=h-N$, with geoid separation $N$. Copernicus uses EGM2008; do not silently compare it with ellipsoidal GNSS heights. [R1](references.md#r1--copernicus-elevation-product)
4. Treat bridges, tunnels, parallel roads, poor GNSS fixes and low-confidence map matches as explicit ambiguity or missing data.
5. Retain quality flags; do not fill outages with apparently measured values.

### 5.2 Differencing can amplify elevation noise

For a local grade estimate $q=(z_2-z_1)/\Delta x$, neglecting horizontal error,

$$
\sigma_q^2\approx
\frac{\sigma_{z_1}^2+\sigma_{z_2}^2-2\operatorname{Cov}(z_1,z_2)}
{(\Delta x)^2}.
$$

For illustration only, suppose each height has **independent 1σ uncertainty of 0.02 m**. This is a hypothetical input, not a reinterpretation of the manufacturer's median statistic.

| Horizontal separation | Grade uncertainty, 1σ, in percentage points |
|---|---:|
| 1 m | 2.828 |
| 10 m | 0.283 |
| 30 m | 0.094 |

Longer differencing windows reduce independent noise but suppress short features. Real errors can be correlated; bias, horizontal uncertainty and changing satellite geometry require separate treatment. More samples do not remove a common bias, and spatial smoothing creates correlation between neighbouring outputs.

### 5.3 Grade error can masquerade as resistance

At small angles, a persistent $0.1^\circ$ grade bias corresponds to approximately 0.001745 grade ratio. For a 1,500-kg vehicle it changes the gravity-force estimate by about 25.7 N. Over one kilometre that is about 7.13 Wh of mechanical work, or 7.92 Wh at 90% driving efficiency if propulsion remains positive. These are illustrative calculations, not measured project errors.

In a residual resistance calculation, the same angular bias can cause a coefficient error of approximately 0.001745. Relative to an assumed coefficient of 0.010, that is about 17.5%. This explains why an apparently plausible resistance map can instead contain grade-estimation error.

## 6. Surface resistance and acoustic inference

### 6.1 Identifiability comes before machine learning

With an independent tractive-force estimate and declared loss model, one possible residual estimator is

$$
\widehat C_{rr,\mathrm{eff}}=
\frac{F_{\mathrm{tr}}-m_{\mathrm{eff}}a-mg\sin\theta
-F_{\mathrm{aero}}-F_{\mathrm{other}}}
{mg\cos\theta}.
$$

Motion and geometry alone generally do not identify resistance when the applied driving force is unknown. Inferring wheel force from battery power also introduces efficiency and auxiliary-load uncertainty. At low speed, converting power to force by division by speed is ill-conditioned; suitable exclusion thresholds must be justified.

A controlled coastdown or wheel-force experiment can provide calibration information, but its braking/regen state, wind, grade and mechanical losses must be independently accounted for. Ordinary deceleration on an EV is not automatically a free-rolling resistance measurement. The measurement/model literature should inform the chosen reference procedure. [R5](references.md#r5--rolling-resistance-measurement-and-modelling)

### 6.2 Separate classification from numerical prediction

Published work supports tyre-audio terrain classification. It does not validate the earlier draft's precise sound-to-$C_{rr}$ claim. [R6](references.md#r6--acoustic-road-terrain-classification)

The proposed pipeline is:

1. Label surface categories independently, and record tyre, pressure, load, speed, temperature and wetness.
2. Compare acoustic features against a baseline using those covariates alone.
3. Train a numerical resistance model only where independent force/energy labels exist.
4. Evaluate on whole held-out routes, recording days, tyres and vehicles; split before creating overlapping audio windows.
5. Return calibrated intervals or abstain when conditions are outside the training domain.

MFCCs and log-mel spectrograms are candidate representations, not evidence that the target is recoverable. A high surface-classification score cannot be substituted for a resistance-error metric.

### 6.3 A conditional quantity, not one permanent road number

A useful model would have the form

$$
C_{rr,\mathrm{eff}}=
f(\mathrm{surface},\mathrm{tyre},\mathrm{pressure},\mathrm{load},
\mathrm{speed},\mathrm{temperature},\mathrm{wetness},\mathrm{vehicle}).
$$

Geometry may be comparatively stable, while wetness, tyre configuration and weather change. Store reusable road features separately from vehicle-specific predictions and transient observations. An uncalibrated acoustic record should contain a null resistance estimate, not an invented coefficient.


## 7. Segment data and routing integration

### 7.1 A proposed sidecar, not a working routing extension

The July JSON example is replaced by a [documented segment record](../data/README.md). The example is synthetic. It carries chainage, elevation samples, units, datum, direction, uncertainty semantics, calibration references and evidence status. Missing observations are represented explicitly.

A future implementation can store this information in a versioned sidecar database and associate it with directed graph segments. Valhalla provides dynamic costing, but this repository does not implement a new cost class or tile extension. [R9](references.md#r9--routing-architecture)

Graph associations must include a graph-build identity and enough geometry/version information to detect stale joins. A bare edge number is not treated as a permanent road identity. Valhalla exposes several build/data identifiers; the proposed integration additionally records the exact graph snapshot digest and rematches after relevant changes. [R10](references.md#r10--routing-graph-versioning)

For reverse traversal, reorder the profile and change the sign of longitudinal grade. Do not simply reuse a forward-direction energy estimate. Crossfall conventions, lane choice and carriageway identity also need explicit handling.

### 7.2 Start with candidate-route scoring

The lowest-complexity proposed integration is:

1. Obtain several feasible candidate routes from an existing router.
2. Match each route to available geometry and condition observations, with a declared fallback for missing coverage.
3. Apply the same vehicle model and forecast speed/weather inputs to every candidate.
4. Compute signed battery energy and track cumulative energy feasibility, reserve requirements and any charge-acceptance assumptions.
5. Compare predictions with measured trips, and only then consider deeper routing integration.

This procedure does not guarantee the globally minimum-energy route: the optimum may be absent from the candidate set. Report that limitation.

Regeneration can create a negative signed-energy contribution on an edge. Such values cannot simply be inserted as ordinary non-negative Dijkstra costs. Clipping all negative energy to zero changes the objective. A future global solution would need a suitable algorithm and battery-state/resource constraints; no such solver is included here.

Uncertainty should also be evaluated at route level. Adding independent per-segment variances is generally inappropriate when elevation, calibration and weather errors are correlated.

## 8. Reproducible synthetic demonstration

### 8.1 Purpose

The included code tests how the **representation of a known profile** affects one simplified energy calculation. It does not test the proposed sensors, a Kalman filter, an acoustic model, real elevation data or a routing engine.

The numerical profile is

$$
z(x)=0.005x+A\left[
\sin\left(\frac{2\pi x}{40}\right)
+0.35\sin\left(\frac{2\pi x}{75}\right)
\right],\qquad 0\le x\le1200\ \mathrm{m}.
$$

The deliberately undulating profile is a stress case, not a surveyed road or a claim about typical road-design geometry. Both endpoints are held exact for every reconstruction. The net rise is 6 m.

The comparison samples this function on coarser horizontal grids and connects samples linearly. This is **not a simulation of satellite sensing, raster interpolation, canopy error or a particular DEM processing chain**.

### 8.2 Declared assumptions

| Parameter | Values or treatment |
|---|---|
| Vehicle mass | 1,500 kg, illustrative |
| Constant rolling coefficient | 0.010, illustrative |
| Drag area $C_dA$ | 0.65 m², illustrative |
| Air density | 1.225 kg/m³ |
| Driving/regeneration efficiency | 0.90 / 0.65 |
| Auxiliary demand | 300 W |
| Amplitude parameter $A$ | 0, 0.25, 0.75 m |
| Constant road-path speed | 8, 15, 25 m/s |
| Battery-side regeneration cap | 0, 5, 20 kW |
| Coarse sampling | 5, 10, 30 m |
| Coarse-grid offsets | 0, 0.25, 0.5, 0.75 of each grid spacing |
| Numerical reference | 0.5-m point sampling; checked against 0.25 m |
| Excluded | Wind, acceleration, cornering, vertical dynamics, sensor noise, efficiency maps, motor drive limits and SOC evolution |

These choices are controlled model inputs, not fitted parameters for any named car or scooter. The sweep contains $3\times3\times3\times3\times4=324$ comparisons. All cases are published in [sensitivity.csv](../results/sensitivity.csv).

For each straight segment, the implementation uses

$$
\Delta s=\sqrt{\Delta x^2+\Delta z^2},\qquad
\Delta t=\Delta s/v,
$$

$$
W_g=mg\Delta z,\qquad
W_{rr}=mgC_{rr}\Delta x,\qquad
W_{\mathrm{aero}}=\frac12\rho C_dA v^2\Delta s.
$$

It then converts the sum of wheel work to battery energy using Section 3.2. This preserves gravitational work exactly for a given pair of endpoints. Path length and traversal time vary slightly with reconstruction; the resulting differences in drag and auxiliary energy are retained and reported. There are no fitted acoustic or measured resistance values.

### 8.3 One disclosed example

For $A=0.75$ m, $v=15$ m/s and a 5-kW regeneration cap, the numerical reference uses approximately **229.791 Wh**.

| Coarse spacing | Mean coarse minus reference energy | Range across the four grid offsets |
|---|---:|---:|
| 5 m | −4.710 Wh | −5.784 to −4.289 Wh |
| 10 m | −18.956 Wh | −20.333 to −16.634 Wh |
| 30 m | −100.165 Wh | −100.354 to −99.879 Wh |

Negative differences mean the coarse representation predicts less energy **within this model**. The ranges are deterministic alignment sensitivity, not confidence intervals. The large difference in the 30-m example reflects the deliberately oscillating test profile and the chosen losses; it is not a claimed mapping-system improvement.

![Synthetic profile, grade and energy sensitivity](../figures/sampling_energy.svg)

The full [generated results](../results/README.md) include other amplitudes, speeds and regeneration limits. The amplitude-zero case is a constant 0.5% grade control, not a level road. Its energy is invariant to sampling spacing and grid offset within numerical precision.

### 8.4 Verification and limits

Nine analytical/physical tests check the level-road solution, the lossless closed-hill limit, endpoint gravitational work, conversion losses, regeneration caps, zero regeneration, the full energy balance, constant-grade invariance and invalid inputs.

Refining the reference from 0.5 m to 0.25 m changes computed energy by at most **0.044376 Wh** across the 27 reference combinations. This is a numerical consistency check, not proof that the physical model is accurate.

The simplified normal load can be inaccurate on short vertical curves, especially at the higher example speeds. The model also lacks motor power feasibility and battery charge-acceptance dynamics. Therefore, even a perfectly reconstructed version of this synthetic profile is not a validated real-road energy prediction. Adding realistic sensor errors and vertical dynamics is a future experiment, not an unreported implementation.

To reproduce numerical results from the repository root:

~~~bash
python code/run_demo.py
python -m unittest discover -s tests -v
~~~

The [parameters file](../results/parameters.json) records all sweep inputs. Figure generation is optional and separate from the standard-library numerical calculation.

## 9. Field evaluation needed to establish value

The proposed [field-validation protocol](validation-protocol.md) keeps three questions separate:

1. **Geometry:** How accurately are the road profile and grade reconstructed relative to an independent survey?
2. **Resistance:** Does a conditional resistance estimate agree with an independently justified reference and generalise across conditions?
3. **Energy:** Does either improvement reduce held-out trip-energy error with the same vehicle model, speed information and coverage policy?

A hierarchy of baselines is needed: DEM plus constant resistance; improved geometry plus the same constant resistance; geometry plus non-acoustic contextual resistance; then optional acoustic and LiDAR additions. This prevents an improvement from being incorrectly credited to the most complex sensor combination.

Primary energy outcomes should include signed bias and absolute error in Wh/trip, with uncertainty clustered by independent route/day or appropriately defined experimental unit. Report Wh/km and relative errors with care when net energy is small or negative. Grade should be reported both in angular units and grade percentage points, together with coverage and rejection rates.

Separate a retrospective experiment using observed speed from a prospective forecast using only information available before departure. A system evaluated with future speed or weather is not yet a deployable route predictor.

Cost evaluation should include equipment, mounting/calibration labour, correction services, repeated surveying, data processing and map maintenance per usable kilometre. No hardware cost or return-on-investment claim is made here.

## 10. Limitations and next implementation steps

The proposal's unresolved risks include uncertain body-to-road attitude, poor GNSS visibility, datum mismatch, timestamp error, biased reference labels, transfer between tyres/vehicles, weather drift, incomplete map coverage and routing-state complexity. A densely sampled but biased map can make energy predictions worse.

The next useful implementation sequence is:

1. Build a timestamped GNSS/IMU/speed logger and a calibrated geometry baseline.
2. Validate geometry independently before fitting any resistance model.
3. Obtain a defensible force or terminal-energy reference and quantify its uncertainty.
4. Evaluate added surface/context features; retain audio only if it adds held-out value.
5. Implement candidate-route scoring with explicit missing-data and energy-feasibility handling.
6. Publish field data, calibration files and measured outcomes with appropriate permissions and data terms.

None of these future stages is represented as completed by the synthetic code. Expanding the instrument list is not itself a scientific result.

## 11. Publication, licensing and citation

This version is an **independent technical whitepaper with a synthetic demonstration**. It should be described that way in a research portfolio. It contains no verified field-performance claim or peer-review record.

The repository preserves its original CC0 dedication. CC0 does not determine patent novelty, priority, freedom to operate or the rights in other people's work. This revision makes no such determination. Future use of OpenStreetMap or other external datasets must respect their own terms. [R11](references.md#r11--cc0-scope), [R12](references.md#r12--openstreetmap-data-terms)

The July draft remains available in Git history. September additions are dated as a new version. [Authorship and AI assistance](provenance.md) are disclosed.

**Suggested citation:** Kawade, A. (2026). *Road Geometry and Surface-Resistance Mapping for EV Energy Prediction: A Sensor Architecture and Validation Framework* (Version 0.2.0). Independent technical whitepaper with synthetic demonstration. GitHub.

The complete [reference list and source notes](references.md) and [BibTeX entries](../references.bib) accompany this paper.
