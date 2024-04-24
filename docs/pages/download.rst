*************
Data download
*************

Google Colab offers free GPU resources, which can be used for a fast translation of data. Note that you have to upload and download your data to the Notebook.
For all case studies we provide a downloader that can be modified to translate custom observations.
Data from SOHO and STEREO requires preprocessing routines, that are only available in SSW IDL. For larger amounts of data it is more
efficient to translate the files on a local workstation (preferable with a GPU).

========================
Simple download tutorial
========================

All download routines are stored in the ``iti.download`` module. The following example shows how to download the data for the Solar Dynamics Observatory (SDO)
Atmospheric Imaging Assembly (AIA) instrument. The default settings for the AIA instrument is given by downloading the data in the 131, 171, 193, 211, 304, 335 Å channels
including HMI magnetograms. The timeframe can be specified with the ``start_date`` and ``end_date`` parameters. The data is stored in the ``download_dir`` directory which can
be specified individually.

To download the data for the AIA instrument, you can run::

    python3 -m iti.download.download_sdo --start_date `start_date` --end_date `end_date` --download_dir `/path/to/download_dir`

If an ``end_date`` is not specified, the current date will be used as default. The download routine will create a subdirectory for each channel in the download directory.

================
Download Testset
================

We also have some publicly available test data which will allow users to play around with a subset of the datasets available without downloading the entire database.
This can be useful for testing the tool as well as exploration.
To download the data to your local machine, you can run::

    gsutil cp -r gs://iti-dataset/ [local_path]

in your terminal. This will download the test dataset to the selected path of your local machine. It consists of data from::

    - Solar Dynamics Observatory (SDO) Atmospheric Imaging Assembly (AIA) instrument
    - PROBA2 Sun Watcher using Active Pixel System detector and Image Processing (SWAP) instrument
    - Solar Orbiter (SolO) EUI instrument including the Full Sun Imager (FSI) and the High Resolution Imager (HRI)
