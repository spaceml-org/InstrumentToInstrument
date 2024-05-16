.. _iti_training_index:

********
Training
********

The trainer class implements the pytorch lightning training function, that requires the workspace directory and the low- and high-quality dataset. The paths to
the datasets are specified in the *config file*.
An optional validation data set can be specified to verify the model results (plots and parallel validation). ITI is build on pytorch lightning and uses the weights and biases logging system.
This simplifies the training process and allows to monitor the training progress in real-time.
The trainer class is initialized with the *config file* and the workspace directory.