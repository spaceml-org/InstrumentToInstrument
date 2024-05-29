"""
==========================
Dataloaders: Solar Orbiter
==========================
This example shows how to preprocess Solar Orbiter EUI data to obtain ML-ready data using the ITI tool.
"""

import glob
from iti.evaluation.util import *
from iti.data.editor import solo_norm
from iti.translate import *
from iti.data.dataset import get_intersecting_files, EUIDataset, HRIDataset
from sunpy.map import Map

base_path = os.getcwd()

############################################################################################################################################################################
# As the first step, we need to download the data. We make use of our publicly available dataset which allows the users to play around with a subset of the data available without downloading the entire database.

download_gcp_bucket('iti-dataset', base_path+'/iti-testset/')
############################################################################################################################################################################
# The EUI instrument is equipped with the Full Sun Imager (FSI) and the High-resolution Imager (HRI). We can glob the files for each instrument separately.

fsi_files = get_intersecting_files(base_path+'/iti-testset/solo', ['eui-fsi174-image', 'eui-fsi304-image'])
hri_files = sorted(glob.glob(base_path+'/iti-testset/solo/eui-hrieuv174-image/*.fits', recursive=True))
############################################################################################################################################################################
# To preprocess the data, we use Editor classes. These classes allow to apply different operations on the data, such as normalization, cropping etc. The Editor classes are stacked and applied sequentially to the data.
#

# For Solar Orbiter/EUI we:
#   - load the `.fits` files as SunPy maps
#   - crop the observations to 1.1 solar radii
#   - transform the maps to data arrays
#   - normalize the data to an interval between [-1, 1]
#   - reshape to channel first format [channel, height, width]

fsi_dataset = EUIDataset(fsi_files)
hri_dataset = HRIDataset(hri_files)
############################################################################################################################################################################
# We can now compare the original data with the preprocessed ML-ready ITI data. Here we load the FSI and HRI files as SunPy maps.

fsi174_maps = [Map(f) for f in fsi_files[0]]
fsi304_maps = [Map(f) for f in fsi_files[1]]
hri_maps = [Map(f) for f in hri_files]

############################################################################################################################################################################
# Plot the FSI observations with the ITI data

fig, axs = plt.subplots(2, 2, subplot_kw={'projection': fsi174_maps[0]}, figsize=(40, 30), dpi=100)
fsi174_maps[0].plot(axes=axs[0, 0])
axs[0, 1].imshow(fsi_dataset[0][0], cmap='sdoaia171', vmin=-1, vmax=1, origin='lower')
fsi304_maps[0].plot(axes=axs[1, 0])
axs[1, 1].imshow(fsi_dataset[0][1], cmap='sdoaia304', vmin=-1, vmax=1, origin='lower')
axs[0, 0].set_axis_off()
axs[0, 1].set_axis_off()
axs[1, 0].set_axis_off()
axs[1, 1].set_axis_off()
axs[0, 0].set_title('Original FSI 174 Å', fontsize=50)
axs[0, 1].set_title('ITI 174 Å', fontsize=50)
axs[1, 0].set_title('Original FSI 304 Å', fontsize=50)
axs[1, 1].set_title('ITI 304 Å', fontsize=50)
plt.show()

############################################################################################################################################################################
# Plot the HRI observations with the ITI data

fig, axs = plt.subplots(1, 2, subplot_kw={'projection': hri_maps[0]}, figsize=(20, 10), dpi=100)
hri_maps[0].plot(axes=axs[0])
axs[1].imshow(hri_dataset[0][0], cmap='sdoaia171', vmin=-1, vmax=1, origin='lower')
axs[0].set_axis_off()
axs[1].set_axis_off()
axs[0].set_title('Original HRI 174 Å', fontsize=50)
axs[1].set_title('ITI 174 Å', fontsize=50)
plt.show()