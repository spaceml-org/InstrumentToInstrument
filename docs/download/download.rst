.. _iti_download:


========================
Simple download tutorial
========================

All download routines are stored in the ``iti.download`` module. The following example shows how to download the data for the Solar Dynamics Observatory (SDO)
Atmospheric Imaging Assembly (AIA) instrument from the terminal. Here we make use of the ``SDODownloader``. The default settings for the AIA instrument is given by downloading the data in the 131, 171, 193, 211, 304, 335 Å channels
including HMI magnetograms. The timeframe can be specified with the ``start_date`` and ``end_date`` parameters. The data is stored in the ``download_dir`` directory which can
be specified individually.

To download the data for the AIA instrument, you can run::

    python3 -m iti.download.download_sdo --start_date 'start_date' --end_date 'end_date' --download_dir '/path/to/download_dir'

If an ``end_date`` is not specified, the current date will be used as default. The download routine will create a subdirectory for each channel in the download directory.

