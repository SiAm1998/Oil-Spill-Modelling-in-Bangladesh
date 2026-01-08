# Oil Spill Modelling in Bangladesh (OpenDrift)

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![OpenDrift](https://img.shields.io/badge/Model-OpenDrift-orange)
![Status](https://img.shields.io/badge/Status-Active-green)

## Project Overview
This project simulates the fate and trajectory of hypothetical oil spills near critical maritime zones in Bangladesh (**Chattogram Port** and **Mongla Port**) using the **OpenDrift** framework (`OpenOil` module). 

The model integrates real-time oceanographic data to predict:
- **Trajectory:** Where the oil will drift over time.
- **Weathering:** Evaporation, emulsification, and biodegradation rates.
- **Stranding:** Potential coastal impact zones (e.g., Sundarbans Mangrove Forest).

## Key Features
- **Hydrodynamic Forcing:** Uses Copernicus Marine Service (CMEMS) for currents, waves, and wind data.
- **Physics Engine:** Includes Stokes drift, vertical mixing, and turbulent diffusion.
- **Automated Pipeline:** Fetches live data via `copernicusmarine` API.

## Data Sources
| Parameter | Source | ID |
|-----------|--------|----|
| **Ocean Currents** | CMEMS Global Analysis | `cmems_mod_glo_phy_anfc_merged-uv_PT1H-i` |
| **Wind Fields** | CMEMS Satellite Obs | `cmems_obs-wind_glo_phy_nrt_l4_0.125deg_PT1H` |
| **Wave Dynamics** | CMEMS Global Waves | `cmems_mod_glo_wav_my_0.2deg_PT3H-i` |

## Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/SiAm1998/Oil-Spill-Modelling-in-Bangladesh.git](https://github.com/SiAm1998/Oil-Spill-Modelling-in-Bangladesh.git)
