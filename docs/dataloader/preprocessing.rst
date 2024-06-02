.. _iti_preprocessing:

*************
Preprocessing
*************

The second module after the data :ref:`download module <iti_download_index>` is the preprocessing module.
This module is responsible for the preprocessing of the data to be used for neural network applications.

The preprocessing steps are built on *Editor* classes which can be stacked together to obtain **ML-ready datasets**.

-------
Editors
-------

All preprocessing editors are stored in `iti.data.editor`. To give you and idea of the available editors, here are the most common ones:

Before we start with the preprocessing, let's first load the data as a 'SunPy' map.

.. autoclass:: iti.data.editor.LoadMapEditor

After loading the data, we can start with the preprocessing. In order to scale all observations to the same size, we use the ``iti.data.editor.NormalizeRadiusEditor``. This
crops the observations 1.1 solar radii and scales them to a fixed resolution.

.. autoclass:: iti.data.editor.NormalizeRadiusEditor

The next step is to transform the SunPy map to a numpy array. This is done by the ``iti.data.editor.MapToDataEditor``.

.. autoclass:: iti.data.editor.MapToDataEditor

Depending on the instruments and the activation function of the neural network we need to normalize the data. This is done by the ``iti.data.editor.NormalizeDataEditor``.

.. autoclass:: iti.data.editor.NormalizeDataEditor

The normalization depends on the instruments used and can be adjusted accordingly.

The last step is to reshape the data according to the neural network architecture. The ``iti.data.editor.ReshapeDataEditor`` is used for this.

.. autoclass:: iti.data.editor.ReshapeDataEditor


---------------------------------
Instrument specific preprocessing
---------------------------------

In some cases, we need to preprocess the data according to the instrument used. For example, the AIA instrument needs to be corrected for instrument degradation.
This is done by the ``iti.data.editor.AIAPrepEditor``.

.. autoclass:: iti.data.editor.AIAPrepEditor

For more information on the individual editors available, please look up the ``iti.data.editor`` module on `GitHub <https://github.com/spaceml-org/InstrumentToInstrument/blob/master/iti/data/editor.py>`__.