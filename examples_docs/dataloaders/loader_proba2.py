"""
===================
Dataloaders: PROBA2
===================
This example shows how to preprocess PROBA2 data to obtain ML-ready data using the ITI tool.
"""
import glob

from iti.evaluation.evaluation import *
from iti.data.editor import solo_norm
from iti.translate import *
from iti.data.dataset import get_intersecting_files, SWAPDataset
from sunpy.map import Map

base_path = os.getcwd()

############################################################################################################################################################################
# As the first step, we need to download the data. We make use of our publicly available dataset which allows the users to play around with a subset of the data available without downloading the entire database.

download_gcp_bucket('iti-dataset', base_path+'/iti-testset/')
############################################################################################################################################################################
# Glob the downloaded files and sort them by date.

swap_files = sorted(glob.glob(base_path+'/iti-testset/proba2/*/*.fits', recursive=True))
############################################################################################################################################################################
# To preprocess the data, we use Editor classes. These classes allow to apply different operations on the data, such as normalization, cropping etc. The Editor classes are stacked and applied sequentially to the data.
#
# For PROBA2/SWAP we:
#   - load the `.fits` files as SunPy maps
#   - crop the observations to 1.1 solar radii
#   - transform the maps to data arrays
#   - normalize the data to an interval between [-1, 1]
#   - reshape to channel first format [channel, height, width]

swap_dataset = SWAPDataset(swap_files)
############################################################################################################################################################################
# We can now compare the original data with the preprocessed ML-ready ITI data. Here we load the aia files as SunPy maps and visualize them with the ITI data.

swap_maps = [Map(f) for f in swap_files]


fig, axs = plt.subplots(1, 2, subplot_kw={'projection': swap_maps[0]}, figsize=(20, 10), dpi=100)
swap_maps[0].plot(axes=axs[0])
axs[1].imshow(swap_dataset[0][0], cmap='sdoaia171', vmin=-1, vmax=1, origin='lower')
axs[0].set_axis_off()
axs[1].set_axis_off()
axs[0].set_title('Original SWAP 174 Å', fontsize=50)
axs[1].set_title('ITI 171 Å', fontsize=50)
plt.show()
