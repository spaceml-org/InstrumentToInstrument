.. _iti_download:


===========
Downloaders
===========

All download routines are stored in the ``iti.download`` module. The following examples shows how to download the data using
the ``ITI`` downloader classes.

---
SDO
---

For SDO we use the ``iti.download.download_sdo.SDODownloader`` class:

.. autoclass:: iti.download.download_sdo.SDODownloader

The default settings for the AIA instrument is given by downloading the data in the 131, 171, 193, 211, 304, 335 Å channels
without the HMI magnetograms. However, we can include them by adding the ``6173`` Å in the wavelength initialization of the ``iti.download.download_sdo.SDODownloader``.
The ``iti.download.download_sdo.SDODownloader`` class contains a function to download the data for specific dates with the ``downloadDate`` function.

.. autofunction:: iti.download.download_sdo.SDODownloader.downloadDate

----
SOHO
----

For SOHO we use the ``iti.download.download_soho.SOHODownloader`` class:

.. autoclass:: iti.download.download_soho.SOHODownloader

The default settings for the SOHO downloader class is given by downloading the data from the ``EIT`` in the 171, 195, 284 and 304 Å channels as well as the ``MDI`` instrument
simultaneously. It contains functions to download the data for specific dates with the ``downloadDate`` function,
but also for the individual imagers ``EIT`` and ``MDI``.

.. autofunction:: iti.download.download_soho.SOHODownloader.downloadDate

.. autofunction:: iti.download.download_soho.SOHODownloader.downloadEIT

.. autofunction:: iti.download.download_soho.SOHODownloader.downloadMDI

------
STEREO
------

For STEREO we employ the ``iti.download.download_stereo.STEREODownloader`` class:

.. autoclass:: iti.download.download_stereo.STEREODownloader

Similar as for SDO and SOHO, the default settings for the STEREO downloader class is given by downloading the data from the ``EUVI`` instrument in the 171, 195, 284 and 304 Å channels .
It also contains a function to download the data for specific dates with the ``downloadDate`` function.

.. autofunction:: iti.download.download_stereo.STEREODownloader.downloadDate

------
PROBA2
------

For PROBA2 we use the ``iti.download.download_proba2.PROBA2Downloader`` class:

.. autoclass:: iti.download.download_proba2.PROBA2Downloader

The default settings for the PROBA2 downloader class is given by downloading the data from the ``SWAP`` instrument in the 174 Å channel.
With the ``downloadDate`` function, the data can be downloaded for specific dates.

.. autofunction:: iti.download.download_proba2.PROBA2Downloader.downloadDate

-------------
Solar Orbiter
-------------

For Solar Orbiter we use the ``iti.download.download_solo.SOLODownloader`` class:

.. autoclass:: iti.download.download_solo.SOLODownloader

For the Solar Orbiter downloader class, the default settings are given by downloading the data from the ``EUI`` instrument. This contains both the ``FSI`` and ``HRI`` instrument.
Note that for FSI, data is available in the 174 and 304 Å channels, while for HRI, data can be downloaded in the 174 Å and the Lyman-α channel.
The data can be downloaded for specific dates with the ``downloadDate`` function.

.. autofunction:: iti.download.download_solo.SOLODownloader.downloadDate

----------------------------
Kanzelhoehe Solar Observatory
----------------------------

The Kanzelhoehe Solar Observatory download routine is based on the two functions ``searchHalpha`` and ``downloadFile``. The ``searchHalpha`` function
searches for the available H-alpha images for a specific date and the ``downloadFile`` function downloads the data for the specified date.

.. autofunction:: iti.download.download_kso_synoptic.searchHalpha

.. autofunction:: iti.download.download_kso_synoptic.downloadFile

-----------------------------
Download data in the terminal
-----------------------------

For all download routines, that are based on *downloader classes* the data can be downloaded with a terminal command.
The timeframe can be specified with the ``start_date`` and ``end_date`` parameters. The data is stored in the ``download_dir`` directory which can
be specified individually.

To download the data from the terminal, you can run::

    python3 -m `iti.download.download_class --start_date 'start_date' --end_date 'end_date' --download_dir '/path/to/download_dir'

If an ``end_date`` is not specified, the current date will be used as default. The download routine will create a subdirectory for each channel in the download directory.

