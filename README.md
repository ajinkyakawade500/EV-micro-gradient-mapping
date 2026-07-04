# Hardware Architecture for Empirical Road Resistance and Micro-Gradient Mobile Mapping Fleets to Optimize Electric Vehicle Predictive Energy Routing

**Author:** **Ajinkya Kawade**

**Date:** July 2026

**License:** Public Domain ([CC0 1.0 Universal](LICENSE))

---

## Abstract
Predictive energy routing for Electric Vehicles (EVs) remains severely bottlenecked by the low spatial resolution and static nature of current satellite-derived Digital Elevation Models (DEMs). These models fai l to capture localized micro-gradients, structural road banking, and dynamic rolling resistance coefficients ($C_{rr}$), causing significant divergence between predicted and real-world battery State of Charge (SoC). 

This whitepaper outlines a mobile fleet sensor architecture designed for integration into standard mapping vehicles (e.g., street-level photography fleets). By combining 6-axis Inertial Measurement Units (IMUs), Real-Time Kinematic (RTK) GNSS, barometric altimetry, solid-state LiDAR, and acoustic tire-friction arrays, mapping vehicles can generate a deterministic, high-resolution empirical database of road tractive resistance. This document is published defensively to establish open prior art, enabling the unrestricted global development of precision EV navigation systems.

---

## 1. The EV Routing Problem & Limitations of Existing Models

Current EV routing engines compute energy expenditure by applying vehicle mass and aerodynamic profiles over a sequence of road segments. The total tractive force ($F_{\text{total}}$) required to propel the vehicle is modeled as:

$$F_{\text{total}} = F_{\text{gravity}} + F_{\text{rolling}} + F_{\text{aerodynamic}} + F_{\text{inertial}}$$

Where:
*   $F_{\text{gravity}} = m \cdot g \cdot \sin(\theta)$
*   $F_{\text{rolling}} = m \cdot g \cdot C_{rr} \cdot \cos(\theta)$
*   $F_{\text{aerodynamic}} = \frac{1}{2} \cdot \rho \cdot C_d \cdot A \cdot v^2$
*   $F_{\text{inertial}} = m \cdot a$

*(Where $m$ represents total vehicle mass, $g$ is gravitational acceleration, $\theta$ is the road gradient slope angle, $C_{rr}$ is the rolling resistance coefficient, $\rho$ is air density, $C_d$ is the aerodynamic drag coefficient, $A$ is the vehicle frontal area, $v$ is velocity, and $a$ is acceleration.)*

### The Saturation and Resolution Deficit
Standard routing frameworks pull elevation data from satellite frameworks like the Shuttle Radar Topography Mission (SRTM) or Copernicus DEM. These systems suffer from fundamental engineering limitations when applied to EV routing:
1.  **Spatial Smoothing:** Satellite data typically resolves at 30-meter horizontal grids. Sudden grade breaks, steep switchbacks (ghat sections), and micro-topography are mathematically smoothed out, causing algorithms to underestimate the high power spikes required to overcome gravitational resistance on short, steep inclines.
2.  **Canopy and Urban Obscuration:** In dense forests or deep urban canyons, satellite altimetry suffers from severe signal degradation, leading to interpolated elevation profiles that do not match physical road surfaces.
3.  **Assumed Uniformity of $C_{rr}$:** Routing engines typically treat rolling resistance as a static constant across all tarmac. In reality, degraded concrete, rough asphalt, and water logging can increase $C_{rr}$ by greater than 15%, directly inducing unpredicted battery drain.

---

## 2. Proposed Mobile Sensor Architecture

To map these variables empirically, mapping vehicles must collect real-time chassis dynamics and road surface acoustics simultaneously. The tracking fleet uses a specialized four-tier hardware sensor array.

### Sensor Specifications and Operational Logic

