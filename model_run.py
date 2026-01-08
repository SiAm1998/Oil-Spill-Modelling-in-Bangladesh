import os
import datetime
import copernicusmarine
import matplotlib.pyplot as plt
from opendrift.models.openoil import OpenOil
from opendrift.readers import reader_constant
from opendrift.readers.reader_global_landmask import Reader as LandmaskReader
from opendrift.readers.reader_netCDF_CF_generic import Reader

# --- Configuration ---
# BEST PRACTICE: Set these in your OS environment variables, do not hardcode.
USERNAME = os.getenv("COPERNICUS_USER")
PASSWORD = os.getenv("COPERNICUS_PASS")

if not USERNAME or not PASSWORD:
    print("WARNING: Credentials not found. Please set COPERNICUS_USER and COPERNICUS_PASS.")
    # You can uncomment below for local testing, but NEVER commit to GitHub
    # USERNAME = "your_email"
    # PASSWORD = "your_password"

# Simulation Parameters
START_TIME = datetime.datetime(2024, 7, 15, 12, 0, 0)
DURATION_DAYS = 2
SPILL_LOCATION = {'lat': 21.4633, 'lon': 89.5441} # Near Mongla
OIL_TYPE = 'GENERIC MEDIUM CRUDE'

def setup_model():
    """Initializes the OpenOil model with specific physics configurations."""
    o = OpenOil()
    
    # Physics Settings
    o.set_config('processes:dispersion', True)
    o.set_config('processes:evaporation', True)
    o.set_config('processes:emulsification', True)
    o.set_config('processes:biodegradation', True)
    o.set_config('drift:vertical_mixing', True)
    o.set_config('vertical_mixing:timestep', 5)
    
    # Environment Constants (Fallbacks)
    o.set_config('environment:constant:sea_water_temperature', 26)
    o.set_config('environment:constant:sea_water_salinity', 35)
    o.set_config('environment:constant:ocean_mixed_layer_thickness', 20)
    o.set_config('drift:current_uncertainty', 0.1)
    o.set_config('drift:wind_uncertainty', 0.1)
    o.set_config('general:coastline_action', 'stranding')
    
    return o

def add_readers(o):
    """Adds Copernicus Marine Service (CMEMS) readers and Landmask."""
    
    # 1. Landmask
    o.add_reader(LandmaskReader())
    
    # 2. CMEMS Data Loaders
    # Note: 'chunk_size_limit=0' disables chunking warnings for small subsets
    try:
        ds_current = copernicusmarine.open_dataset(
            dataset_id='cmems_mod_glo_phy_anfc_merged-uv_PT1H-i', 
            username=USERNAME, password=PASSWORD, chunk_size_limit=0)
        
        ds_wind = copernicusmarine.open_dataset(
            dataset_id='cmems_obs-wind_glo_phy_nrt_l4_0.125deg_PT1H', 
            username=USERNAME, password=PASSWORD, chunk_size_limit=0)
            
        ds_wave = copernicusmarine.open_dataset(
            dataset_id='cmems_mod_glo_wav_my_0.2deg_PT3H-i', 
            username=USERNAME, password=PASSWORD, chunk_size_limit=0)

        # 3. Create Readers with Mapping
        reader_current = Reader(ds_current, standard_name_mapping={
            'uo': 'x_sea_water_velocity',
            'vo': 'y_sea_water_velocity'
        })
        
        reader_wind = Reader(ds_wind, standard_name_mapping={
            'eastward_wind': 'x_wind',
            'northward_wind': 'y_wind'
        })
        
        reader_wave = Reader(ds_wave, standard_name_mapping={
            'VSDX': 'sea_surface_wave_stokes_drift_x_velocity',
            'VSDY': 'sea_surface_wave_stokes_drift_y_velocity',
            'VHM0': 'sea_surface_wave_significant_height',
            'VTPK': 'sea_surface_wave_period_at_variance_spectral_density_maximum',
            'VTM02': 'sea_surface_wave_mean_period_from_variance_spectral_density_second_frequency_moment'
        })

        o.add_reader(reader_current)
        o.add_reader(reader_wind)
        o.add_reader(reader_wave)
        print("MetOcean data loaded successfully.")
        
    except Exception as e:
        print(f"❌ Error loading CMEMS data: {e}")
        return None

    return o

def run_simulation(o):
    """Runs the simulation and generates outputs."""
    o.seed_elements(
        lon=SPILL_LOCATION['lon'], 
        lat=SPILL_LOCATION['lat'], 
        number=100, 
        time=START_TIME, 
        m3_per_hour=1500, 
        oil_type=OIL_TYPE,
        wind_drift_factor=0 # Typically ~0.03, but 0 if using Stokes drift explicitly
    )

    end_time = START_TIME + datetime.timedelta(days=DURATION_DAYS)
    
    print("Starting simulation...")
    o.run(end_time=end_time, time_step=7200, time_step_output=14400)
    
    # Generate Outputs
    print("Saving outputs...")
    if not os.path.exists('output'):
        os.makedirs('output')
        
    o.plot(filename='output/trajectory_map.png')
    o.plot_oil_budget(filename='output/oil_budget.png')
    
    try:
        o.animation(filename='output/simulation_video.mp4')
    except Exception as e:
        print(f"Animation skipped (ffmpeg might be missing): {e}")

if __name__ == "__main__":
    model = setup_model()
    model = add_readers(model)
    if model:
        run_simulation(model)
