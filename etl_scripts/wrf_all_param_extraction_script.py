#!/usr/bin/python3
#+++++++++++++++---------------------------------------------++++++++++++++++++
import os
import fiona, numpy as np
from pyscissor import scissor
from netCDF4 import Dataset, num2date
from shapely.geometry import shape
from datetime import datetime as dt, timedelta as delt

#++++++++++++++-----------------------------------------------++++++++++++++++++

# Constants value to compute RH
svp1 = 611.2
svp2 = 17.67
svp3 = 29.65
svpt0 = 273.15
eps = 0.622

#++++++++++++++-------------------------------------------------+++++++++++++++++
def calculate_RH(PSFC, Q, T):
    # Calculate saturation vapor pressure
    e_s = svp1 * np.exp(svp2 * (T - svpt0) / (T - svp3))

    # Calculate actual vapor pressure
    e = PSFC * Q / (eps + Q * (1 - eps))

    # Calculate relative humidity
    rh = 1.0e2 * e / e_s

    return rh
#++++++++++++++-------------------------------------------------+++++++++++++++++

def process_temperature(temperature, start_idx, end_idx, wg):
    # Pre-allocate a list to store the averaged temperatures
    day_temp_data = []

    # Loop through the specified range and calculate weighted averages
    for i in range(start_idx, end_idx):
        avg_temp = np.average(temperature[i, :, :], weights=wg)
        day_temp_data.append(avg_temp)

    # Convert list to numpy array for efficient operations
    day_temp_data = np.array(day_temp_data)

    # Calculate min, max, and average temperatures
    min_temp = np.min(day_temp_data)
    max_temp = np.max(day_temp_data)
    avg_temp = np.average(day_temp_data)

    return min_temp, max_temp, avg_temp
#++++++++++++++-------------------------------------------------+++++++++++++++++

def process_master(weather_param, start_idx, end_idx, wg):
    # Pre-allocate a list to store the averaged weather param
    weather_param_data = []

    # Loop through the specified range and calculate weighted averages
    for i in range(start_idx, end_idx):
        avg_wp = np.average(weather_param[i, :, :], weights=wg)
        weather_param_data.append(avg_wp)

    # Convert list to numpy array for efficient operations
    weather_param_data = np.array(weather_param_data)

    # Calculate the average
    avg_wp = np.average(weather_param_data)

    return avg_wp
#++++++++++++++-------------------------------------------------+++++++++++++++++

def process_cldfra(cldfra, start_idx, end_idx, wg):
    # Pre-allocate a list to store the averaged cldfra
    cldfra_data = []

    # Loop through the specified range and calculate weighted averages
    for i in range(start_idx, end_idx):
        first_d = cldfra[i, :, :, :]
        for i in range(34):  # 34 is vertical levels present in the cldfra variable in nc file
            second_d = first_d[i, :, :]
            avg_cldfra = np.average(second_d, weights = wg)
            cldfra_data.append(avg_cldfra)

    #Convert list to numpy array for efficient operations
    cldfra_data = np.array(cldfra_data)

    #Calculate the average
    avg_cldfra = np.average(cldfra_data)

    return avg_cldfra
#++++++++++++++-------------------------------------------------+++++++++++++++++

# Function to save a file in a directory
def save_data(data_path, file_name, data_txt):
    if not os.path.exists(data_path):
        os.makedirs(data_path)
    file_path = os.path.join(data_path, file_name)
    with open(file_path, 'w') as file:
        file.write(data_txt)

#++++++++++++++-------------------------------------------------+++++++++++++++++

def extract_txt_file(weather_param_data_days):
    return f"{weather_param_data_days[0]:0.2f} \t{weather_param_data_days[1]:0.2f} \t{weather_param_data_days[2]:0.2f}"

#++++++++++++++-------------------------------------------------+++++++++++++++++

def today_formatted_date():
    today = dt.today()
    fdate = today.strftime('%Y%m%d')
    return fdate

#++++++++++++++-------------------------------------------------+++++++++++++++++

def yesterday_formatted_date():
    today = dt.today()
    temp_dt = today- delt(days=1)
    td = temp_dt.strftime('%Y-%m-%d')
    return td

#++++++++++++++-------------------------------------------------+++++++++++++++++

def assign_filename(weather_param_name, location):
    return f"{location}.txt"
    #return f"{location}_{weather_param_name}.txt"
    #formatted_date = today_formatted_date()
    #return f"{location}_{weather_param_name}_{formatted_date}.txt"
    #return f"{location}_{weather_param_name}_20240717.txt"

#++++++++++++++-------------------------------------------------+++++++++++++++++

SHAPEFILE = 'var/www/instantnp/scripts/SINDHUPALCHOK_DISTRICT_BOUNDARY.geojson'
output_path= '/var/www/instantnp/scripts/WRFModelOutput/'
nc_file_name = 'nepal_d'+yesterday_formatted_date()+'.nc'
print(nc_file_name)
NCFILE = f"/var/www/instantnp/scripts/WRFNCFiles/{nc_file_name}"

#read shapefile and netcdf file
ncf = Dataset(NCFILE)
sf = fiona.open(SHAPEFILE, 'r')

lat = ncf.variables['XLAT'][:, 122]
lon = ncf.variables['XLONG'][74, :]

