"""
===============================================
Translation of SOHO/EIT-to-SDO/AIA observations
===============================================
This example shows how to intercalibrate `SOHO <https://umbra.nascom.nasa.gov/eit/>`__ observations to `SDO <https://sdo.gsfc.nasa.gov/mission/instruments.php>`__ observations.
"""
from iti.evaluation.util import *
import glob
from iti.translate import *
from matplotlib.colors import Normalize
from datetime import timedelta, datetime

base_path = os.getcwd()

############################################################################################################################################################################
# For the translation of SOHO/EIT observations we make use of the multi-channel representation and translate all four EUV channels as well as the magnetogram channel simultaneous. For this application we use half of the SDO resolution as reference for our enchancement.

############################################################################################################################################################################
# We provide a publicly available dataset which allows the users to play around with a subset of the data available without downloading the entire database.
#
# This dataset contains `.fits` files from **PROBA2/SWAP**, **SDO/AIA**, **Solar Orbiter/EUI (FSI and HRI)**, **SOHO/EIT** and **STEREO/EUVI**.
#
# In addition 3 trained models are stored with:
# 1. PROBA2/SWAP to SDO/AIA
# 2. Solar Orbiter/EUI FSI to SDO/AIA and
# 3. SDO/AIA to Solar Orbiter/EUI HRI
#
# to perform the translation.

download_gcp_bucket('iti-dataset', base_path+'/iti-testset/')

############################################################################################################################################################################
# We load the previously downloaded SOHO files. The translator requires a list of the four aligned FITS files for each translation. We use a patch factor of 2 to save memory.

soho_files = sorted(glob.glob(base_path+'/iti-testset/soho/*/*.fits', recursive=True))
soho_maps = [Map(f).rotate() for f in soho_files] # rotate north up

translator = SOHOToSDO(patch_factor=2)
iti_soho_maps = list(translator.translate([[f] for f in soho_files]))[0]

############################################################################################################################################################################
# We set the magnetograms to a fixed value range [-1000, 1000]

iti_soho_maps[-1].plot_settings['norm'] = Normalize(vmin=-1000, vmax=1000)
soho_maps[-1].plot_settings['norm'] = Normalize(vmin=-1000, vmax=1000)

############################################################################################################################################################################
# Now we plot the translated maps side by side with the original SOHO observations.

fig, axs = plt.subplots(2, 5, subplot_kw={'projection': soho_maps[0]}, figsize=(40, 20), dpi=100)
for i, (soho_map, iti_map) in enumerate(zip(soho_maps, iti_soho_maps)):
    soho_map.plot(axes=axs[0, i])
    iti_map.plot(axes=axs[1, i])
    axs[0, i].set_title('SOHO/EIT', fontsize=30)
    axs[1, i].set_title('ITI', fontsize=30)
plt.show()