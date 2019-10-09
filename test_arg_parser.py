# -*- coding: utf-8 -*-
"""
Created on Wed Oct  9 09:26:24 2019

@author: Mihai Boldeanu
"""

import argparse
from pathlib import Path
import rpg_lib
import numpy as np


def main():
    parser = argparse.ArgumentParser(prog='FRM4RADAR')
    parser.add_argument(
        "path",
        type=Path,
        default=Path(__file__).absolute().parent / "data",
        help="Path to the data directory",
    )
    parser.add_argument(
        "--proc",
        type=bool,
        default = False ,
        help="Path is for processed data or raw data.(default False)",
    )

    parser.add_argument(
        "--time",
        type=int,
        default = 3600 ,
        help="Time to average at in seconds.(default 3600s)",
    )
    parser.add_argument(
        "--height",
        type=int,
        default = 500 ,
        help="Height to average atin meters.(default 500 m)",
    )
    p = parser.parse_args()
    print("Looking for files starting from this path:",p.path)
    print("Found files will be treated as processed netcdCDF4:",p.proc)
    print("Time at which the averaging will be done:",p.time)
    print("Height at which the averaging will be done:",p.height)
    daily_data = rpg_lib.read_folders(p.path,p.proc)
    if not p.proc:
        for data in daily_data:
            if data:
                
                daily_reflectivity_log = 10 * np.log10(data[2])
                mask = rpg_lib.filter_rpg(daily_reflectivity_log)
                reverse_mask = np.logical_not(mask)
                clean_data = daily_reflectivity_log * mask / mask
                noise = daily_reflectivity_log * reverse_mask / reverse_mask
                daily_time = data[0]
                height_range = data[1]
                
                save_data = {"data"  : clean_data,
                             "mask"  : mask,
                             "noise" : noise,
                             "time"  : daily_time,
                             "height": height_range}
                save_name = data[3]
                ### Saving data 
                rpg_lib.save_netcdf(save_name,save_data)
                
                clean_data = data[2] * mask / mask
                averaged_time,averaged_range,avearaged_data = rpg_lib.average(daily_time,height_range,clean_data,height_bin_size=p.height,time_bin_size=p.time)
                averaged_time,averaged_range,avearaged_noise = rpg_lib.average(daily_time,height_range,mask,height_bin_size=p.height,time_bin_size=p.time)
                
                avearaged_mask = avearaged_data * 0 + 1
                avearaged_mask[np.where(np.isnan(avearaged_mask))] = 0 
                
                save_data_avr = {"data"  : 10 * np.log10(avearaged_data),
                             "time"  : averaged_time,
                             "height": averaged_range,
                             "mask"  : avearaged_mask,
                             "noise" : avearaged_noise,}
                rpg_lib.save_netcdf(save_name+"_averaged",save_data_avr)
    


if __name__ == "__main__":
    main()