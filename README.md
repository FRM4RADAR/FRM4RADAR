# FRM4RADAR
A small repository for the development of a common codebase for radar data processing and visualization in python.
For questions and ideas contact me at mihai.boldeanu@inoe.ro

# Summary
Dependencies for this library are:
- numpy 
- netcdf4
- matplotlib
- scipy
- datetime

So far code uploaded to this repository was made for :
- netCDF4 file handling
- concatenating data in files based on the number of chirp tables used
- hourly to daily conversions
- visualization of the data
- filtering of noise

TODO:
- converting timestamps from seconds since... to datetime objects 
- saving processed files as daily files (only creates plots at the moment)
- more options regarding the averaging(selecting a timestamp or height level to average around)
- adding error handling if the averaging values are invalid

# Exmaple of data processing
The following pictures show the data processing flow:
- Original Data
![Alt text](/images/00_original_data.png?raw=true "Original data")
- Filtered Data (noise saved as separate array)
![Alt text](/images/01_filtered_data.png?raw=true "Filtered data")
- Averaging done on th eheight dimension
![Alt text](/images/averaged_data_500.png?raw=true "Averaged Height wise")
- Averaging done on the time dimension
![Alt text](/images/averaged_data_1h.png?raw=true "Averaged Time wise")
- Averaging done on the time and height simultaneously
![Alt text](/images/00_averaged_raw.png?raw=true "Averaged Time wise")




