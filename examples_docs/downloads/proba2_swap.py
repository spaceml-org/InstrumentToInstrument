import glob
import os
from datetime import datetime
from sunpy.map import Map
import matplotlib.pyplot as plt

from iti.download.download_proba2 import Proba2Downloader

###############################################################################
# Initialize path where to download the data
base_path = os.getcwd()

###############################################################################
# Set up the downloader for PROBA2/SWAP with the path to download the data
downloader = Proba2Downloader(base_path=base_path+'/swap')

###############################################################################
# Download the data for a specific date
downloader.downloadDate(date=datetime(2023, 5, 8, 15))

###############################################################################
# Glob the downloaded files and sort them by date
swap_files = sorted(glob.glob('swap/*/*.fits', recursive=True))

###############################################################################
# In the next step we load the `.fits`files as SunPy maps.
swap_map = Map(swap_files[0])

###############################################################################
# We can visualize the map with its metadata
print(swap_map)

###############################################################################
# And plot the map
plt.figure(figsize=(10, 10))
swap_map.plot()
plt.show()

