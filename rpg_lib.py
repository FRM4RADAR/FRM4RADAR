# -*- coding: utf-8 -*-
"""
Created on Mon Sep 23 09:12:35 2019

@author: Mihai Boldeanu

@goal: A library of useful functions for working with RPG-94 radar systems

@contents:
    - Reading and plotting raw data
    - Cleaning noise from raw data
    - Averaging in height and time
"""
from netCDF4 import Dataset
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from scipy import ndimage
import numpy as np

### READING Function for netCDF4 files ###
def read_rpg_netcdf(path):
    
    """
    read_rph_netcdf: takes the absolute path of a netcdf file and returns a dictionary with the content

    Args:
        path (str): Path to the netcdf file
        
    Returns:
        dictionary: Returns a dictionary with netCDF variable names as keys

    """
    
    
    dataset = Dataset(path)
    variables_in_file =  dataset.variables.keys()
    temp_data = {}
    for key in variables_in_file:
        temp_data[key] =  dataset.variables[key][:]
    dataset.close()
    return temp_data


def merge_chirp(netcdf_dict):
    
    """
    merge_chirp: takes a dictionary containing radar data and returns the concatenated chirp tables 

    Args:
        netcdf_dict (sictionary): dictionary obtained from netcdf file with read_rph_netcdf()
        
    Returns:
        time: Returns time array from netcdf file(seconds since...)
        range_concat: Returns the range in meters of the concatenated reflectivity array
        reflectivity_concat: Returns the CZE value for all the chirp tables as one array of size len(time) X len(range)

    """
    nb_chirp_tables = netcdf_dict["ChirpNum"]
    range_val = []
    reflectivity_factor = []
    time = netcdf_dict["Time"].data
    for i in range(nb_chirp_tables):
        range_val.append(netcdf_dict["C"+str(i+1)+"Range"].data)
        reflectivity_factor.append(netcdf_dict["C"+str(i+1)+"ZE"].data)
    
    reflectivity_concat = np.concatenate(reflectivity_factor,axis=1)
    reflectivity_concat[np.where(reflectivity_concat==-999)] = np.nan
    range_concat = np.concatenate(range_val)
    return time,range_concat,reflectivity_concat
    
### Binning height of measurement to lower vertical resolution
def create_bins(lower_bound, higher_bound,width):
    """ create_bins returns an equal-width (distance) partitioning. 
        It returns an ascending list of tuples, representing the intervals.
        A tuple bins[i], i.e. (bins[i][0], bins[i][1])  with i > 0 
        and i < quantity, satisfies the following conditions:
            (1) bins[i][0] + width == bins[i][1]
            (2) bins[i-1][0] + width == bins[i][0] and
                bins[i-1][1] + width == bins[i][1]
    """
    
    bins = []
    for low in np.linspace(lower_bound, 
                     higher_bound,int((higher_bound-lower_bound)/ (width-1))):
        bins.append((low, low+width))
    return bins

def find_bin(value, bins):
    """ bins is a list of tuples, like [(0,20), (20, 40), (40, 60)],
        binning returns the smallest index i of bins so that
        bin[i][0] <= value < bin[i][1]
    """
    
    for i in range(0, len(bins)):
        if bins[i][0] <= value < bins[i][1]:
            return i
    min_dist = 999999999999
    ret_val =-1
    for i in range(0, len(bins)):
        if bins[i][-1]- value <= min_dist:
            min_dist = bins[i][-1]- value
            ret_val = i
    
        
    return ret_val

### Filter noise out of radar data by applying opening followed by closing
def filter_rpg(data,structure=0):
    """
    filter_rpg: takes a numpy array, creates a boolean array of the same size with False for NAN values and true for the rest
                Filters the noise by using an opening and clossing matematical operation

    Args:
        data: the 2d numpy array that should be filtered
        structure: TODO// should permit the user to select a filtering kernel
        
    Returns:
        mask: returns a boolean mask with True for valid values and False for Nan values

    """
    bin_mask_daily_reflectivity = np.copy(data)
    bin_mask_daily_reflectivity[np.where(np.logical_not(np.isnan(bin_mask_daily_reflectivity))) ] = 1
    bin_mask_daily_reflectivity[np.where(np.isnan(bin_mask_daily_reflectivity)) ] = 0
    
    #eroded_mask = ndimage.binary_erosion(bin_mask_daily_reflectivity,structure = ndimage.generate_binary_structure(2, 1))
    open_mask = ndimage.binary_opening(bin_mask_daily_reflectivity,structure = ndimage.generate_binary_structure(2, 1))
    #dilated_mask = ndimage.binary_dilation(open_mask,structure = ndimage.generate_binary_structure(2, 1)) 
    close_mask = ndimage.binary_closing(open_mask,structure = ndimage.generate_binary_structure(2, 2))
    
    
    return close_mask
    
