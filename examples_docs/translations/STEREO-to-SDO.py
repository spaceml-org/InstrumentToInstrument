"""
=================================================
Translation of STEREO/EIT-to-SDO/AIA observations
=================================================
This example shows how to intercalibrate `STEREO/EUVI <https://stereo.gsfc.nasa.gov/classroom/EUVsun.shtml>`__ observations to `SDO <https://sdo.gsfc.nasa.gov/mission/instruments.php>`__ observations.
"""

from iti.evaluation.util import *
import glob
from iti.translate import *
from matplotlib.colors import Normalize
from datetime import timedelta, datetime

base_path = os.getcwd()

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
# We load the previously downloaded STEREO files. The translator requires a list of the four aligned FITS files for each translation. We use a patch factor of 2 to save memory.

stereo_files = sorted(glob.glob(base_path+'/iti-testset/stereo/*/*.fits', recursive=True))
stereo_maps = [Map(f).rotate() for f in stereo_files] # rotate north up

translator = STEREOToSDO(patch_factor=2)
iti_stereo_maps = list(translator.translate([[f] for f in stereo_files]))[0]

############################################################################################################################################################################
# Now we plot the translated maps side by side with the original STEREO observations.

fig, axs = plt.subplots(2, 4, subplot_kw={'projection': stereo_maps[0]}, figsize=(40, 20), dpi=100)
for i, (stereo_map, iti_map) in enumerate(zip(stereo_maps, iti_stereo_maps)):
    stereo_map.plot(axes=axs[0, i])
    iti_map.plot(axes=axs[1, i])
    axs[0, i].set_title('STEREO/EUVI', fontsize=20)
    axs[1, i].set_title('ITI', fontsize=20)
plt.show()