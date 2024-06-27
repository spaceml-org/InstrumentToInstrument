"""
==========================
Translation of SWAP to AIA
==========================
This example shows how to enhance `PROBA2/SWAP <https://proba2.sidc.be/about/SWAP>`__ observations to `SDO/AIA <https://sdo.gsfc.nasa.gov/mission/instruments.php>`__ observations.
"""

from iti.evaluation.util import *
import glob
from iti.download.download_proba2 import PROBA2Downloader
from iti.download.download_sdo import SDODownloader
from iti.data.editor import proba2_norm
from iti.translate import *
from datetime import timedelta, datetime

base_path = os.getcwd()

############################################################################################################################################################################
# We provide a publicly available dataset which allows the users to play around with a subset of the data available without downloading the entire database.
#
# This dataset contains `.fits` files from **PROBA2/SWAP**, **SDO/AIA** and **Solar Orbiter/EUI (FSI and HRI)**.
#
# In addition 3 trained models are stored with:
# 1. PROBA2/SWAP to SDO/AIA
# 2. Solar Orbiter/EUI FSI to SDO/AIA and
# 3. SDO/AIA to Solar Orbiter/EUI HRI
#
# to perform the translation.

download_gcp_bucket('iti-dataset', base_path+'/iti-testset/')

# If you wish to translate different time periods that are not included in the test dataset, we provide download routines for the instruments used for ITI.
# In order to download data from JSOC (SDO) you need to register your email at `JSOC <http://jsoc.stanford.edu/ajax/register_email.html>`__. If you are registered you can set the environment variable ``JSOC_EMAIL`` to your email address.
############################################################################################################################################################################
# Downloading SWAP data
swap_downloader = PROBA2Downloader(base_path=base_path+'/swap')
swap_downloader.downloadDate(date=datetime(2024, 5, 8, 15))

############################################################################################################################################################################
# Downloading AIA data
jsoc_email = os.environ["JSOC_EMAIL"]

sdo_downloader = SDODownloader(base_path=base_path+'/sdo', email=jsoc_email)
sdo_downloader.downloadDate(date=datetime(2024, 5, 8, 15))

############################################################################################################################################################################
# Glob the downloaded files and sort them by date. For SDO we use observations only the 171 Ångström channel.
swap_files = sorted(glob.glob('swap/*/*.fits', recursive=True))
sdo_files = sorted(glob.glob('sdo/171/*.fits', recursive=True))

############################################################################################################################################################################
# In the next step we load the `.fits`files as SunPy maps. Here we crop the observations to 1.1 solar radii to cover the same Field-of-View (FOV).
# For SDO/AIA this additionally includes a degradation correction of the instrument.
swap_data = [getSWAPdata(f) for f in tqdm(swap_files)]
aia_data = [getAIAdata(f) for f in tqdm(sdo_files)]


############################################################################################################################################################################
# The translator classes are the core element of the ITI translation. They follow the notation: `InstrumentAToInstrumentB`. We initialize the translation class by giving it the path where the model is stored.

translator = SWAPToAIA(model_name=base_path+'/iti-testset/models/swap_to_aia_v0_4.pt', patch_factor=3)

############################################################################################################################################################################

# The result of the ITI translation is a SunPy map that stores all necessary coordinate information.

iti_maps = list(translator.translate(swap_files))

############################################################################################################################################################################
# Now that we have the translated maps, we can plot them side by side with the original data and the ground truth.

fig, axs = plt.subplots(1, 3, subplot_kw={'projection': aia_data[0]}, figsize=(40, 20), dpi=100)
swap_data[0].plot(axes=axs[0], norm=proba2_norm[174])
aia_data[0].plot(axes=axs[1], norm=sdo_norms[171])
iti_maps[0].plot(axes=axs[2], norm=sdo_norms[171])
axs[0].set_title('Original-SWAP', fontsize=30)
axs[1].set_title('Ground Truth-AIA', fontsize=30)
axs[2].set_title('ITI', fontsize=30)
plt.show()