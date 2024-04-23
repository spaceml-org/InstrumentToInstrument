***********
Translation
***********

After training the ITI model, we can translate between image domains, which offers the three use cases with image enhancement, instrument intercalibration and super-resolution
observations. For the translation process we use the build in translate function which can be found in the ``iti.translate`` folder. The function only requires as input the files
of the images of the source domain.

===================
Example translation
===================

We provide an example of the translation process between the **PROBA2/SWAP** observations to **SDO/AIA** observations. To carry out the translation, we need to open a python terminal
and run::

    from iti.evaluation.evaluation import *

to import all dependencies. We can then glob our images from the source domain and the target domain::

    swap_files = sorted(glob.glob('path_to_aia_files/*.fits', recursive=True))
    aia_files = sorted(glob.glob('path_to_swap_files/*.fits', recursive=True))

For later comparison we load both instrument observations as sunpy maps::

    swap_data = [getSWAPdata(f) for f in tqdm(swap_files)]
    aia_data = [getAIAdata(f) for f in tqdm(aia_files)]

This includes a cropping of the observations to 1.1 solar radii and a prep routine to account for the degradation of the instruments.
The next step is to translate the images from the source domain to the target domain::

    translator = SWAPtoAIA()
    iti_maps = translate(swap_files, translator)

Here, we initialize the translator and call the translate function with the source domain files and the translator. The function returns the translated images as sunpy maps.
This allows us to visually compare the results of the translation process with the original images and the ground truth::

    plotImageComparison(original=swap_data[0], ground_truth=aia_data[0], iti=iti_maps[0], norm_original=proba2_norm[174], norm_ground_truth=sdo_norms[171], name='SWAPToAIA', path='path_to_save')
