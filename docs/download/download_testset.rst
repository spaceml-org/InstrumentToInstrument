.. _iti_testset:

================
Download Testset
================

We also have some publicly available test data which will allow users to play around with a subset of the datasets available without downloading the entire database.
This can be useful for testing the tool as well as exploration.
To download the data to your local machine, you can run::

    gsutil cp -r gs://iti-dataset/ '[local_path]'

in your terminal. This will download the test dataset to the selected path of your local machine. It consists of data from:

    - Solar Dynamics Observatory (SDO) Atmospheric Imaging Assembly (AIA) instrument
    - PROBA2 Sun Watcher using Active Pixel System detector and Image Processing (SWAP) instrument
    - Solar Orbiter (SolO) EUI instrument including the Full Sun Imager (FSI) and the High Resolution Imager (HRI)