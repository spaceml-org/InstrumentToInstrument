import argparse
import ast
import collections.abc
import os

import autoroot  # Needed for import from src

# hyper needs the four following aliases to be done manually.
collections.Iterable = collections.abc.Iterable
collections.Mapping = collections.abc.Mapping
collections.MutableSet = collections.abc.MutableSet
collections.MutableMapping = collections.abc.MutableMapping
import warnings

# Now import hyper
import torch
import wandb
import yaml
from lightning import Trainer
from lightning.pytorch import seed_everything
from lightning.pytorch.callbacks import ModelCheckpoint
from lightning.pytorch.loggers import WandbLogger

from itipy.data.dataset import StorageDataset
from itipy.data.editor import RandomPatchEditor
from itipy.data.geo_constants import SPLITS_DICT as splits_dict
from itipy.data.geo_datasets import GeoDataset
from itipy.data.geo_editor import (
    MinMaxNormEditor,
    NanDictEditor,
    WavelengthSelectionEditor,
)

warnings.filterwarnings("ignore")

from datetime import datetime

from loguru import logger

from itipy.callback import PlotABA, PlotBAB, SaveCallback
from itipy.data.data_module import ITIDataModule
from itipy.iti import ITIModule

parser = argparse.ArgumentParser(description="Train MSG to GOES translations")
parser.add_argument(
    "--config",
    default="/home/anna.jungbluth/InstrumentToInstrument/config/msg_to_goes.yaml",
    type=str,
    help="path to the config file.",
)

args = parser.parse_args()

with open(args.config) as stream:
    config = yaml.safe_load(stream)

# Extract and set model and data seeds
seed = config.seed if "seed" in config else 42
logger.info(f"training with seed {seed}")
seed_everything(seed, workers=True)

# Create timestamped directory within base_dir where checkpoints are saved
base_dir = config["base_dir"]
time_str = datetime.now().strftime("%Y%m%d-%H%M")
save_dir = os.path.join(base_dir, time_str)
os.makedirs(save_dir, exist_ok=True)

# Initialize Dataset
data_config = config["data"]
msg_path = data_config["A_path"]
goes_path = data_config["B_path"]
msg_patch_size = (
    ast.literal_eval(data_config["A_patch_size"])
    if data_config["A_patch_size"] is not None
    else None
)
goes_patch_size = (
    ast.literal_eval(data_config["B_patch_size"])
    if data_config["B_patch_size"] is not None
    else None
)

msg_bands = config["data"]["A_bands"]
# TODO: Add resampling editor for MSG
msg_editors = [
    WavelengthSelectionEditor(
        wavelengths=msg_bands,
    ),
    MinMaxNormEditor(),
    NanDictEditor(),
]

goes_bands = config["data"]["B_bands"]
goes_editors = [
    WavelengthSelectionEditor(
        wavelengths=goes_bands,
    ),
    MinMaxNormEditor(),
    NanDictEditor(),
]

logger.info(f"Instantiating datasets.")

msg_dataset = GeoDataset(
    satellite="msg",
    data_dir=msg_path,
    splits_dict=splits_dict["train"],
    editors=msg_editors,
    load_zenith=False,
    load_solar=False,
    patch_size=msg_patch_size,
)
msg_dataset = StorageDataset(
    dataset=msg_dataset,
    store_dir=config["data"]["converted_A_path"],
    ext_editors=[RandomPatchEditor(patch_shape=(256, 256))],
)

msg_valid = GeoDataset(
    satellite="msg",
    data_dir=msg_path,
    splits_dict=splits_dict["val"],
    editors=msg_editors,
    load_zenith=False,
    load_solar=False,
    patch_size=msg_patch_size,
)
msg_valid = StorageDataset(
    dataset=msg_valid,
    store_dir=config["data"]["converted_A_path"],
    ext_editors=[RandomPatchEditor(patch_shape=(256, 256))],
)