### Averaging in height with binning
def average_in_height(time_array,height_array,data_array,height_bin_size=100,time_bin_size=3600):
    """
    average_in_height:  function that averages the radar signal height wise

    Args:
        time_array: numpy 1d array with timestamps
        height_array: numpy 1d array with height range
        data_array:  numpy 2d array size len(time_array) X len(height_array)
        height_bin_size: the averaging window in meters
        time_bin_size: the averaging window in seconds//NOT USED
        
    Returns:
        bin_range: returns the new height dimension
        pixel_in_bin: returns what pixels from the old range dimension got binned togethr
        heigh_averaged: the data averaged over height size len(time_array) X len(bin_range) 
        
    """
    bins = create_bins(height_array[0],height_array[-1],height_bin_size) 
    bin_range = [bini[0] for bini in bins]
    pixel_in_bin = []
    for height in height_array:
        pixel_in_bin.append(find_bin(height,bins))
    
    max_val = np.max(pixel_in_bin)
    pixel_in_bin = np.array(pixel_in_bin)
    heigh_averaged = []
    
    for i in range(max_val+1):
        temp_average = np.nanmean(data_array[:,np.where(pixel_in_bin==i)[0]],axis=1)
        heigh_averaged.append(temp_average)
    heigh_averaged = np.stack(heigh_averaged,axis=1)
    return bin_range,pixel_in_bin,heigh_averaged

### Averaging in time with binning
def average_in_time(time_array,height_array,data_array,height_bin_size=100,time_bin_size=3600):
    """
    average_in_time:  function that averages the radar signal time wise

    Args:
        time_array: numpy 1d array with timestamps
        height_array: numpy 1d array with height range
        data_array:  numpy 2d array size len(time_array) X len(height_array)
        height_bin_size: the averaging window in meters//NOT USED
        time_bin_size: the averaging window in seconds
        
    Returns:
        bin_range: returns the new time dimension
        pixel_in_bin: returns what pixels from the old time dimension got binned togethr
        time_averaged: the data averaged over time size len(bin_range) X len(height_array) 
        
    """
    past_time = time_array[0]
    bins = []
    for time in time_array:
        if past_time + time_bin_size > time:
            continue
        else:
            bins.append((past_time,time))
            past_time = time
    bins.append((time,time_array[-1]))
    #bins = create_bins(time_array[0],time_array[-1],time_bin_size)
    bin_range = [bini[0] for bini in bins]
    pixel_in_bin = []
    for time in time_array:
        pixel_in_bin.append(find_bin(time,bins))
    
    max_val = np.max(pixel_in_bin)
    pixel_in_bin = np.array(pixel_in_bin)
    time_averaged = []
    for i in range(max_val+1):
        temp_average = np.nanmean(data_array[np.where(pixel_in_bin==i)[0],:],axis=0)
        time_averaged.append(temp_average)
    time_averaged = np.stack(time_averaged,axis=1)
    return bin_range,pixel_in_bin,time_averaged

### Averaging in time and spacewith binning
def average(time_array,height_array,data_array,height_bin_size=100,time_bin_size=3600):
    """
    average:  function that averages the radar signal by height and time

    Args:
        time_array: numpy 1d array with timestamps
        height_array: numpy 1d array with height range
        data_array:  numpy 2d array size len(time_array) X len(height_array)
        height_bin_size: the averaging window in meters
        time_bin_size: the averaging window in seconds
        
    Returns:
        time: returns the new time dimension
        height: returns the new height dimension
        averaged: the data averaged  size len(time) X len(height) 
        
    """
    past_time = time_array[0]
    bins_time = []
    for time in time_array:
        if past_time + time_bin_size > time:
            continue
        else:
            bins_time.append((past_time,time))
            past_time = time
    bins_time.append((time,time_array[-1]))
    
    bin_range_time = [bini[0] for bini in bins_time]
    pixel_in_bin_time = []
    for time in time_array:
        pixel_in_bin_time.append(find_bin(time,bins_time))
    
    max_val_time = np.max(pixel_in_bin_time)
    pixel_in_bin_time = np.array(pixel_in_bin_time)
    
    
    bins = create_bins(height_array[0],height_array[-1],height_bin_size) 
    bin_range = [bini[0] for bini in bins]
    pixel_in_bin = []
    for height in height_array:
        pixel_in_bin.append(find_bin(height,bins))
    
    max_val = np.max(pixel_in_bin)
    pixel_in_bin = np.array(pixel_in_bin)
    
    averaged = np.zeros((len(bins_time),len(bins)))
    for i in range(max_val_time+1):
        for j in range(max_val+1):
            min_time =  np.where(pixel_in_bin_time==i)[0][0]
            max_time =  np.where(pixel_in_bin_time==i)[0][-1]
            min_height = np.where(pixel_in_bin==j)[0][0]
            max_height = np.where(pixel_in_bin==j)[0][-1]
            temp_selection = data_array[min_time:max_time,min_height:max_height]
            temp_average = np.nanmean(temp_selection)
            averaged[i,j] = temp_average
        
    time = bin_range_time
    height = bin_range
    return time,height,averaged
    
    
### Plot radar data ###
def plot_rpg(time_array, height_array, data_array,name="test_file",title="test title",min_v=0,max_v=0):
    """
    plot_rpg:  

    Args:
        time_array: numpy 1d array containing timestamp
        height_array: numpy 1d array height
        data_array:  the data to be visualized size len(time) X len(height) 
    Optional_Args:
        name="test_file" name of the saved file
        title="test title" title of plot
        min_v=0 min value for colorscale
        max_v=0 max value for colorscale
        
    Returns:
        
    """
    if min_v == max_v and min_v==0:
        min_v = -40
        max_v = 20
    plt.figure(figsize=(60,20))
    cmap_v = cm.get_cmap('viridis', 8)
    m = np.ma.masked_where(np.isnan(data_array),data_array)
    plt.pcolormesh(time_array, height_array,m.T,cmap = cmap_v,vmin=min_v,vmax=max_v)
    plt.title(title)
    plt.colorbar()
    plt.savefig(name+".png")
    
