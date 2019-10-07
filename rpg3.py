# -*- coding: utf-8 -*-
"""
Created on Fri Sep 20 09:46:44 2019

@author: Mihai Boldeanu
"""


import numpy as np
import rpg_lib

path_raw = r"H:\Brute\RPG-FMCW-94\Y2019\M08\D05"
path_proc = r"H:\Brute\RPG-FMCW-94\from_Lukas\08\05"
# Get date of measurement from file

## List all files in *path* and only select the netCDF files
daily_time,height_range,daily_reflectivity_raw = rpg_lib.read_netcdf(path_proc,processed = True)
daily_reflectivity_log = 10 * np.log10(daily_reflectivity_raw)

### Plotting the data
dat = "_05"
rpg_lib.plot_rpg(daily_time,height_range,daily_reflectivity_log,name="proccessed_data"+dat)



## List all files in *path* and only select the netCDF files
daily_time,height_range,daily_reflectivity_raw = rpg_lib.read_netcdf(path_raw)
daily_reflectivity_log = 10 * np.log10(daily_reflectivity_raw)

### Cleaning the data  
mask = rpg_lib.filter_rpg(daily_reflectivity_log)
reverse_mask = np.logical_not(mask)
clean_data = daily_reflectivity_log * mask / mask
noise = daily_reflectivity_log * reverse_mask / reverse_mask

### Plotting the data

rpg_lib.plot_rpg(daily_time,height_range,mask,name="mask"+dat,min_v = 0,max_v=1)
rpg_lib.plot_rpg(daily_time,height_range,clean_data,name="filtered_data"+dat)
rpg_lib.plot_rpg(daily_time,height_range,daily_reflectivity_log,name="original_data"+dat)
rpg_lib.plot_rpg(daily_time,height_range,noise,name="noise_data"+dat)

save_data = {"data"  : clean_data,
             "mask"  : mask,
             "noise" : noise,
             "time"  : daily_time,
             "height": height_range}

### Saving data 
rpg_lib.save_netcdf("test",save_data)