goes_dataset = GeoDataset(
    satellite="goes",
    data_dir=goes_path,
    splits_dict=splits_dict["train"],
    editors=goes_editors,
    load_zenith=False,
    load_solar=False,
    patch_size=goes_patch_size,
)
goes_dataset = StorageDataset(
    dataset=goes_dataset,
    store_dir=config["data"]["converted_B_path"],
    ext_editors=[RandomPatchEditor(patch_shape=(256, 256))],
)

goes_valid = GeoDataset(
    satellite="goes",
    data_dir=goes_path,
    splits_dict=splits_dict["val"],
    editors=goes_editors,
    load_zenith=False,
    load_solar=False,
    patch_size=goes_patch_size,
)
goes_valid = StorageDataset(
    dataset=goes_valid,
    store_dir=config["data"]["converted_B_path"],
    ext_editors=[RandomPatchEditor(patch_shape=(256, 256))],
)

data_module = ITIDataModule(
    msg_dataset, goes_dataset, msg_valid, goes_valid, **config["data"]
)

# Setup logging
logger.info(f"Setting up WandB logging...")

logging_config = config["logging"]
wandb_id = logging_config["wandb_id"] if "wandb_id" in logging_config else None
log_model = (
    logging_config["wandb_log_model"] if "wandb_log_model" in logging_config else False
)

# Initialize wandb
run = wandb.init(
    project=logging_config["wandb_project"],
    name=logging_config["wandb_name"],
    entity=logging_config["wandb_entity"],
    id=wandb_id,
    dir=save_dir,
)
wandb_logger = WandbLogger(
    project=logging_config["wandb_project"],
    name=logging_config["wandb_name"],
    offline=False,
    entity=logging_config["wandb_entity"],
    id=wandb_id,
    dir=save_dir,
    log_model=log_model,
)


# log config to wandb
logger.debug(f"Config: {config}")

# Start training
logger.info(f"Initializing training steps...")

module = ITIModule(**config["model"])

# setup save callbacks
logger.info(f"Initializing callbacks...")
checkpoint_dir = os.path.join(save_dir, "checkpoints")
os.makedirs(checkpoint_dir, exist_ok=True)
checkpoint_callback = ModelCheckpoint(
    dirpath=checkpoint_dir, save_last=True, every_n_epochs=1, save_weights_only=False
)
save_callback = SaveCallback(checkpoint_dir)

# setup plot callbacks
plot_callbacks = []

plot_settings_A = []
plot_settings_B = []

for wvl in config["data"]["A_bands"]:
    plot_settings_A.append({"cmap": "Blues", "title": f"MSG {wvl}"})
for wvl in config["data"]["B_bands"]:
    plot_settings_B.append({"cmap": "Greys", "title": f"GOES {wvl}"})

plot_callbacks += [
    PlotBAB(
        goes_valid.sample(4),
        module,
        plot_settings_A=plot_settings_A,
        plot_settings_B=plot_settings_B,
    )
]
plot_callbacks += [
    PlotABA(
        msg_valid.sample(4),
        module,
        plot_settings_A=plot_settings_A,
        plot_settings_B=plot_settings_B,
    )
]

n_gpus = torch.cuda.device_count()
n_cpus = os.cpu_count()

logger.info(f"Initializing Trainer...")
trainer = Trainer(
    max_epochs=int(config["training"]["epochs"]),
    fast_dev_run=False,
    logger=wandb_logger,
    devices=n_gpus if n_gpus > 0 else n_cpus,
    accelerator="gpu" if n_gpus >= 1 else "cpu",
    strategy="dp" if n_gpus > 1 else "auto",  # ddp breaks memory and wandb
    num_sanity_val_steps=0,
    callbacks=[checkpoint_callback, save_callback, *plot_callbacks],
    limit_train_batches=config["training"]["limit_train_batches"],
    limit_val_batches=config["training"]["limit_val_batches"],
)

logger.info(f"Starting training...")
trainer.fit(module, data_module, ckpt_path="last")
logger.info(f"Done...!")
