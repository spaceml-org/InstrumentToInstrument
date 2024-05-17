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

.. grid:: 1 1 2 2
   :gutter: 1

      .. grid-item-card:: Installation
         :link: iti_installation_index
         :link-type: ref
         :text-align: center

         :material-outlined:`settings;8em;sd-text-secondary`

         Information on how to install the ITI tool with its requirements.

      .. grid-item-card:: Download
         :link: iti_download_index
         :link-type: ref
         :text-align: center

         :material-outlined:`cloud_download;8em;sd-text-secondary`

         Data download.


      .. grid-item-card:: Dataloader
         :link: iti_dataloader_index
         :link-type: ref
         :text-align: center

         :material-outlined:`data_usage;8em;sd-text-secondary`

         Dataloader.

      .. grid-item-card:: Training
         :link: iti_training_index
         :link-type: ref
         :text-align: center

         :material-outlined:`school;8em;sd-text-secondary`

         Training.

      .. grid-item-card:: Translation
         :link: iti_translation_index
         :link-type: ref
         :text-align: center

         :material-outlined:`translate;8em;sd-text-secondary`

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
   /dataloader/index
   /training/index
   /generated/gallery/index