"""
=========================
Download SDO/AIA data
=========================
This example shows how to download SDO AIA data from the `Joint Science Operations Center (JSOC) <http://jsoc.stanford.edu/>`__ using the ITI tool.
"""


import os
from datetime import datetime
from sunpy.map import Map
import matplotlib.pyplot as plt

from iti.data.dataset import get_intersecting_files
from iti.download.download_sdo import SDODownloader

###############################################################################
# Initialize path where to download the data
base_path = os.getcwd()

###############################################################################
# Set up the downloader for SDO with the path to download the data
#
# The SDO downloader allows to download AIA data in all available wavelengths. In addition to the EUV observations from AIA, we can download the HMI magnetograms at 6173 Å.
jsoc_email = os.environ["JSOC_EMAIL"]
downloader = SDODownloader(base_path=base_path+'/sdo', email=jsoc_email, wavelengths=[171, 193, 211, 304])

###############################################################################
# Download the data for a specific date
downloader.downloadDate(date=datetime(2022, 4, 5, 5))

###############################################################################
# We can now glob the downloaded files and sort them by date
aia_files = get_intersecting_files(base_path+'/sdo', [171, 193, 211, 304, 6173])

###############################################################################
# In the next step we load the `.fits` files as SunPy maps.
aia_map171 = [Map(f) for f in aia_files[0]]
aia_map193 = [Map(f) for f in aia_files[1]]
aia_map211 = [Map(f) for f in aia_files[2]]
aia_map304 = [Map(f) for f in aia_files[3]]
aia_map6173 = [Map(f) for f in aia_files[4]]

###############################################################################
# We can visualize the map of the two instruments using the SunPy plotting capabilities
fig, axs = plt.subplots(1, 5, subplot_kw={'projection': aia_map171}, figsize=(20, 10), dpi=100)
aia_map171[0].plot(axes=axs[0])
aia_map193[0].plot(axes=axs[1])
aia_map211[0].plot(axes=axs[2])
aia_map304[0].plot(axes=axs[3])
aia_map6173[0].plot(axes=axs[4])
plt.show()