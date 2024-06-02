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

By appyling the translation from SOHO to SDO, the user can obtain SOHO observations in the SDO domain. The translation is
carried out by the ``iti.translate.SOHOToSDO`` class.

.. autoclass:: iti.translate.SOHOToSDO

-------------
STEREO to SDO
-------------

The translation from STEREO to SDO is performed by the ``iti.translate.STEREOToSDO`` class. Here, we translate between the EUVI and AIA instruments.

.. autoclass:: iti.translate.STEREOToSDO

We provide a second translation class for the STEREO to SDO translation, by translating between the magnetogram observations of the two instruments MDI and HMI.

.. autoclass:: iti.translate.STEREOToSDOMagnetogram

-------------
HMI to Hinode
-------------

In order to super resolve SDO/HMI observations we can translate them to the Hinode/SOT domain. This is performed by the ``iti.translate.HMIToHinode`` class.

.. autoclass:: iti.translate.HMIToHinode

-------------
PROBA2 to SDO
-------------

The translation from PROBA2 to SDO is performed by the ``iti.translate.PROBA2ToSDO`` class. This provides enhanced SWAP observations in the AIA domain.

.. autoclass:: iti.translate.PROBA2ToSDO

--------------------
Solar Orbiter to SDO
--------------------

Translating Solar Orbiter/FSI observations to the SDO/AIA domain provides instrument intercalibration, which can be used for multi-viewpoint
investigations. The translation is performed by the ``iti.translate.FSIToAIA`` class.

.. autoclass:: iti.translate.SolarOrbiterToSDO

--------------------
SDO to Solar Orbiter
--------------------

With the Solar Orbiter/HRI instrument, we can translate SDO/AIA observations to the Solar Orbiter/HRI domain. This enables full-sun super-resolved observations.
This is performed by the ``iti.translate.SDOToSolarOrbiter`` class.

.. autoclass:: iti.translate.SDOToSolarOrbiter