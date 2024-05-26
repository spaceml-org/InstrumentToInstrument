"""
=======================
Example training script
=======================

This script demonstrates how to train a model using the ITI framework. The example shows the translation between PROBA2/SWAP and SDO/AIA.
"""


#import os
#import collections.abc
#import shutil

#hyper needs the four following aliases to be done manually.
#collections.Iterable = collections.abc.Iterable
#collections.Mapping = collections.abc.Mapping
#collections.MutableSet = collections.abc.MutableSet
#collections.MutableMapping = collections.abc.MutableMapping
#Now import hyper
#import torch
#import yaml
#from lightning import Trainer
#from lightning.pytorch.callbacks import ModelCheckpoint
#from lightning.pytorch.loggers import WandbLogger
#from lightning.pytorch.strategies import DataParallelStrategy
#from sunpy.visualization.colormaps import cm

#from iti.callback import SaveCallback, PlotBAB, PlotABA
#from iti.data.dataset import AIADataset, StorageDataset, SWAPDataset, ITIDataModule
#from iti.data.editor import RandomPatchEditor, BrightestPixelPatchEditor
#from iti.iti import ITIModule

########################################################################################
# Open the config file
#with open('config/proba2_to_sdo_colab.yaml', "r") as stream:
#    try:
#        config = yaml.safe_load(stream)
#    except yaml.YAMLError as exc:
#        print(exc)

#base_dir = config['base_dir']
#os.makedirs(base_dir, exist_ok=True)

########################################################################################
# Initialize the paths from the config file
#data_config = config['data']
#swap_path = data_config['A_path']
#swap_converted_path = data_config['converted_A_path']
#os.makedirs(swap_converted_path, exist_ok=True)
#sdo_path = data_config['B_path']
#sdo_converted_path = data_config['converted_B_path']
#os.makedirs(sdo_converted_path, exist_ok=True)

########################################################################################
# Define the training and validation months
#test_months = [11, 12]
#train_months = list(range(2, 10))

########################################################################################
# Initialize the datasets
#
# To accelerate the training procedure, the data is stored as `.npy` files in the `converted path` directories.
#
# The training is performed on patches of size `(128, 128)` for the SWAP data and `(256, 256)` for the AIA data. We use the `RandomPatchEditor` to extract random patches from the full images.

#sdo_dataset = AIADataset(sdo_path, wavelength=171, months=train_months)
#sdo_dataset = StorageDataset(sdo_dataset,
#                             sdo_converted_path,
#                             ext_editors=[RandomPatchEditor((256, 256))])

#swap_dataset = SWAPDataset(swap_path, months=train_months)
#swap_dataset = StorageDataset(swap_dataset, swap_converted_path,
#                                ext_editors=[RandomPatchEditor((128, 128))])

#sdo_valid = StorageDataset(AIADataset(sdo_path, wavelength=171, months=test_months, limit=100),
#                           sdo_converted_path, ext_editors=[RandomPatchEditor((256, 256))])
#swap_valid = StorageDataset(SWAPDataset(swap_path, months=test_months, limit=100),
#                              swap_converted_path, ext_editors=[RandomPatchEditor((128, 128))])


########################################################################################
# Initialize the data module

#data_module = ITIDataModule(swap_dataset, sdo_dataset, swap_valid, sdo_valid, **config['data'])

########################################################################################
# Define the plot settings for the callbacks

#plot_settings_A = [
#    {"cmap": cm.sdoaia171, "title": "SWAP 174", 'vmin': -1, 'vmax': 1},
#]
#plot_settings_B = [
#    {"cmap": cm.sdoaia171, "title": "AIA 171", 'vmin': -1, 'vmax': 1},
#]

########################################################################################
# Setup the logging for weights and biases (wandb)
#logging_config = config['logging']
#wandb_id = logging_config['wandb_id'] if 'wandb_id' in logging_config else None
#log_model = logging_config['wandb_log_model'] if 'wandb_log_model' in logging_config else False
#wandb_logger = WandbLogger(project=logging_config['wandb_project'], name=logging_config['wandb_name'], offline=False,
#                           entity=logging_config['wandb_entity'], id=wandb_id, dir=config['base_dir'], log_model=log_model)
#wandb_logger.experiment.config.update(config, allow_val_change=True)


########################################################################################
# Start training

#module = ITIModule(**config['model'])

########################################################################################
# Setup save callbacks
#checkpoint_callback = ModelCheckpoint(dirpath=base_dir, save_last=True, every_n_epochs=1, save_weights_only=False)
#save_callback = SaveCallback(base_dir)

########################################################################################
# setup plot callbacks
#
# This will plot the predictions of the model on the validation data every epoch.

#plot_callbacks = []
#plot_callbacks += [PlotBAB(sdo_valid.sample(4), module, plot_settings_A=plot_settings_A, plot_settings_B=plot_settings_B)]
#plot_callbacks += [PlotABA(swap_valid.sample(4), module, plot_settings_A=plot_settings_A, plot_settings_B=plot_settings_B)]

########################################################################################
# Start the training

#n_gpus = torch.cuda.device_count()
#trainer = Trainer(max_epochs=int(config['training']['epochs']),
#                  logger=wandb_logger,
#                  devices=n_gpus if n_gpus > 0 else None,
#                  accelerator="gpu" if n_gpus >= 1 else None,
#                  strategy='dp' if n_gpus > 1 else None,  # ddp breaks memory and wandb
#                  num_sanity_val_steps=0,
#                  callbacks=[checkpoint_callback, save_callback, *plot_callbacks],)

#trainer.fit(module, data_module, ckpt_path='last')