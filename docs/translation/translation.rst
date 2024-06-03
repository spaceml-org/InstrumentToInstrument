.. _iti_translation:

===================
Translation classes
===================

The heart of ITI is the translation class performing the domain translations after training. This enables the user to obtain:

    - Image enhancement,
    - Instrument intercalibration and
    - super resolution observations.

The translation process is based on the core class ``iti.translate.InstrumentToInstrument``.

.. autoclass:: iti.translate.InstrumentToInstrument


The indivdual case studies make use use of the core class to perform the translation.

-----------
SOHO to SDO
-----------

By appyling the translation from SOHO to SDO, the user can obtain observations from SOHO/EIT in the SDO/AIA domain. This translation includes
image enhancement and instrument intercalibration, providing a unified data set dating back to 1996. In addition to the EUV channels, the Michelson Doppler Imager (MDI)
is translated to SDO/HMI magnetograms. The translation is carried out by the ``iti.translate.SOHOToSDO`` class.

.. autoclass:: iti.translate.SOHOToSDO

-------------
STEREO to SDO
-------------

Similar as for the SOHO to SDO translation, STEREO to SDO provides image enhancement and instrument intercalibration between the two instruments
simultaneously. The translation from STEREO to SDO is performed by the ``iti.translate.STEREOToSDO`` class. Here, we translate between the EUVI and AIA instruments.

.. autoclass:: iti.translate.STEREOToSDO

The STEREO mission unfortunately does not provide full-disk magnetograms. However, ITI can be used to estimate the missing information based on proxy data.
ITI can be used to complement the STEREO observations, by generating LOS magnetograms based on STEREO EUV filtergrams. This is performed by the ``iti.translate.STEREOToSDOMagnetogram`` class.

.. autoclass:: iti.translate.STEREOToSDOMagnetogram

-------------
HMI to Hinode
-------------

In order to super resolve SDO/HMI observations we can translate them to the Hinode/SOT domain. Here, we resize Hinode observations
to 0.15 arcsec pixels and use ITI to super resolve HMI observations by a factor of 4. This is performed by the ``iti.translate.HMIToHinode`` class.

.. autoclass:: iti.translate.HMIToHinode

-------------
PROBA2 to SDO
-------------

Complementary to the *SOHO to SDO* and *STEREO to SDO* translation, the PROBA2/SWAP to SDO/AIA is a similar application. For this use case we translate only a single
channel in the 174 Å band from SWAP to the 171 Å channel of AIA. The translation again includes image enhancement and instrument intercalibration.
The translation from PROBA2 to SDO is performed by the ``iti.translate.PROBA2ToSDO`` class.

.. autoclass:: iti.translate.PROBA2ToSDO

--------------------
Solar Orbiter to SDO
--------------------

Translating Solar Orbiter/FSI observations to the SDO/AIA domain provides instrument intercalibration. Due to the varying orbit of Solar Orbiter
these dataproducts can be used for multi-viewpoint investigations. The translation is performed by the ``iti.translate.FSIToAIA`` class.

.. autoclass:: iti.translate.SolarOrbiterToSDO

--------------------
SDO to Solar Orbiter
--------------------

With the Solar Orbiter/HRI instrument, we can translate SDO/AIA observations to the Solar Orbiter/HRI domain. With the use of unpaired image translation we do
not require a spatial or temporal overlap between the data sets, moreover the model training is performed with small patches of the full images.
This enables the use of instruments that can observe only a fraction of the Sun for the enhancement of full-disk observations. For the translation between SDO/AIA
and Solar Orbiter/HRI this allows for super-resolved full-sun AIA observations. This is performed by the ``iti.translate.SDOToSolarOrbiter`` class.

.. autoclass:: iti.translate.SDOToSolarOrbiter