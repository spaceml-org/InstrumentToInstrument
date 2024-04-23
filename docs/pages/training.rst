********
Training
********

The trainer class implements the pytorch lightning training function, that requires the workspace directory and the low- and high-quality dataset. The paths to
the datasets are specified in the *config file*.
An optional validation data set can be specified to verify the model results (plots and parallel validation). ITI is build on pytorch lightning and uses the weights and biases logging system.
This simplifies the training process and allows to monitor the training progress in real-time.
The trainer class is initialized with the *config file* and the workspace directory.

===============================
Training example configuration
===============================

The training scripts for the individual case studies are stored in the ``iti.train`` directory.
In the example we intercalibrate Solar Orbiter Full Sun Imager (FSI) observations to SDO (AIA) observations. For both instruments we use 2 channels (``input_dim_a/b=2``).
We do not increase the resolution, corresponding to a ``upsampling=0``. We expect mostly instrumental characteristics that cause degradations and set the diversity
factor to 0 (``lambda_diversity=0``). For the discriminator we provide three settings::

        - discriminator_mode=SINGLE: 'use a single discriminator across all channels.'
        - discriminator_mode=CHANNELS: 'use a discriminator per channel and one for the combined channels.'
        - discriminator_mode=SINGLE_PER_CHANNEL: 'use a single discriminator for each channel.'

For the training we specify the SDO and Solar Orbiter datasets, where we use a fixed resolution of 1024 pix for
Solar Orbiter and consequently for SDO. The training is performed with images patches, that we sample from the full-disk observations.
According to our GPU memory we select a patch size of *128 pixels* for Solar Orbiter and SDO. We apply a temporal separation of our dataset, where we use
the months 1-10 for training and 11-12 for validation.
Images are automatically saved during training, but note that they will only provide information about the quality of the translation when the
InstanceNormalization weights are fixed (after *100 000 iterations*). The use of learned parameters of the InstanceNormalization is required for the training with image patches.
We additionally store the ``.fits`` files as a ``.npy`` file in the ``converted_path`` directory. This allows to load the data faster and consequently accelerates the training process.
To initialize the training we use ``.yaml`` configuration files, that are stored in the ``iti/train/configs`` directory. An example is shown here:

.. code-block:: yaml

    base_dir: 'path to workspace directory'
    data:
        B_path: 'path to SDO data'
        converted_B_path: 'path to converted SDO data'
        A_path: 'path to FSI data'
        converted_A_path: 'path to converted FSI data'
        num_workers: '6'
        iterations_per_epoch: '1000'
    model:
        input_dim_a: '2'
        input_dim_b: '2'
        upsampling: '0'
        discriminator_mode: 'CHANNELS'
        lambda_diversity: '0'
        norm: 'in_rs_aff'
        use_batch_statistic: 'False'
    logging:
        wandb_entity: 'wandb username'
        wandb_project: 'wandb project name'
        wandb_name: 'wandb run name'
        wandb_id: 'null'
    training:
        epochs: '220000'

The following command can then be used to run the training::

    python3 -m iti.train.FSI_to_SDO --config 'path to config file'.

Running the training script will create a new directory in the workspace directory where the training results will be stored. The progress
of the training is monitored in real time using the weights and biases logging system. For more information about weights and biases, see: https://wandb.ai/site.