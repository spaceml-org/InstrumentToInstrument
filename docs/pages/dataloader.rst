***********
Dataloaders
***********

Instrument-to-Instrument translation is designed as general framework that can be easily applied to similar tasks.
Many of the basic data loading, normalizing and scaling operations are already implemented by editors and can be used for
the creation of new data sets, while also new custom editors can be added.

=======================
Create custom Datasets
=======================

ITI uses the pytorch Dataset class as basis for loading data. The easiest way to create a new data sets is the use of existing
data editors and the BaseDataset class. The BaseDataset requires the path to the files or a list of file paths. The data processing
pipeline can be customized by specifying editors, that will be sequentially applied to the data. The first editor receives a file path.
The output of each editor serve as input for the next editor. In the example bellow we implement a custom data set for
HMI magnetograms that:

1. loads a SunPy map from the file
2. centers the solar disk and scales the image to 2048
3. replaces all off-limb values with 0
4. Converts the SunPy map to a numpy array
5. replaces NaN values with 0
6. Scales the data to [-1, 1]
7. Reshapes the array to channel first notation

The editors are listed in ``iti.data.editor``. Custom editor (e.g., preprocessing) can be implement by using ``iti.data,editor``.
Editor as base class and implementing the call function. Minor functionalities can be added by using ``iti.data,editor.LambdaEditor`` (e.g., ``LambdaEditor(lambda x: x * 2``).

.. code-block:: python

    from iti.data.dataset import BaseDataset
    from iti.data.editor import LoadMapEditor, NormalizeRadiusEditor, RemoveOffLimbEditor, MapToDataEditor, NanEditor, \
        NormalizeEditor, ReshapeEditor
    from astropy.visualization import ImageNormalize, LinearStretch

    class HMIDataset(BaseDataset):

        def __init__(self, path, resolution=2048, ext='.fits', **kwargs):
            norm = ImageNormalize(vmin=-1000, vmax=1000, stretch=LinearStretch(), clip=True)
            editors = [
                # open FITS
                LoadMapEditor(),
                # normalize rad
                NormalizeRadiusEditor(resolution),
                # truncate off limb (optional)
                RemoveOffLimbEditor(),
                # get data from SunPy map
                MapToDataEditor(),
                # replace NaN with 0
                NanEditor(),
                # normalize data to [-1, 1]
                NormalizeEditor(norm),
                # change data to channel first format
                ReshapeEditor((1, resolution, resolution))]
            super().__init__(path, editors=editors, ext=ext, **kwargs)

