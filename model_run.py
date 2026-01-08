import os
import datetime
import cf_xarray
import copernicusmarine
import matplotlib.pyplot as plt
from opendrift.models.openoil import OpenOil
from opendrift.readers import reader_constant
from opendrift.readers.reader_global_landmask import Reader as LandmaskReader
from opendrift.readers.reader_netCDF_CF_generic import Reader


username = "username from CMEM"
password = "Password from CMEM"


o = OpenOil()


start_time = datetime.datetime(2024, 7, 15, 12, 0, 0)
end_time = start_time + datetime.timedelta(days=2)
o.start_time = start_time

spill_lat = 21.4633
spill_lon = 89.5441
oil_type = 'GENERIC MEDIUM CRUDE'


#o.list_configspec()


# o.set_config('seed:m3_per_hour', 10) # spill amount can also be set in this way as an instantaneous release or as a spill rate
# The amount (volume) of oil released per hour (or total amount if release is instantaneous)

o.set_config('processes:dispersion', True)
o.set_config('processes:evaporation',  True)
o.set_config('processes:emulsification',  True)
o.set_config('processes:biodegradation', True)
o.set_config('drift:vertical_mixing',  True)
o.set_config('vertical_mixing:timestep',  5)

o.set_config('environment:constant:sea_water_temperature', 26)                  #
o.set_config('environment:constant:sea_water_salinity', 35)

# edit from here, 
o.set_config('environment:fallback:sea_surface_height', 0.4)
o.set_config('environment:fallback:upward_sea_water_velocity', 0.1)
o.set_config('environment:fallback:sea_surface_wave_significant_height', 1)
o.set_config('environment:fallback:sea_surface_wave_stokes_drift_x_velocity', -0.0302)
o.set_config('environment:fallback:sea_surface_wave_stokes_drift_y_velocity', 0.0898)
# o.set_config('environment:fallback:sea_surface_wave_period_at_variance_spectral_density_maximum', )
# o.set_config('environment:fallback:sea_surface_wave_mean_period_from_variance_spectral_density_second_frequency_moment', )

# o.set_config('environment:constant:sea_floor_depth_below_sea_level', )
o.set_config('environment:constant:ocean_mixed_layer_thickness', 20)



o.set_config('drift:current_uncertainty', .1)
o.set_config('drift:wind_uncertainty', .1)

o.set_config('general:coastline_action', 'stranding')
o.set_config('general:coastline_approximation_precision', .001)  # approx 100m




# Creating a constant reader with desired values
env_reader = reader_constant.Reader({
    'sea_water_temperature': 26,  # in °C
    'sea_water_salinity': 35    # in PSU
})

o.add_reader(env_reader)




ds_current = copernicusmarine.open_dataset(dataset_id='cmems_mod_glo_phy_anfc_merged-uv_PT1H-i', username=username, password=password, chunk_size_limit=0)
print(ds_current)     # Default Xarray output
print(ds_current.cf)  # Output from cf-xarray


ds_wind = copernicusmarine.open_dataset(dataset_id='cmems_obs-wind_glo_phy_nrt_l4_0.125deg_PT1H', username=username, password=password, chunk_size_limit=0)
print(ds_wind)     # Default Xarray output
print(ds_wind.cf)  # Output from cf-xarray


ds_wave = copernicusmarine.open_dataset(dataset_id='cmems_mod_glo_wav_my_0.2deg_PT3H-i', username=username, password=password, chunk_size_limit=0)
print(ds_wave)     # Default Xarray output
print(ds_wave.cf)  # Output from cf-xarray



reader_current = Reader(ds_current, standard_name_mapping={
                        'uo': 'x_sea_water_velocity',
                        'vo': 'y_sea_water_velocity',
                        })



reader_wind = Reader(ds_wind, standard_name_mapping={
                        'eastward_wind': 'x_wind',
                        'northward_wind': 'y_wind',
                        })


reader_wave = Reader(ds_wave, standard_name_mapping={
                        'VSDX': 'sea_surface_wave_stokes_drift_x_velocity',
                        'VSDY': 'sea_surface_wave_stokes_drift_y_velocity',
                        'VHM0' : 'sea_surface_wave_significant_height',
                        'VTPK' : 'sea_surface_wave_period_at_variance_spectral_density_maximum',
                        'VTM02' : 'sea_surface_wave_mean_period_from_variance_spectral_density_second_frequency_moment',
                        })



o.add_reader(reader_current, variables=['x_sea_water_velocity', 'y_sea_water_velocity'])

o.add_reader(reader_wind, variables=['x_wind', 'y_wind'])

o.add_reader(reader_wave, variables=[
    'sea_surface_wave_stokes_drift_x_velocity',
    'sea_surface_wave_stokes_drift_y_velocity',
    'sea_surface_wave_significant_height',
    'sea_surface_wave_period_at_variance_spectral_density_maximum',
    'sea_surface_wave_mean_period_from_variance_spectral_density_second_frequency_moment'
    ])



landmask = LandmaskReader()
print("Successfully loaded landmask data.")
o.add_reader(landmask)





o.seed_elements(lon=spill_lon, lat=spill_lat, number=100, time=start_time, m3_per_hour=1500, oil_type=oil_type, wind_drift_factor=0)

o.elements.substance = oil_type 


# ncfile = 'openoil_sample_output.nc'
# o.run(end_time=end_time, time_step=900, time_step_output=3600, outfile=ncfile)



o.run(end_time=end_time, time_step=1800, time_step_output=3600)


print(o)

o.plot()
# o.plot(fast=True)

o.plot_oil_budget()

o.plot_oil_budget(filename='Mongla_summer_oil_budget.png')

b = o.get_oil_budget()
time = (o.result.time-o.result.time[0]).dt.total_seconds()/3600  # Hours since start
fig, ax = plt.subplots()
ax.plot(time, b['mass_submerged'], label='Submerged oil mass')
ax.plot(time, b['mass_surface'], label='Surface oil mass')
ax.plot(time, b['mass_biodegraded'], label='Biodegraded oil mass')
ax.set_title(f'{o.get_oil_name()},  {b["oil_density"].max():.2f} kg/m3')
plt.legend()
plt.xlabel('Time [hours]')
plt.ylabel('Mass oil [kg]')
plt.show()

o.animation(filename='CTG_July15_July22.mp4')
o.animation(fast=True)
