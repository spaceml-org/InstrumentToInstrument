import collections.abc

import autoroot  # Needed for import from src
import numpy as np

# hyper needs the four following aliases to be done manually.
collections.Iterable = collections.abc.Iterable
collections.Mapping = collections.abc.Mapping
collections.MutableSet = collections.abc.MutableSet
collections.MutableMapping = collections.abc.MutableMapping
import warnings

# Now import hyper
from tqdm import tqdm

from itipy.data.dataset import StorageDataset
from itipy.data.editor import RandomPatchEditor
from itipy.data.geo_datasets import GeoDataset
from itipy.data.geo_editor import (
    MinMaxNormEditor,
    NanDictEditor,
    WavelengthSelectionEditor,
)

warnings.filterwarnings("ignore")

from loguru import logger

SATELLITE = "msg"

PATHS = {
    "himawari": "/mnt/disks/pretraining/2025-esl-3dclouds-extremes-datasets/pre-training/himawari/l1b",
    "goes": "/mnt/disks/pretraining/2025-esl-3dclouds-extremes-datasets/pre-training/goes/mcmip",
    "msg": "/mnt/disks/pretraining/2025-esl-3dclouds-extremes-datasets/pre-training/msg/l1b",
}

MSG_CHANNELS = [
    640.0,
    810.0,
    1640.0,
    3920.0,
    6250.0,
    7350.0,
    8700.0,
    9660.0,
    10800.0,
    12000.0,
    13400.0,
]

GOES_CHANNELS = [
    470.0,
    640.0,
    870.0,
    1380.0,
    1610.0,
    2250.0,
    3890.0,
    6170.0,
    6930.0,
    7340.0,
    8440.0,
    9610.0,
    10330.0,
    11190.0,
    12270.0,
    13270.0,
]

HIMAWARI_CHANNELS = [
    470.0,
    510.0,
    640.0,
    860.0,
    1600.0,
    2300.0,
    3900.0,
    6200.0,
    6900.0,
    7300.0,
    8600.0,
    9600.0,
    10400.0,
    11200.0,
    12400.0,
    13300.0,
]

CHANNELS = {
    "himawari": HIMAWARI_CHANNELS,
    "goes": GOES_CHANNELS,
    "msg": MSG_CHANNELS,
}

# Define paths and parameters
data_path = PATHS[SATELLITE]
converted_data_path = f"/home/annajungbluth/converted/{SATELLITE}"
patch_size = (256, 256)
converted_patch_size = (256, 256)
bands = CHANNELS[SATELLITE]
resolution = None


# default split configuration for the datamodule
SPLITS_DICT = {
    "train": {
        "years": np.arange(2004, 2025).tolist(),
        "months": np.arange(1, 13).tolist(),
        "days": np.arange(2, 23).tolist(),
    },
    "val": {
        "years": np.arange(2004, 2025).tolist(),
        "months": np.arange(1, 13).tolist(),
        "days": np.arange(24, 32).tolist(),
    },
    "test": {
        "years": np.arange(2004, 2025).tolist(),
        "months": np.arange(1, 13).tolist(),
        "days": [1, 23],
    },
}

editors = [
    WavelengthSelectionEditor(
        wavelengths=bands,
    ),
    MinMaxNormEditor(),
    NanDictEditor(),
]

# Instantiating train dataset for satellite
train_dataset = GeoDataset(
    satellite=SATELLITE,
    data_dir=data_path,
    splits_dict=SPLITS_DICT["train"],
    editors=editors,
    load_zenith=False,
    load_solar=False,
    patch_size=patch_size,
    resolution=resolution,
    center_crop=False,
    radius=0,
    filter_daytime=False,
    stats_filepath=None,
)

train_dataset = StorageDataset(
    dataset=train_dataset,
    store_dir=f"{converted_data_path}/train",
    ext_editors=[RandomPatchEditor(patch_shape=converted_patch_size)],
)

# Instantiating valid dataset for satellite
valid_dataset = GeoDataset(
    satellite=SATELLITE,
    data_dir=data_path,
    splits_dict=SPLITS_DICT["val"],
    editors=editors,
    load_zenith=False,
    load_solar=False,
    patch_size=patch_size,
    resolution=resolution,
    center_crop=False,
    radius=0,
    filter_daytime=False,
    stats_filepath=None,
)

valid_dataset = StorageDataset(
    dataset=valid_dataset,
    store_dir=f"{converted_data_path}/val",
    ext_editors=[RandomPatchEditor(patch_shape=converted_patch_size)],
)

# Instantiating test dataset for satellite
test_dataset = GeoDataset(
    satellite=SATELLITE,
    data_dir=data_path,
    splits_dict=SPLITS_DICT["test"],
    editors=editors,
    load_zenith=False,
    load_solar=False,
    patch_size=patch_size,
    resolution=resolution,
    center_crop=False,
    radius=0,
    filter_daytime=False,
    stats_filepath=None,
)

test_dataset = StorageDataset(
    dataset=test_dataset,
    store_dir=f"{converted_data_path}/test",
    ext_editors=[RandomPatchEditor(patch_shape=converted_patch_size)],
)

logger.info(f"Starting conversion of {SATELLITE} data")
logger.info(
    f"Saving {len(train_dataset) + len(valid_dataset) + len(test_dataset)} files to {converted_data_path}"
)
logger.info(f"Saving {len(CHANNELS[SATELLITE])} channels: {CHANNELS[SATELLITE]}")

logger.info("Converting train dataset")
for _ in tqdm(range(len(train_dataset))):
    _ = train_dataset[_]

logger.info("Converting valid dataset")
for _ in tqdm(range(len(valid_dataset))):
    _ = valid_dataset[_]

logger.info("Converting test dataset")
for _ in tqdm(range(len(test_dataset))):
    _ = test_dataset[_]
