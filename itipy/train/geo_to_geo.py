"""
Hydra training pipeline for translating between two geostationary satellite instruments.
"""
import ast
import collections.abc
import os
import sys

import autoroot  # Needed for import from src
import hydra
import omegaconf

# hyper needs the four following aliases to be done manually.
collections.Iterable = collections.abc.Iterable
collections.Mapping = collections.abc.Mapping
collections.MutableSet = collections.abc.MutableSet
collections.MutableMapping = collections.abc.MutableMapping
import warnings

# Now import hyper
import torch
import wandb
from lightning import Trainer
from lightning.pytorch import seed_everything
from lightning.pytorch.callbacks import ModelCheckpoint
from lightning.pytorch.loggers import WandbLogger
from omegaconf import DictConfig

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


from loguru import logger

from itipy.callback import PlotABA, PlotBAB, SaveCallback
from itipy.data.data_module import ITIDataModule
from itipy.iti import ITIModule


@hydra.main(
    version_base="1.3",
    config_path="ADD-PATH-TO-CONFIG",
    config_name="train.yaml",
)
def main(config: DictConfig):
    # ------- seeds -------
    # extract and set model and data seeds
    seed = config.seed if "seed" in config else 42
    logger.info(f"training with seed {seed}...")
    seed_everything(seed, workers=True)

    # ------- wandb logging -------
    # set up wandb config
    wandb.config = omegaconf.OmegaConf.to_container(
        config, resolve=True, throw_on_missing=True
    )

    # get wandb experiment tags from config
    tags = config.logging.tags if "tags" in config.logging else []
    if isinstance(tags, str):
        tags = tags.split()

    # get experiment name from config
    experiment_name = config.logging.wandb_name

    # set up wandb logger
    output_dir = hydra.core.hydra_config.HydraConfig.get().runtime.output_dir
    logger.info(f"output dir: {output_dir}...")

    wandb_logger = WandbLogger(
        name=experiment_name,
        project=config.logging.wandb_project,
        entity=config.logging.wandb_entity,
        mode=config.logging.wandb_mode if "wandb_mode" in config.logging else "online",
        tags=tags,
        save_dir=output_dir,
    )

    # log command to terminal and wandb
    cmd = " ".join(sys.argv)
    logger.info(f"Command executed: {cmd}")

    # log config to wandb
    yaml_str = omegaconf.OmegaConf.to_yaml(config)
    logger.debug(f"Hydra-config: {yaml_str}")

    # ------- dataloaders -------

    # Parameters for satellite A (the one to be translated from)
    A_patch_size = (
        ast.literal_eval(config.data.A_patch_size)
        if config.data.A_patch_size is not None
        else None
    )
    A_bands = config.data.A_bands
    # TODO: Make more modular using hydra config instantiation
    A_editors = [
        WavelengthSelectionEditor(
            wavelengths=A_bands,
        ),
        MinMaxNormEditor(),
        NanDictEditor(),
    ]

    # Parameters for satellite B (the one to be translated to)
    config.data.B_path
    B_patch_size = (
        ast.literal_eval(config.data.B_patch_size)
        if config.data.B_patch_size is not None
        else None
    )
    B_bands = config.data.B_bands
    # TODO: Make more modular using hydra config instantiation
    B_editors = [
        WavelengthSelectionEditor(
            wavelengths=B_bands,
        ),
        MinMaxNormEditor(),
        NanDictEditor(),
    ]
    # Instantiate datasets and dataloaders

    logger.info("instantiating datasets...")

    # Instantiating dataset for satellite A
    A_train_dataset = GeoDataset(
        satellite=config.data.A_satellite,
        data_dir=config.data.A_path,
        splits_dict=splits_dict["train"],
        editors=A_editors,
        load_zenith=False,
        load_solar=False,
        patch_size=A_patch_size,
        resolution=config.data.A_resolution if "A_resolution" in config.data else None,
        center_crop=config.data.A_center_crop
        if "A_center_crop" in config.data
        else False,
        radius=config.data.A_radius if "A_radius" in config.data else 0,
    )
    A_valid_dataset = GeoDataset(
        satellite=config.data.A_satellite,
        data_dir=config.data.A_path,
        splits_dict=splits_dict["val"],
        editors=A_editors,
        load_zenith=False,
        load_solar=False,
        patch_size=A_patch_size,
        resolution=config.data.A_resolution if "A_resolution" in config.data else None,
        center_crop=config.data.A_center_crop
        if "A_center_crop" in config.data
        else False,
        radius=config.data.A_radius if "A_radius" in config.data else 0,
    )

    if "converted_A_path" in config.data:
        converted_A_patch_size = (
            ast.literal_eval(config.data.converted_A_patch_size)
            if "converted_A_patch_size" in config.data
            and config.data.converted_A_patch_size is not None
            else (256, 256)
        )
        A_train_dataset = StorageDataset(
            dataset=A_train_dataset,
            store_dir=config.data.converted_A_path,
            ext_editors=[RandomPatchEditor(patch_shape=converted_A_patch_size)],
        )
        A_valid_dataset = StorageDataset(
            dataset=A_valid_dataset,
            store_dir=config.data.converted_A_path,
            ext_editors=[RandomPatchEditor(patch_shape=converted_A_patch_size)],
        )

    # Instantiating dataset for satellite B
    B_train_dataset = GeoDataset(
        satellite=config.data.B_satellite,
        data_dir=config.data.B_path,
        splits_dict=splits_dict["train"],
        editors=B_editors,
        load_zenith=False,
        load_solar=False,
        patch_size=B_patch_size,
        resolution=config.data.B_resolution if "B_resolution" in config.data else None,
        center_crop=config.data.B_center_crop
        if "B_center_crop" in config.data
        else False,
        radius=config.data.B_radius if "B_radius" in config.data else 0,
    )
    B_valid_dataset = GeoDataset(
        satellite=config.data.B_satellite,
        data_dir=config.data.B_path,
        splits_dict=splits_dict["val"],
        editors=B_editors,
        load_zenith=False,
        load_solar=False,
        patch_size=B_patch_size,
        resolution=config.data.B_resolution if "B_resolution" in config.data else None,
        center_crop=config.data.B_center_crop
        if "B_center_crop" in config.data
        else False,
        radius=config.data.B_radius if "B_radius" in config.data else 0,
    )

    if "converted_B_path" in config.data:
        converted_B_patch_size = (
            ast.literal_eval(config.data.converted_B_patch_size)
            if "converted_B_patch_size" in config.data
            and config.data.converted_B_patch_size is not None
            else (256, 256)
        )
        B_train_dataset = StorageDataset(
            dataset=B_train_dataset,
            store_dir=config.data.converted_B_path,
            ext_editors=[RandomPatchEditor(patch_shape=converted_B_patch_size)],
        )
        B_valid_dataset = StorageDataset(
            dataset=B_valid_dataset,
            store_dir=config.data.converted_B_path,
            ext_editors=[RandomPatchEditor(patch_shape=converted_B_patch_size)],
        )

    logger.info("instantiating ITI dataloader...")
    data_module = ITIDataModule(
        A_train_ds=A_train_dataset,
        B_train_ds=B_train_dataset,
        A_valid_ds=A_valid_dataset,
        B_valid_ds=B_valid_dataset,
        num_workers=config.training.num_workers
        if "num_workers" in config.training
        else 4,
        iterations_per_epoch=config.training.iterations_per_epoch
        if "iterations_per_epoch" in config.training
        else 10000,
    )

    # ------- training -------

    # Start training
    logger.info(f"Initializing ITI model...")

    module = ITIModule(**config["model"])

    logger.info(f"Initializing callbacks...")
    # setup save callbacks
    checkpoint_dir = os.path.join(output_dir, "checkpoints")
    os.makedirs(checkpoint_dir, exist_ok=True)
    checkpoint_callback = ModelCheckpoint(
        dirpath=checkpoint_dir,
        save_last=True,
        every_n_epochs=1,
        save_weights_only=False,
    )
    save_callback = SaveCallback(checkpoint_dir)

    # setup plot callbacks
    plot_callbacks = []

    plot_settings_A = []
    plot_settings_B = []

    for wvl in config.data.A_bands:
        plot_settings_A.append({"cmap": "Blues", "title": f"MSG {wvl}"})
    for wvl in config.data.B_bands:
        plot_settings_B.append({"cmap": "Greys", "title": f"GOES {wvl}"})

    plot_callbacks += [
        PlotBAB(
            B_valid_dataset.sample(4),
            module,
            plot_settings_A=plot_settings_A,
            plot_settings_B=plot_settings_B,
        )
    ]
    plot_callbacks += [
        PlotABA(
            A_valid_dataset.sample(4),
            module,
            plot_settings_A=plot_settings_A,
            plot_settings_B=plot_settings_B,
        )
    ]

    n_gpus = torch.cuda.device_count()
    n_cpus = os.cpu_count()

    logger.info(f"Initializing trainer...")
    trainer = Trainer(
        max_epochs=int(config.training.epochs),
        fast_dev_run=False,
        logger=wandb_logger,
        devices=n_gpus if n_gpus > 0 else n_cpus,
        accelerator="gpu" if n_gpus >= 1 else "cpu",
        strategy="dp" if n_gpus > 1 else "auto",  # ddp breaks memory and wandb
        num_sanity_val_steps=0,
        callbacks=[checkpoint_callback, save_callback, *plot_callbacks],
        limit_train_batches=config.training.limit_train_batches,
        limit_val_batches=config.training.limit_val_batches,
    )

    logger.info(f"Starting training...")
    trainer.fit(module, data_module, ckpt_path="last")
    logger.info(f"Done...!")


if __name__ == "__main__":
    main()
