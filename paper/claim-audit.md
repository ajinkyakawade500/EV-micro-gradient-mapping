# Audit of the July draft

This records substantive changes from the [original draft](https://github.com/ajinkyakawade500/EV-micro-gradient-mapping/blob/63d8c3819836abadf38ca3d4c4fbe695e930bc81/README.md). It separates corrected claims from prospective design choices.

| Earlier claim or implication | Revision | Basis |
|---|---|---|
| Coarse satellite elevation is the central bottleneck for current EV routing | Scope to a testable source of error; do not generalise across providers | Product descriptions and a need for comparative evidence: [R1–R4](references.md) |
| Satellite maps universally describe the physical road surface | Distinguish surface model, terrain model and actual road geometry | [R1](references.md#r1--copernicus-elevation-product) |
| A high-rate IMU isolates true road slope independently of chassis vibration | Model mounting, body motion and road attitude separately | [R3](references.md#r3--mobile-road-grade-estimation) and estimation design |
| RTK provides unconditional ±2-cm absolute road height | Report statistics, conditions, datum and full measurement chain | [R7](references.md#r7--rtk-receiver-specification) |
| A specific gyro bias specification guarantees useful sub-metre slope accuracy | Replace with a spatial-error budget; sample rate is not effective resolution | Error propagation in whitepaper Section 5 |
| Microphones produce a precise local rolling coefficient | Keep acoustic-to-resistance inference as a hypothesis requiring independent labels | [R5](references.md#r5--rolling-resistance-measurement-and-modelling), [R6](references.md#r6--acoustic-road-terrain-classification) |
| Surface type, skid friction and rolling resistance are interchangeable | Define different quantities; condition resistance on vehicle/tyre/environment | Model identifiability and data contract |
| Banking necessarily increases propulsion torque | Use a force/energy model; banking alone is not a longitudinal power penalty | [R8](references.md#r8--circular-motion-mechanics) |
| Combining pitch and bank angles gives an effective gravity vector | Treat these as geometric descriptors, with consistent units and frames | Dimensional analysis |
| Sensor fusion creates noise-free empirical data | Retain uncertainty, bias, quality flags and missing data | Proposed estimation and validation procedures |
| Missing short power peaks necessarily implies large total energy error | Separate power, gravitational work, conversion losses and recovery limits | Whitepaper Section 3 and analytical tests |
| Waterlogging or roughness increases resistance by a general percentage | Remove the unsourced percentage; specify conditions and require measurements | No supporting project dataset |
| Historical pressure suffices for air density at forecast time | Require temperature and relevant environmental inputs | Physical density relation and temporal validity |
| A JSON edge payload is an implemented Valhalla integration | Label the sidecar as proposed; define graph versioning and route-scoring limits | [R9](references.md#r9--routing-architecture), [R10](references.md#r10--routing-graph-versioning) |
| Defensive publication guarantees unrestricted global development | Preserve open publication intent without a legal priority or freedom-to-operate conclusion | [R11](references.md#r11--cc0-scope) |

The revision also adds references, version/citation metadata, a prospective validation plan and executable synthetic calculations. The numerical example does not retroactively validate the original hardware proposal.
