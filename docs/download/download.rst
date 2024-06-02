.. _iti_download:


===========
Downloaders
===========

All download routines are stored in the ``iti.download`` module. The following examples shows how to download the data using
the `ÌTI``downloader classes.

---
SDO
---

For SDO we use the ``iti.download.download_sdo.SDODownloader`` class:

.. autoclass:: iti.download.download_sdo.SDODownloader

The default settings for the AIA instrument is given by downloading the data in the 131, 171, 193, 211, 304, 335 Å channels
including HMI magnetograms. The ``iti.download.download_sdo.SDODownloader`` class contains a function to download the data for specific dates with the ``downloadDate`` function.

.. autofunction:: iti.download.download_sdo.SDODownloader.downloadDate










The timeframe can be specified with the ``start_date`` and ``end_date`` parameters. The data is stored in the ``download_dir`` directory which can
be specified individually.

To download the data for the AIA instrument, you can run::

    python3 -m iti.download.download_sdo --start_date 'start_date' --end_date 'end_date' --download_dir '/path/to/download_dir'

If an ``end_date`` is not specified, the current date will be used as default. The download routine will create a subdirectory for each channel in the download directory.

