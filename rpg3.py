# -*- coding: utf-8 -*-
"""
Created on Fri Sep 20 09:46:44 2019

@author: Mihai Boldeanu

Example script of how to use the rpg_lib radar processing library:
- Reading multiple files from different folders
- For each daily file filter data
- Average at selected time and height resolution
- Save to netcdf files

"""


import numpy as np
import rpg_lib

path_raw = r"H:\Brute\RPG-FMCW-94\Y2019\M08\D05"
path_proc = r"H:\Brute\RPG-FMCW-94\from_Lukas\08\05"

daily_file = rpg_lib.read_folders(path_raw,processed = False)
for day in daily_file:
    daily_time = day[0]
    height_range = day[1]
    daily_reflectivity_raw = day[2]
    daily_reflectivity_log = 10 * np.log10(daily_reflectivity_raw)
    name = day[3]
   
    
    ### Cleaning the data  
    mask = rpg_lib.filter_rpg(daily_reflectivity_log)
    reverse_mask = np.logical_not(mask)
    clean_data = daily_reflectivity_log * mask / mask
    noise = daily_reflectivity_log * reverse_mask / reverse_mask
    

    
    save_data = {"data"  : clean_data,
                 "mask"  : mask,
                 "noise" : noise,
                 "time"  : daily_time,
                 "height": height_range}
    
    ### Saving data 
    rpg_lib.save_netcdf(name,save_data)
    clean_data = daily_reflectivity_raw * mask / mask
    averaged_time,averaged_range,avearaged_data = rpg_lib.average(daily_time,height_range,clean_data)
    averaged_time,averaged_range,avearaged_noise = rpg_lib.average(daily_time,height_range,noise)
    avearaged_mask = avearaged_data * 0 + 1
    avearaged_mask[np.where(np.isnan(avearaged_mask))] = 0 
    
    
    
    save_data_avr = {"data"  : 10 * np.log10(avearaged_data),
                 "time"  : averaged_time,
                 "height": averaged_range,
                 "mask"  : avearaged_mask,
                 "noise" : avearaged_noise,}
    rpg_lib.save_netcdf(name+"_averaged",save_data_avr)



