# References and source notes

Sources checked on **21 September 2026**. This is a targeted literature review, not a systematic review or an exhaustive novelty/patent search. Source-specific findings below are distinguished from the repository's proposed design choices. No third-party paper, dataset or figure is redistributed here.

## R1 — Copernicus elevation product

Copernicus Data Space Ecosystem. *Copernicus DEM — Global and European Digital Elevation Model*. [Official documentation](https://dataspace.copernicus.eu/explore-data/data-collections/copernicus-contributing-missions/collections-description/COP-DEM). Dataset DOI: [10.5270/ESA-c5d3d65](https://doi.org/10.5270/ESA-c5d3d65).

Supports the distinction between a surface model and a terrain model, GLO-30 grid spacing, vertical reference EGM2008 and published product accuracy statistics. It does not establish road-level accuracy at a particular site or the dataset used by every routing provider.

## R2 — SRTM product

U.S. Geological Survey. *USGS EROS Archive — Digital Elevation — Shuttle Radar Topography Mission (SRTM) 1 Arc-Second Global*. [Official product page](https://www.usgs.gov/centers/eros/science/usgs-eros-archive-digital-elevation-shuttle-radar-topography-mission-srtm-1).

Supports identification of the approximately 30-m global product. Grid spacing and vertical error are different quantities; a 30-m grid does not imply a 30-m height error.

## R3 — Mobile road-grade estimation

Gupta, A., Hu, S., Zhong, W., Sadek, A., Su, L., & Qiao, C. (2020). *Road Grade Estimation Using Crowd-Sourced Smartphone Data*. [Author preprint, arXiv:2006.03633](https://arxiv.org/abs/2006.03633), [full text](https://arxiv.org/html/2006.03633v1), [publisher record](https://ieeexplore.ieee.org/document/9111051/).

An existing demonstration of mobile grade estimation and aggregation. Its experimental performance belongs to its own sensor setup and test route. It is not a promised accuracy for this project.

## R4 — Road grade and vehicle energy

Wood, E., Burton, E., Duran, A., & Gonder, J. (2014). *Contribution of Road Grade to the Energy Use of Modern Automobiles Across Large Datasets of Real-World Drive Cycles*. NREL/CP-5400-61108, conference-paper preprint. [Laboratory report](https://docs.nlr.gov/docs/fy14osti/61108.pdf).

Supports evaluating road grade with a vehicle-energy model and drive cycles. Its aggregate findings are not transferred to Indian roads, two-wheelers or this synthetic experiment.

## R5 — Rolling-resistance measurement and modelling

Andersen, L. G., Larsen, J., Fraser, E. S., Schmidt, B., & Dyre, J. C. (2015). *Rolling Resistance Measurement and Model Development*. Journal of Transportation Engineering, 141(2), 04014075. DOI: [10.1061/(ASCE)TE.1943-5436.0000673](https://doi.org/10.1061/(ASCE)TE.1943-5436.0000673). [Authors' university record and full-text link](https://forskning.ruc.dk/en/publications/rolling-resistance-measurement-and-model-development/).

Provides measurement/model context. The university record and abstract were checked for this revision; this repository does not claim to implement a standardised tyre-testing procedure from the paper.

## R6 — Acoustic road-terrain classification

Yang, D., Zhang, D., Yuan, Y., Lei, Z., Ding, B., & Bo, L. (2024). *Road terrain recognition based on tire noise for autonomous vehicle*. Scientific Reports, 14, 30913. DOI: [10.1038/s41598-024-81666-7](https://doi.org/10.1038/s41598-024-81666-7). [Publisher full text](https://www.nature.com/articles/s41598-024-81666-7).

Demonstrates a terrain-classification task using tyre audio. It does not establish a calibrated, transferable numerical rolling-resistance coefficient from sound. The proposed acoustic-to-resistance regression in this repository remains untested.

## R7 — RTK receiver specification

u-blox. *ZED-F9P-05B Data Sheet*, UBXDOC-963802114-12824, revision R02. [Manufacturer PDF](https://www.u-blox.com/sites/default/files/documents/ZED-F9P-05B_DataSheet_UBXDOC-963802114-12824.pdf).

Table 3 describes horizontal CEP and vertical median accuracy with specified test conditions. Footnotes include baseline and antenna conditions. These statistics are not a universal 95% confidence bound on moving road-height measurements. This is a specification example, not a procurement recommendation.

## R8 — Circular-motion mechanics

OpenStax. *University Physics, Volume 1*, Section 6.3, “Centripetal Force.” [Textbook section](https://openstax.org/books/university-physics-volume-1/pages/6-3-centripetal-force).

Supports the banked-curve force diagram. The power and dimensional-consistency discussion in the whitepaper follows from applying those mechanics.

## R9 — Routing architecture

Valhalla contributors. *Dynamic costing*. [Official documentation](https://valhalla.github.io/valhalla/concepts/costing/dynamic-costing/).

Supports the distinction between runtime costing and the attributes stored in routing tiles. The proposed sidecar format is not an existing Valhalla API.

## R10 — Routing graph versioning

Valhalla contributors. *Change identification*. [Official documentation](https://valhalla.github.io/valhalla/concepts/change-identification/).

Documents dataset/build/tile identity mechanisms. The proposed strong build digest and rematching policy are this repository's design choices.

## R11 — CC0 scope

Creative Commons. *CC0 1.0 Universal — Legal Code*, especially Section 4. [Official legal text](https://creativecommons.org/publicdomain/zero/1.0/legalcode.en).

Supports the license-scope correction. The repository makes no patentability, priority or freedom-to-operate determination.

## R12 — OpenStreetMap data terms

OpenStreetMap Foundation. *Copyright and License*. [Official page](https://www.openstreetmap.org/copyright).

Relevant to future integrations using OSM data. The current example contains synthetic identifiers and no OSM extract. Applying CC0 to repository-authored work does not relicense external data.
