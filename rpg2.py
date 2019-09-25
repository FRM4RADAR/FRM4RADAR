# -*- coding: utf-8 -*-
"""
Created on Fri Sep 20 09:46:44 2019

@author: Mihai Boldeanu
"""


import os
import numpy as np
import rpg_lib

path = r"H:\Brute\RPG-FMCW-94\Y2019\M08\D01"
## List all files in *path* and only select the netCDF files
hourly_files = os.listdir(path)
hourly_files_nc = [hour_file for hour_file in hourly_files if "NC" in hour_file]
hourly_files_nc = sorted(hourly_files_nc)


## Empty lists for data
daily_reflectivity = []
hourly_average = []
hourly_average_nan = []
hourly_range = []
daily_time = []

for file_name in hourly_files_nc:
    file_path = os.path.join(path,file_name)
    
    ## Read data from netcdf4
    temp_data = rpg_lib.read_rpg_netcdf(file_path)
    
    ## Merge Chirp tables
    time,height_range,reflectivity = rpg_lib.merge_chirp(temp_data)
    
    ## Add hourly data to daily set
    daily_reflectivity.append(reflectivity)  
    daily_time.append(time)
    
    
### Cleaning the data    
daily_reflectivity_raw = np.concatenate(daily_reflectivity)
daily_reflectivity_concat = 10 * np.log10(daily_reflectivity_raw)

daily_time = np.concatenate(daily_time)
clean_data = rpg_lib.filter_rpg(daily_reflectivity_concat)

rpg_lib.plot_rpg(daily_time,height_range,clean_data,name="clean_data",min_v = 0,max_v=1)
rpg_lib.plot_rpg(daily_time,height_range,daily_reflectivity_concat * clean_data/clean_data,name="filtered_data")
rpg_lib.plot_rpg(daily_time,height_range,daily_reflectivity_concat,name="original_data")

clean_data = daily_reflectivity_concat* clean_data/clean_data



### Average experiment with logs

## Averaging heigth than time
bins,bins_over_height,averaged_data = rpg_lib.average_in_height(daily_time,height_range,clean_data,height_bin_size=500,time_bin_size=3600)
rpg_lib.plot_rpg(daily_time,bins,averaged_data,name="averaged_data_500")
bins_t,bins_over_time,averaged_data_h_t = rpg_lib.average_in_time(daily_time,bins,averaged_data,height_bin_size=500,time_bin_size=3600)
rpg_lib.plot_rpg(bins_t,bins,averaged_data_h_t.T,name="averaged_data_500m_1h")


## Averaging time than height
bins,bins_over_time,averaged_data = rpg_lib.average_in_time(daily_time,height_range,clean_data,height_bin_size=500,time_bin_size=3600)
rpg_lib.plot_rpg(bins,height_range,averaged_data.T,name="averaged_data_1h")
bins_height,bins_over_height,averaged_data_t_h = rpg_lib.average_in_height(bins,height_range,averaged_data.T,height_bin_size=500,time_bin_size=3600)
rpg_lib.plot_rpg(bins,bins_height,averaged_data_t_h,name="averaged_data_1h_500m")


## Averaging both time and height at same time
time,height,average = rpg_lib.average(daily_time,height_range,clean_data,height_bin_size=500,time_bin_size=3600)
rpg_lib.plot_rpg(time,height,average,name="averaged")


### Difference of averages
rpg_lib.plot_rpg(time,height,average-averaged_data_t_h,name="averaged-time_height",min_v=-10,max_v=10)
rpg_lib.plot_rpg(time,height,average-averaged_data_h_t.T,name="averaged-height_time",min_v=-10,max_v=10)
rpg_lib.plot_rpg(time,height,averaged_data_t_h-averaged_data_h_t.T,name="time_height-height_time",min_v=-10,max_v=10)




### Average experiment with raw
clean_data = rpg_lib.filter_rpg(daily_reflectivity_concat)

clean_data = daily_reflectivity_raw * clean_data/clean_data
## Averaging heigth than time
bins,bins_over_height,averaged_data = rpg_lib.average_in_height(daily_time,height_range,clean_data,height_bin_size=500,time_bin_size=3600)
rpg_lib.plot_rpg(daily_time,bins,10*np.log10(averaged_data),name="averaged_data_500_raw")
bins_t,bins_over_time,averaged_data_h_t = rpg_lib.average_in_time(daily_time,bins,averaged_data,height_bin_size=500,time_bin_size=3600)
rpg_lib.plot_rpg(bins_t,bins,10*np.log10(averaged_data_h_t.T),name="averaged_data_500m_1h_raw")


## Averaging time than height
bins,bins_over_time,averaged_data = rpg_lib.average_in_time(daily_time,height_range,clean_data,height_bin_size=500,time_bin_size=3600)
rpg_lib.plot_rpg(bins,height_range,10*np.log10(averaged_data.T),name="averaged_data_1h_raw")
bins_height,bins_over_height,averaged_data_t_h = rpg_lib.average_in_height(bins,height_range,averaged_data.T,height_bin_size=500,time_bin_size=3600)
rpg_lib.plot_rpg(bins,bins_height,10*np.log10(averaged_data_t_h),name="averaged_data_1h_500m_raw")


## Averaging both time and height at same time
time,height,average = rpg_lib.average(daily_time,height_range,clean_data,height_bin_size=500,time_bin_size=3600)
rpg_lib.plot_rpg(time,height,10*np.log10(average),name="averaged_raw")


### Difference of averages
rpg_lib.plot_rpg(time,height,10*np.log10(average-averaged_data_t_h),name="averaged-time_height_raw",min_v=-10,max_v=10)
rpg_lib.plot_rpg(time,height,10*np.log10(average-averaged_data_h_t.T),name="averaged-height_time_raw",min_v=-10,max_v=10)
rpg_lib.plot_rpg(time,height,10*np.log10(averaged_data_t_h-averaged_data_h_t.T),name="time_height-height_time_raw",min_v=-10,max_v=10)