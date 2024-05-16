.. Instrument-To-Instrument documentation master file, created by
   sphinx-quickstart on Fri Apr 2 11:20:37 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

=============================================================
Welcome to Instrument-To-Instrument (ITI) tool documentation!
=============================================================

``ITI`` is an AI tool capable of translating between different image domains. It is based on a Generative Adversarial Network (GAN) with unpaired image-to-image translation. This allows for:
   - Image enhancement
   - Instrument intercalibration
   - Super-resolution
for many science domains. The tool has been applied to heliophysics and earth science use cases.

The constant improvement of astronomical instrumentation provides the foundation for scientific discoveries. In general,
these improvements have only implications forward in time, while previous observations do not profit from this trend. In
solar physics, the study of long-term evolution typically exceeds the lifetime of single instruments and data driven approaches
are strongly limited in terms of coherent long-term data samples.
We demonstrate that the available data sets can directly profit from the most recent instrumental improvements and provide
a so far unused resource to foster novel research and accelerate data driven studies.
Here we provide a general method that translates between image domains of different instruments (Instrument-to-Instrument translation; ITI),
in order to inter-calibrate data sets, enhance physically relevant features which are otherwise beyond the diffraction
limit of the telescope, mitigate atmospheric degradation effects and can estimate observables that are not covered by the instrument.
We demonstrate that our method can provide unified long-term data sets at the highest quality, by applying it to
five different applications of ground- and space-based solar observations.
We obtain:
    - a homogeneous data series of 24 years of space-based observations of the solar corona
    - solar full-disk observations with unprecedented spatial resolution
    - real-time mitigation of atmospheric degradations in ground-based observations
    - a uniform series of ground-based H-alpha observations starting from 1973, that unifies solar observations recorded on photographic film and CCD
    - magnetic field estimates from the solar far-side based on multi-band EUV imagery
    - instrument intercalibration between space-based telescopes
    - super-resolution solar observations.

The direct comparison to simultaneous high-quality observations shows that our method produces images that are perceptually similar and match the reference image distribution.

.. grid:: 1 2 3 2
    :gutter: 2

    .. grid-item-card:: Installation
        :link: iti_installation_index
        :link-type: ref
        :text-align: center

      Information on how to install the ITI tool with its requirements.

    .. grid-item-card:: Download
        :link: iti_download_index
        :link-type: ref
        :text-align: center

      Data download.


   .. grid-item-card:: Dataloader
        :link: iti_dataloader_index
        :link-type: ref
        :text-align: center

      Dataloader.

   .. grid-item-card:: Training
        :link: iti_training_index
        :link-type: ref
        :text-align: center

      Training.

    .. grid-item-card:: Translation
          :link: iti_translation_index
          :link-type: ref
          :text-align: center

      Translation.

=====
Links
=====

* ITI paper: https://doi.org/10.48550/arXiv.2401.08057
* :ref:`genindex`
* :ref:`search`
* Install python: https://www.python.org/downloads/
* Translate your own data: https://colab.research.google.com/github/RobertJaro/InstrumentToInstrument/blob/master/examples/ITI_translation.ipynb
* GPU support: https://pytorch.org/get-started/locally/
* Weights and Biases: https://wandb.ai/site


.. toctree::
    :maxdepth: 1
    :hidden:

    /installation/index
    /download/index
    /generated/gallery/index
    /dataloader/index
    /training/index
    /translation/index