| Sensor Class | Hardware Specifications | Target Physics Metric | Algorithmic Utility |
| :--- | :--- | :--- | :--- |
| **6-Axis Industrial IMU** | High-bias stability ($<0.05^\circ\text{/hr}$), high-frequency ($>200\text{ Hz}$) Accelerometers & Gyroscopes. | Instantaneous pitch angle ($\theta_{\text{pitch}}$) and roll angle ($\theta_{\text{roll}}$). | Isolates true vehicle attitude independent of vehicle vibrations, capturing accurate road slope changes at sub-meter intervals. |
| **RTK-GNSS + Barometric Altimeter** | Multi-band L1/L2/L5 receiver with local RTK correction network subscription; MEMS piezoresistive pressure sensor. | Absolute ellipsoidal height ($z$-axis) down to $\pm2\text{ cm}$; Ambient pressure ($P$). | Bakes absolute elevation anchors into the IMU trajectory loop while tracking local air density changes ($\rho$) for aerodynamic calculations. |
| **Solid-State LiDAR** | High-density, multi-echo, non-repeating scan pattern array (e.g., 905nm wavelength). | Digital surface twin; transverse road cross-sections ($C_{\text{bank}}$). | Identifies structural road banking and lateral slopes on tight curves. Steering against steep, banked switchbacks demands higher motor torque vectors. |
| **Chassis-Mounted Acoustic Array** | Dual-element, weatherproof, directional microphones mounted in the wheel-well housing, shielded from aerodynamic wind noise. | Acoustic sound pressure level (SPL) frequency spectrum ($20\text{ Hz} - 20\text{ kHz}$) of tire-to-road interaction. | Machine learning models map the raw audio frequency signatures against calibrated road texture archetypes to output a precise localized $C_{rr}$ value. |

---

## 3. Sensor Fusion & The Empirical Data Pipeline

The raw telemetry streams must be fused to create a highly accurate, noise-free representation of the road's topology. 

### Step 1: Extended Kalman Filter (EKF) Attitude Fusion
To derive the true road gradient, a localized EKF continuously fuses the high-frequency IMU pitch acceleration with the absolute position points provided by the RTK-GNSS system. This prevents accelerometer drift from corrupting the gradient mapping over long distances:

$$\hat{\theta}(t) = f\left(\text{IMU}_{\text{gyro}}(t),\, \text{GNSS}_{\Delta z}(t),\, \text{Baro}_{\Delta P}(t)\right)$$

### Step 2: Extracting Spatial Surface Geometry via LiDAR
The solid-state LiDAR continuously measures the transverse angle of the lane. If a vehicle is cornering on a slope, the true gravitational load experienced by the electric drivetrain shifts due to centripetal vectors and the road's lateral banking angle ($\alpha$). The system records a combined spatial vector:

$$\vec{G}_{\text{effective}} = \begin{bmatrix} \theta_{\text{pitch}} \\ \alpha_{\text{bank}} \end{bmatrix}$$

### Step 3: Acoustic Profiling for Friction Mapping
The wheel-well microphones capture the high-frequency vibrations and acoustic friction of the tire rolling over the surface. The central computing unit extracts Mel-Frequency Cepstral Coefficients (MFCCs) from the audio stream. A pre-trained machine learning architecture runs on the edge to classify the road surface material:

$$\text{Audio Spectrum File} \longrightarrow \text{MFCC Feature Extraction} \longrightarrow \text{Surface Classifier Model} \longrightarrow \text{Dynamic } C_{rr} \text{ Modifier}$$

---

## 4. Routing Engine Integration (Valhalla/OSM Edge Costing)

The resulting datasets are compressed and projected onto an OpenStreetMap (OSM) base layer map graph using a specialized edge-costing format. Instead of storing complex, heavy raw point-cloud data, each discrete road edge segment is injected with a small, highly compressed telemetry payload array:

```json
{
  "edge_id": 987654321,
  "length_meters": 120.5,
  "base_gradient_pct": 6.82,
  "micro_gradients": [6.1, 6.4, 6.8, 7.2, 7.1, 6.7],
  "lateral_bank_deg": 1.45,
  "empirical_crr": 0.0115,
  "avg_baro_pa": 98450
}
