"""
===============================================
Translation of Solar Orbiter/EUI/FSI to SDO/AIA
===============================================
This example shows how to intercalibrate `Solar Orbiter/EUI/FSI <https://sci.esa.int/web/solar-orbiter/-/51217-instruments>`__ observations to `SDO/AIA <https://sdo.gsfc.nasa.gov/mission/instruments.php>`__ observations.
"""

from iti.evaluation.util import *
from iti.data.editor import solo_norm
from iti.translate import *
from iti.data.dataset import get_intersecting_files

base_path = os.getcwd()

############################################################################################################################################################################
# We provide a publicly available dataset which allows the users to play around with a subset of the data available without downloading the entire database.
#
# This dataset contains `.fits` files from **PROBA2/SWAP**, **SDO/AIA** and **Solar Orbiter/EUI (FSI and HRI)**.
download_gcp_bucket('iti-dataset', base_path+'/iti-testset/')

############################################################################################################################################################################
# Glob the downloaded files and sort them by date. Here we use the two channels in 171/174 Å and 304 Å.
fsi_files = get_intersecting_files(base_path+'/iti-testset/solo', ['eui-fsi174-image', 'eui-fsi304-image'])
aia_files = get_intersecting_files(base_path+'/iti-testset/sdo', [171, 304])

############################################################################################################################################################################
# In the next step we load the `.fits`files as SunPy maps. Here we crop the observations to 1.1 solar radii to cover the same Field-of-View (FOV).
# For SDO/AIA this additionally includes a degradation correction of the instrument.
fsi_data_174 = [getFSIdata(f) for f in tqdm(fsi_files[0])]
fsi_data_304 = [getFSIdata(f) for f in tqdm(fsi_files[1])]

aia_data_171 = [getAIAdata(f) for f in tqdm(aia_files[0])]
aia_data_304 = [getAIAdata(f) for f in tqdm(aia_files[1])]


############################################################################################################################################################################
# The translator classes are the core element of the ITI translation. They follow the notation: `InstrumentAToInstrumentB`. We initialize the translation class by giving it the path where the model is stored.

translator = FSIToAIA(model_name=base_path+'/iti-testset/models/fsi_to_aia_v0_3.pt')

############################################################################################################################################################################

# The result of the ITI translation is a SunPy map that stores all necessary coordinate information.

iti_maps = list(translator.translate(fsi_files))

############################################################################################################################################################################
# Now that we have the translated maps, we can plot them side by side with the original data and the ground truth.

fig, axs = plt.subplots(2, 3, subplot_kw={'projection': aia_data_171[0]}, figsize=(40, 30), dpi=100)
fsi_data_174[0].plot(axes=axs[0, 0], norm=solo_norm['eui-fsi174-image'])
aia_data_171[0].plot(axes=axs[0, 1], norm=sdo_norms[171])
iti_maps[0][0].plot(axes=axs[0, 2], norm=sdo_norms[171])
fsi_data_304[0].plot(axes=axs[1, 0], norm=solo_norm['eui-fsi304-image'])
aia_data_304[0].plot(axes=axs[1, 1], norm=sdo_norms[304])
iti_maps[0][1].plot(axes=axs[1, 2], norm=sdo_norms[304])
axs[0, 0].set_title('Original-FSI', fontsize=30)
axs[0, 1].set_title('Ground Truth-AIA', fontsize=30)
axs[0, 2].set_title('ITI', fontsize=30)
plt.show()