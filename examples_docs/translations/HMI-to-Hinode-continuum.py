"""
===============================================
Translation of SDO/HMI-to-Hinode/SOT continuum
===============================================
This example shows how to enhance `SDO/HMI <https://sdo.gsfc.nasa.gov/mission/instruments.php>`__ observations to `Hinode/SOT <https://hinode.nao.ac.jp/en/for-researchers/instruments/sot/>`__ observations.
Here we super-resolve HMI observations with 4096x4096 pixels by a factor 4. The model was trained with observations from Hinode/SOT to infer the resolution increase.
"""

from iti.download.download_hmi_continuum import HMIContinuumDownloader
from iti.translate import *

from matplotlib import pyplot as plt
from datetime import datetime

from astropy import units as u
from astropy.coordinates import SkyCoord
import warnings

############################################################################################################################################################################
# We start by downloading FITS files from SDO/HMI continuum. ITI provides a download routines for multiple data sets, here we utilize the HMIContinuumDownloader. We download an observation from 2021-09-09.

jsoc_email = os.environ["JSOC_EMAIL"]
fetcher = HMIContinuumDownloader(ds_path='hmi', email=jsoc_email, num_worker_threads=4)
hmi_files = fetcher.fetchDates([datetime(2021, 9, 9, 15)])
print('downloaded:', hmi_files)

############################################################################################################################################################################
# For later comparison we load the HMI FITS file as SunPy Map.

hmi_map = Map(hmi_files[0])
hmi_map.data[np.isnan(hmi_map.data)] = 0

############################################################################################################################################################################
# For HMI files we need to translate the image in patches (patch_factor=3), otherwise we would exceed the memory. The first initialization of each translator triggers the download of the pre-trained model and stores it locally for later use.

translator = HMIToHinode(patch_factor=2)

############################################################################################################################################################################
# The translate function starts the translation process of the HMI FITS files and returns a genartor object. This can be used to sequentially process the results. Here we only translate a single file and convert the generator object to a list.

iti_hmi_map = list(translator.translate(hmi_files))[0]

############################################################################################################################################################################
# The result of the ITI translation is a SunPy map that stores all necessary coordinate information. We can compare this map to the original HMI observation.

#fig, axs = plt.subplots(1, 2, subplot_kw={'projection': hmi_map}, figsize=(20, 10), dpi=100)
#hmi_map.plot(axes=axs[0])
#iti_hmi_map.plot(axes=axs[1])
#axs[0].set_title('Original-HMI', fontsize=20)
#axs[1].set_title('ITI', fontsize=20)
#plt.show()
#plt.close()

############################################################################################################################################################################
# For a comparison at smaller scales we can specify a subframe and plot the images side-by-side.


#bl = SkyCoord(-5 * u.arcsec, -440 * u.arcsec, frame=hmi_map.coordinate_frame)
#tr = SkyCoord(55 * u.arcsec, -380 * u.arcsec, frame=hmi_map.coordinate_frame)

#fig, axs = plt.subplots(1, 2, figsize=(20, 10), sharex=True, sharey=True)
#hmi_map.submap(bl, top_right=tr).plot(axes=axs[0])
#axs[0].set_title('Original - HMI')
#iti_hmi_map.submap(bl, top_right=tr).plot(axes=axs[1])
#axs[1].set_title('ITI')
#plt.show()
#plt.close()
