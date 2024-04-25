***********
Translation
***********

After training the ITI model, we can translate between two image domains, which offers the three use cases of image enhancement,
instrument intercalibration, and super-resolution observations. For the translation process we use the built-in translate function
located in the ``iti.translate`` directory. Here you find the the translation classes for the different use cases. If you want to translate your own data
you can create a new translation class using the base class ``InstrumentToInstrument`` and implement the ``translate`` method.

===================
Example translation
===================

We provide an example of the translation process for image enhancement between the **PROBA2/SWAP** observations to **SDO/AIA** observations. To carry out the
translation, we need to open a python terminal and run::

    from iti.evaluation.evaluation import *

to import all dependencies.

----------------
Data preparation
----------------

We can then glob our images from the source domain and the target domain with::

    swap_files = sorted(glob.glob('path_to_aia_files/*.fits', recursive=True))
    aia_files = sorted(glob.glob('path_to_swap_files/*.fits', recursive=True))

------------
Data loading
------------

For later comparison we load the observations from both instruments as sunpy maps::

    swap_data = [getSWAPdata(f) for f in tqdm(swap_files)]
    aia_data = [getAIAdata(f) for f in tqdm(aia_files)]

This includes a cropping of the observations to 1.1 solar radii and a prep routine to account for the degradation of each instrument.

-----------
Translation
-----------
The next step is to translate the images from the source domain to the target domain::

    translator = SWAPtoAIA()
    iti_maps = translate(swap_files, translator)

Here, we initialize the translator and call the translate function with the source domain files and the translator. The function returns the translated images as sunpy maps.

-------------
Visualization
-------------
This allows us to visually compare the results of the translation process with the original images and the ground truth by running::

    plotImageComparison(original=swap_data[0], ground_truth=aia_data[0], iti=iti_maps[0], norm_original=proba2_norm[174], norm_ground_truth=sdo_norms[171], name='SWAPToAIA', path='path_to_save')


--------------
Saving to FITS
--------------

After the translation we can save the images as ``.fits`` files with::

    saveToFITS(iti_maps, 'path_to_save')

This saves the observations in the ``.fits`` format in the path specified. Each file is named according to the observation date, using the format ``YYYY-MM-DDTHH:MM:SS.fits``.
The translation process already includes an update and translation of the metadata. Saving to the ``.fits`` format therefore
allows all the necessary information of an observation to be stored in a single file, including image and metadata.