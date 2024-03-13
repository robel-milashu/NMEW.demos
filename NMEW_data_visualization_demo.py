#!/usr/bin/env python
# coding: utf-8

import numpy as np
from matplotlib import pyplot as plot, colors
from mpl_toolkits import basemap
from netCDF4 import Dataset, num2date
from matplotlib.colors import LinearSegmentedColormap


# Input file and data visualization settings
file = './results/daily/gcomc/chla/GS20200812_CHL_NW_day.nc'
varname = 'chlor_a'
font_size = 20
cmin, cmax = -2, 2
# for CHL we use lognorm
norm = colors.LogNorm(cmin, cmax)
# update the size of figure labels
plot.rcParams.update({'font.size': font_size})
# Assuming these are the coordinates you want to crop to
# lat_min_crop, lat_max_crop = 34.3, 35.7  # Update these values as needed
# lon_min_crop, lon_max_crop = 138.3, 140.23  # Update these values as needed

# # Small Sagami Bay
# lat_min_crop, lat_max_crop = 35.124, 35.34
# lon_min_crop, lon_max_crop = 139.115, 139.68

# Small Sagami Bay
lat_min_crop, lat_max_crop = 34.5, 35.4
lon_min_crop, lon_max_crop = 138.8, 139.9

# Define your color list in hex
hex_colors = [
    '#3500a8', '#0800ba', '#003fd6',
    '#00aca9', '#77f800', '#ff8800',
    '#b30000', '#920000', '#880000'
]


def momnthy_data(file): 
    print(file)
    # Read the dataset and geo-ref data
    with Dataset(file, 'r') as nc:
        sds = nc[varname][:] # the output is a numpy masked array
        sds = np.ma.squeeze(sds)  # Remove singleton dimensions if present
        print("Shape of 'sds' before cropping:", sds.shape)  # Add this line to check the shape

        sds = np.ma.squeeze(sds) # remove singleton dimensions
        label = nc[varname].units.replace('^-3', '$^{-3}$')
        lat = nc['lat'][:]
        lon = nc['lon'][:]
        
        # Find indices for cropping
        lat_inds = np.where((lat >= lat_min_crop) & (lat <= lat_max_crop))[0]
        lon_inds = np.where((lon >= lon_min_crop) & (lon <= lon_max_crop))[0]
        print(sds)
        # Crop data
            # Now add a check to ensure the indices are within the bounds of the array
        if lat_inds.size > 0 and lon_inds.size > 0:
            # Adjust the slicing based on the actual dimensions of sds
            sds_cropped = sds[lat_inds, :][:, lon_inds]  # This is the updated line for a 2D array
            lat_cropped = lat[lat_inds]
            lon_cropped = lon[lon_inds]
        else:
            print("No data within specified crop bounds.")
            
        # sds_cropped = sds[:, lat_inds, :][:, :, lon_inds]  # Assuming sds has a shape of [time, lat, lon]
        lat_cropped = lat[lat_inds]
        lon_cropped = lon[lon_inds]

        print(np.ma.mean(sds_cropped))
        
        time = num2date(nc['time'][:], 
                        units=nc['time'].units,
                        calendar=nc['time'].calendar)
        label = nc[varname].long_name.split(',')[0] + f' [{label}]'

    # Convert hex color list to RGB
    rgb_colors = [colors.hex2color(color) for color in hex_colors]


    # Visualisation with basemap
    if len(lon_cropped.shape) == 1:
        lon_cropped, lat_cropped = np.meshgrid(lon_cropped, lat_cropped)
    lon_0, lat_0 = (lon_cropped.min() + lon_cropped.max()), (lat_cropped.min() + lat_cropped.max()) / 2
    m = basemap.Basemap(llcrnrlon=lon_cropped.min(), llcrnrlat=lat_cropped.min(), 
                        urcrnrlon=lon_cropped.max(), urcrnrlat=lat_cropped.max(), resolution='i', 
                        lon_0=lon_0, lat_0=lat_0, projection='merc')

    # print(sds_cropped)
    sds_cropped_log = np.ma.masked_less_equal(sds_cropped, 0)  # Mask non-positive values
    sds_cropped_log = np.ma.log10(sds_cropped_log)  # Apply log10 to the data


    # Adjust figsize to change the aspect ratio
    fig, ax = plot.subplots(figsize=(7, 6))  # Adjust the width and height to better suit your data aspect ratio

    # figure bounds
    extent = [lon_cropped.min(), lon_cropped.max(), lat_cropped.min(), lat_cropped.max()]

    # Land mask
    mask = np.where(~sds_cropped_log.mask, np.nan, 0)
    ax.imshow(mask, cmap='gray', vmin=-2, vmax=0, extent=extent)

    # Create a colormap object
    custom_colormap = LinearSegmentedColormap.from_list('custom', rgb_colors)

    print(sds_cropped_log.max(), sds_cropped_log.min())
    # We no longer use LogNorm here since we've manually applied log10
    # ims = ax.imshow(sds_cropped_log, cmap='jet', extent=extent)
    ims = ax.imshow(sds_cropped_log,vmin=cmin, vmax=cmax,  cmap=custom_colormap, extent=extent)

    # # Figure labels
    ax.set_xlabel('Longitude [$^\mathregular{o}$E]', fontsize="12")
    ax.set_ylabel('Latitude [$^\mathregular{o}$N]', fontsize="12")
    ax.set_yticks(range(int(np.ceil(lat_cropped.min())), int(np.ceil(lat_cropped.max())) + 1, 1))
    # ax.set_title(time[0].strftime('%b %Y'))

    # # Colourbar
    cbar = fig.colorbar(ims, ax=ax, orientation='vertical', fraction=0.0324, pad=0.025,  aspect=15)
    # cbar.set_label('log10(Chl-a) Conc. mg/m^3', fontsize="12")

    ticks = [ims.get_clim()[0],0, ims.get_clim()[1]] # This gets the color limit range
    cbar.set_ticks(ticks)
    cbar.set_ticklabels([f'{ticks[0]:.2f}', f'{ticks[1]:.2f}', f'{ticks[2]:.2f}']) # Format as desired

    # plot.savefig("test.png", dpi=300)
    # plot.savefig(f'./results/daily/Modis/chla/pics/{file.split("/")[-1].split(".")[0]}.png', dpi=300)
    plot.show()

import os
count = 0
# iterate folders
for file in os.listdir(f'./results/daily/Modis/chla/'):
    print("./results/daily/Modis/chla/"+file)
    count += 1
    if count > 5 :
        break
    # check for file extension 
    if file.endswith('.nc'):
        momnthy_data("./results/daily/Modis/chla/"+file)



