import argparse
import os
import ast
import collections.abc
import shutil
import autoroot

import sys
import json 
#hyper needs the four following aliases to be done manually.
collections.Iterable = collections.abc.Iterable
collections.Mapping = collections.abc.Mapping
collections.MutableSet = collections.abc.MutableSet
collections.MutableMapping = collections.abc.MutableMapping
#Now import hyper
import torch
import yaml
import wandb
from lightning import Trainer
from lightning.pytorch.callbacks import ModelCheckpoint
from lightning.pytorch.loggers import WandbLogger
from lightning.pytorch import seed_everything

import autoroot
from itipy.data.geo_datasets import GeoDataset
from itipy.data.dataset import StorageDataset 
from itipy.data.geo_editor import BandSelectionEditor, NanMaskEditor, CoordNormEditor, NanDictEditor, RadUnitEditor, ToTensorEditor, StackDictEditor, MeanStdNormEditor, MinMaxNormEditor, Rotate180Editor
from itipy.data.geo_utils import get_split, get_list_filenames, normalize, calculate_norm_from_metrics

import warnings
warnings.filterwarnings('ignore')

from itipy.callback import SaveCallback, PlotBAB, PlotABA
from itipy.data.data_module import ITIDataModule
from itipy.iti import ITIModule

from datetime import datetime
from loguru import logger
import xarray as xr

parser = argparse.ArgumentParser(description='Train MSG to GOES translations')
parser.add_argument('--config', 
                    default='/home/anna.jungbluth/InstrumentToInstrument/config/msg_to_goes.yaml',
                    type=str, 
                    help='path to the config file.')

args = parser.parse_args()

with open(args.config, "r") as stream:
    try:
        config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

# Extract and set model and data seeds
seed = config.seed if "seed" in config else 42
logger.info(f"training with seed {seed}")
seed_everything(seed, workers=True)

# Create timestamped directory within base_dir where normalisation, and checkpoints are saved
base_dir = config['base_dir']
time_str = datetime.now().strftime("%Y%m%d-%H%M")
save_dir = os.path.join(base_dir, time_str)
os.makedirs(save_dir, exist_ok=True)

# Initialize Dataset
data_config = config['data']
msg_path = data_config['A_path']
goes_path = data_config['B_path']
msg_patch_size = ast.literal_eval(data_config['A_patch_size']) if data_config['A_patch_size'] is not None else None
goes_patch_size = ast.literal_eval(data_config['B_patch_size']) if data_config['B_patch_size'] is not None else None

splits_dict = { 
    "train": {
        "years": [2020], 
        "months": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 
        "days": list(range(1, 25))
        },
    "val": {
        "years": [2020],
        "months": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 
        "days": list(range(25, 32))
        },
}

norm_config = config['normalization']
if 'A_norm_dir' and 'B_norm_dir' in norm_config:
    logger.info(f"Loading normalization from: {norm_config['A_norm_dir']} and {norm_config['B_norm_dir']}")
    msg_norm = calculate_norm_from_metrics(norm_config['A_norm_dir'], split_dict=splits_dict['train'])
    goes_norm = calculate_norm_from_metrics(norm_config['B_norm_dir'], split_dict=splits_dict['train'])
else:
    raise ValueError("No normalization found. Please specify paths.")

# Save normalisations to save directory
norm_dir = os.path.join(save_dir, 'normalization')
os.makedirs(norm_dir, exist_ok=True)
# Convert and write JSON object to file
with open(os.path.join(norm_dir, 'goes_norm.json'), "w") as outfile: 
    json.dump(goes_norm, outfile)
with open(os.path.join(norm_dir, 'msg_norm.json'), "w") as outfile:
    json.dump(msg_norm, outfile)

logger.info(f"Saved normalization to {norm_dir}...")

msg_bands = config['data']['A_bands']
msg_editors = [
    BandSelectionEditor(target_bands=msg_bands),
    NanDictEditor(key="data", fill_value=0), # Replaces NaNs in data
    Rotate180Editor(key="data"), # Rotate 180 degrees to align north to top of image
    MinMaxNormEditor(norm_dict=msg_norm, key="data"),
    StackDictEditor(allowed_keys = ['data']),
    ToTensorEditor(),
    # RandomPatchEditor(patch_shape=(256, 256)), # NOTE: This is now already taken care of in the GeoDataset
]

