************
Installation
************

The tool is build on python 3.6. To install the tool, you need to have python 3 installed on your system. If you haven't installed python yet, you
can download it from the following link: https://www.python.org/downloads/

=================
Tool Installation
=================

To install the ITI tool, you can use the following command::

    pip install iti

or using anaconda::

    conda install -c conda-forge iti

This will install the tool and all the dependencies required to run the tool.

Another option is to clone the repository from GitHub and install the tool using the following command::

    git clone https://github.com/spaceml-org/InstrumentToInstrument.git

============
Requirements
============

The ITI tool is build on python libraries which are necessary to download first to run the tool. It requires the following packages to be installed on your system:
::

    torch>=1.8
    sunpy>=2.0
    scikit-image
    scikit-learnt
    tqdm
    numpy
    matplotlib
    astropy
    aiapy
    drms
    pandas
    gsutil

These packages can be installed using the following pip command::

        pip install torch>=1.8 sunpy>=2.0 scikit-image scikit-learn tqdm numpy matplotlib astropy aiapy drms pandas gsutil
