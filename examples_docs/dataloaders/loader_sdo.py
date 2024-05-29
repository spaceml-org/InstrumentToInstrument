"""
================
Dataloaders: SDO
================
This example shows how to preprocess SDO AIA data to obtain ML-ready data using the ITI tool.
"""

from iti.evaluation.util import *
from iti.data.editor import solo_norm
from iti.translate import *
from iti.data.dataset import get_intersecting_files, SDODataset
from sunpy.map import Map

base_path = os.getcwd()

############################################################################################################################################################################
# As the first step, we need to download the data. We make use of our publicly available dataset which allows the users to play around with a subset of the data available without downloading the entire database.

download_gcp_bucket('iti-dataset', base_path+'/iti-testset/')
############################################################################################################################################################################
# Glob the downloaded files and sort them by date. Here we use the two channels in 171 Å and 304 Å.

aia_files = get_intersecting_files(base_path+'/iti-testset/sdo', [171, 304])
############################################################################################################################################################################
# To preprocess the data, we use Editor classes. These classes allow to apply different operations on the data, such as normalization, cropping etc. The Editor classes are stacked and applied sequentially to the data.
#
# The sensitivity of the AIA instrument decreases over time. To correct for this, the SDO/AIA team is providing a degradation correction (`Boerner et al., 2012 <https://link.springer.com/article/10.1007/s11207-011-9804-8>`__) which is publicly available.
# For SDO/AIA we:
#   - load the `.fits` files as SunPy maps
#   - crop the observations to 1.1 solar radii
#   - apply a degradation correction of the instrument
#   - transform the maps to data arrays
#   - normalize the data to an interval between [-1, 1]
#   - reshape to channel first format [channel, height, width]

aia_dataset = SDODataset(aia_files, wavelengths=[171, 304], resolution=2048)
############################################################################################################################################################################
# We can now compare the original data with the preprocessed ML-ready ITI data. Here we load the aia files as SunPy maps and visualize them with the ITI data.

aia171_maps = [Map(f) for f in aia_files[0]]
aia304_maps = [Map(f) for f in aia_files[1]]

fig, axs = plt.subplots(2, 2, subplot_kw={'projection': aia171_maps[0]}, figsize=(40, 30), dpi=100)
aia171_maps[0].plot(axes=axs[0, 0])
axs[0, 1].imshow(aia_dataset[0][0], cmap='sdoaia171', vmin=-1, vmax=1, origin='lower')
aia304_maps[0].plot(axes=axs[1, 0])
axs[1, 1].imshow(aia_dataset[0][1], cmap='sdoaia304', vmin=-1, vmax=1, origin='lower')
axs[0, 0].set_axis_off()
axs[0, 1].set_axis_off()
axs[1, 0].set_axis_off()
axs[1, 1].set_axis_off()
axs[0, 0].set_title('Original AIA 171 Å', fontsize=50)
axs[0, 1].set_title('ITI 171 Å', fontsize=50)
axs[1, 0].set_title('Original AIA 304 Å', fontsize=50)
axs[1, 1].set_title('ITI 304 Å', fontsize=50)
plt.show()