goes_bands = config['data']['B_bands']
goes_editors = [
    BandSelectionEditor(target_bands=goes_bands),
    NanDictEditor(key="data", fill_value=0), # Replaces NaNs in data
    MinMaxNormEditor(norm_dict=goes_norm, key="data"),
    StackDictEditor(allowed_keys = ['data']),
    ToTensorEditor(),
    # RandomPatchEditor(patch_shape=(256, 256)), # NOTE: This is now already taken care of in the GeoDataset
]

logger.info(f"Instantiating datasets.")

msg_dataset = GeoDataset(
    data_dir=msg_path,
    editors=msg_editors,
    splits_dict=splits_dict['train'],
    load_coords=False,
    load_cloudmask=False,
    patch_size=msg_patch_size,
)

msg_valid = GeoDataset(
    data_dir=msg_path,
    editors=msg_editors,
    splits_dict=splits_dict['val'],
    load_coords=False,
    load_cloudmask=False,
    patch_size=msg_patch_size,
)

goes_dataset = GeoDataset(
    data_dir=goes_path,
    editors=goes_editors,
    splits_dict=splits_dict['train'],
    load_coords=False,
    load_cloudmask=False,
    patch_size=goes_patch_size,
)

goes_valid = GeoDataset(
    data_dir=goes_path,
    editors=goes_editors,
    splits_dict=splits_dict['val'],
    load_coords=False,
    load_cloudmask=False,
    patch_size=goes_patch_size,
)

data_module = ITIDataModule(msg_dataset, goes_dataset, msg_valid, goes_valid, **config['data'])

# Setup logging
logger.info(f"Setting up WandB logging...")

logging_config = config['logging']
wandb_id = logging_config['wandb_id'] if 'wandb_id' in logging_config else None
log_model = logging_config['wandb_log_model'] if 'wandb_log_model' in logging_config else False

# Initialize wandb
run = wandb.init(project=logging_config['wandb_project'], 
                 name=logging_config['wandb_name'], 
                 entity=logging_config['wandb_entity'], 
                 id=wandb_id, 
                 dir=save_dir)
wandb_logger = WandbLogger(project=logging_config['wandb_project'], name=logging_config['wandb_name'], offline=False,
                           entity=logging_config['wandb_entity'], id=wandb_id, dir=save_dir, log_model=log_model)


# log config to wandb
logger.debug(f"Config: {config}")

# Start training
logger.info(f"Initializing training steps...")

module = ITIModule(**config['model'])

# setup save callbacks
logger.info(f"Initializing callbacks...")
checkpoint_dir = os.path.join(save_dir, 'checkpoints')
os.makedirs(checkpoint_dir, exist_ok=True)
checkpoint_callback = ModelCheckpoint(dirpath=checkpoint_dir, save_last=True, every_n_epochs=1, save_weights_only=False)
save_callback = SaveCallback(checkpoint_dir)

# setup plot callbacks
plot_callbacks = []

plot_settings_A = []
plot_settings_B = []

for wvl in config['data']['A_bands']:
    plot_settings_A.append({"cmap": 'Blues', "title": f"MSG {wvl}"})
for wvl in config['data']['B_bands']:
    plot_settings_B.append({"cmap": 'Greys', "title": f"GOES {wvl}"})

plot_callbacks += [PlotBAB(goes_valid.sample(4), module, plot_settings_A=plot_settings_A, plot_settings_B=plot_settings_B)]
plot_callbacks += [PlotABA(msg_valid.sample(4), module, plot_settings_A=plot_settings_A, plot_settings_B=plot_settings_B)]

n_gpus = torch.cuda.device_count()
n_cpus = os.cpu_count()

logger.info(f"Initializing Trainer...")
trainer = Trainer(
    max_epochs=int(config['training']['epochs']),
    fast_dev_run=False,
    logger=wandb_logger,
    devices=n_gpus if n_gpus > 0 else n_cpus,
    accelerator="gpu" if n_gpus >= 1 else "cpu",
    strategy='dp' if n_gpus > 1 else "auto",  # ddp breaks memory and wandb
    num_sanity_val_steps=0,
    callbacks=[checkpoint_callback, save_callback, *plot_callbacks],
    limit_train_batches=config['training']['limit_train_batches'],
    limit_val_batches=config['training']['limit_val_batches'],
)

logger.info(f"Starting training...")
trainer.fit(module, data_module, ckpt_path='last')
logger.info(f"Done...!")