*****
Usage
*****

Google Colab offers free GPU resources, which can be used for a fast translation of data. Note that you have to upload and download your data to the Notebook.
For all case studies we provide a downloader that can be modified to translate custom observations.
Data from SOHO and STEREO requires preprocessing routines, that are only available in SSW IDL. For larger amounts of data it is more
efficient to translate the files on a local workstation (preferable with a GPU).

====================
Downloading the data
====================

All download routines are stored in the ``ìti.download`` module. The following example shows how to download the data for the Solar Dynamics Observatory (SDO)
Atmospheric Imaging Assembly (AIA) instrument. The default settings for the AIA instrument is given by downloading the data in the 131, 171, 193, 211, 304, 335 Å channels
including HMI magnetograms. The timeframe can be specified with the ``start_date`` and ``end_date`` parameters. The data is stored in the ``download_dir`` directory which can
be specified individually.

To download the data for the AIA instrument, you can run::

    python3 -m iti.download.download_sdo --start_date ``start_date`` --end_date ``end_date`` --download_dir ``/path/to/download_dir``

If an 'end_date' is not specified, the current date will be used as default. The download routine will create a subdirectory for each channel in the download directory.




