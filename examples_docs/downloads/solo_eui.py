"""
=========================
Download Solar Orbiter/EUI data
=========================
This example shows how to download Solar Orbiter EUI data from the `Solar Orbiter archive (SOAR) <https://soar.esac.esa.int/soar/#home>`__ using the ITI tool.
"""


import glob
import os
from datetime import datetime
from sunpy.map import Map
import matplotlib.pyplot as plt

from iti.download.download_solo import SOLODownloader

###############################################################################
# Initialize path where to download the data
base_path = os.getcwd()

###############################################################################
# Set up the downloader for Solar Orbiter/eUI with the path to download the data
#
# The EUI instrument on Solar Orbiter is equipped with two imagers, the Full Sun Imager (FSI) and the High Resolution Imager (HRI).
# By setting the flag `FSI` to `True` we download the FSI data, otherwise the HRI data is downloaded.
downloader = SOLODownloader(base_path=base_path+'/eui')

###############################################################################
# Download the data for a specific date
downloader.downloadDate(date=datetime(2022, 4, 5, 2, 30), FSI=True)
downloader.downloadDate(date=datetime(2022, 4, 5, 2, 30), FSI=False)

###############################################################################
# Glob the downloaded files and sort them by date
eui_files = sorted(glob.glob('eui/*/*.fits', recursive=True))

###############################################################################
# In the next step we load the `.fits`files as SunPy maps.
fsi174_map = Map(eui_files[0])
fsi304_map = Map(eui_files[1])
hri_map = Map(eui_files[2])

###############################################################################
# We can visualize the map of the two instruments using the SunPy plotting capabilities
fig, axs = plt.subplots(1, 3, figsize=(15, 5))
fsi174_map.plot(axes=axs[0])
fsi304_map.plot(axes=axs[1])
hri_map.plot(axes=axs[2])
plt.show()