rainc = ncf.variables['RAINC'][:]
rainnc = ncf.variables['RAINNC'][:]
rainfall = rainc + rainnc
temperature_kelvin = ncf.variables['T2'][:]
temperature = temperature_kelvin - svpt0  #Converting from Kelvin to Celsius

# Extract the U and V components of wind at 10 meters above ground level
U10 = ncf.variables['U10'][:]
V10 = ncf.variables['V10'][:]

# Calculate wind speed at 10 meters
wind_speed_10m = np.sqrt(U10**2 + V10**2)

# Calculate wind direction at 10 meters
wind_direction_10m = 180 + (180 / np.pi) * np.arctan2(V10, U10)

# Extract the cloud fraction 
cldfra = ncf.variables['CLDFRA'][:]

Q = ncf.variables['Q2'][:]     # Extract specific humidity (kg/kg)
P = ncf.variables['PSFC'][:]   # Extract PSFC -> surface pressure (Pa)

RH = calculate_RH(P, Q, temperature_kelvin) # Extract RH from Q2, PSFC and Temperature (in K)

times = num2date(ncf.variables['XTIME'][:], ncf.variables['XTIME'].units)
times_py=[dt(x.year,x.month,x.day,x.hour,x.minute) for x in times]

days = [ (4, 12), (12, 20), (20, 28) ]
for rec in sf:
    _name = rec['properties']['GaPa_NaPa']
    _shp = shape(rec['geometry'])
    pys = scissor(_shp, lat, lon)
    wg = pys.get_masked_weight_recursive()

    # Initialize lists to store the results
    rf_data_days = []
    min_temp_data_days = []
    max_temp_data_days = []
    temp_data_days = []
    ws_data_days = []
    winddirection_data_days = []
    cldfra_data_days = []
    rh_data_days = []

    for ix, (si, ei) in enumerate(days):
        # Weighted Average Rainfall
        pr_day = np.average(rainfall[ei, :, :] - rainfall[si, :, :], weights=wg)
        rf_data_days.append(pr_day)

        min_temp, max_temp, avg_temp = process_temperature(temperature, si, ei, wg)
        min_temp_data_days.append(min_temp)
        max_temp_data_days.append(max_temp)
        temp_data_days.append(avg_temp)

        avg_ws = process_master(wind_speed_10m, si, ei, wg)
        ws_data_days.append(avg_ws)

        avg_wind_direction = process_master(wind_direction_10m, si, ei, wg)
        winddirection_data_days.append(avg_wind_direction)

        avg_cldfra_direction = process_cldfra(cldfra, si, ei, wg)
        cldfra_data_days.append(avg_cldfra_direction)

        avg_RH = process_master(RH, si, ei, wg)
        rh_data_days.append(avg_RH)

    rf_data_txt = extract_txt_file(rf_data_days)
    temp_data_txt = extract_txt_file(temp_data_days)
    min_temp_data_txt = extract_txt_file(min_temp_data_days)
    max_temp_data_txt = extract_txt_file(max_temp_data_days)
    ws_data_txt = extract_txt_file(ws_data_days)
    wind_direction_data_txt = extract_txt_file(winddirection_data_days)
    cldfra_data_txt = extract_txt_file(cldfra_data_days)
    rh_data_txt = extract_txt_file(rh_data_days)

    rf_file_name = assign_filename('rf', _name)
    temp_file_name = assign_filename('temp', _name)
    min_temp_file_name = assign_filename('min_temp', _name)
    max_temp_file_name = assign_filename('max_temp', _name)
    ws_file_name = assign_filename('ws', _name)
    winddirection_file_name = assign_filename('winddir', _name)
    cldfra_file_name = assign_filename('cldfra', _name)
    rh_file_name = assign_filename('rh', _name)

    rf_data_path = f'{output_path}/wrf_rainfall/{today_formatted_date()}'
    temp_data_path = f'{output_path}/wrf_temperature/{today_formatted_date()}'
    min_temp_data_path = f'{output_path}/wrf_minimum_temperature/{today_formatted_date()}'
    max_temp_data_path = f'{output_path}/wrf_maximum_temperature/{today_formatted_date()}'
    ws_data_path = f'{output_path}/wrf_windspeed/{today_formatted_date()}'
    winddirection_data_path = f'{output_path}/wrf_winddirection/{today_formatted_date()}'
    cldfra_data_path = f'{output_path}/wrf_cldfra/{today_formatted_date()}'
    rh_data_path = f'{output_path}/wrf_rh/{today_formatted_date()}'

    # Call the function to save each dataset
    print('Saving weather forecast data for', _name)
    save_data(rf_data_path, rf_file_name, rf_data_txt)
    print('Rainfall export completed')

    save_data(temp_data_path, temp_file_name, temp_data_txt)
    print('Average temperature export completed')

    save_data(min_temp_data_path, min_temp_file_name, min_temp_data_txt)
    print('Minimum temperature export completed')

    save_data(max_temp_data_path, max_temp_file_name, max_temp_data_txt)
    print('Maximum temperature export completed')

    save_data(ws_data_path, ws_file_name, ws_data_txt)
    print('Wind speed export completed')

    save_data(winddirection_data_path, winddirection_file_name, wind_direction_data_txt)
    print('Wind direction export completed')

    save_data(cldfra_data_path, cldfra_file_name, cldfra_data_txt)
    print('Cloud fraction export completed')

    save_data(rh_data_path, rh_file_name, rh_data_txt)
    print('Relative humidity export completed')

    print('++++++++++---------------------------------+++++++++++')


