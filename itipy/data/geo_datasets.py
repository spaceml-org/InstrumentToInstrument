from __future__ import annotations

import collections
import collections.abc

# hyper needs the four following aliases to be done manually.
collections.Iterable = collections.abc.Iterable
collections.Mapping = collections.abc.Mapping
collections.MutableSet = collections.abc.MutableSet
collections.MutableMapping = collections.abc.MutableMapping

import logging

import autoroot  # required for imports from src
import numpy as np
import xarray as xr
from loguru import logger

from itipy.data.dataset import BaseDataset
from itipy.data.editor import Editor
from itipy.data.geo_editor import CenterWeightedCropDatasetEditor
from itipy.data.geo_utils import get_list_filenames, get_split
from itipy.data.goes.load import load_goes_file
from itipy.data.himawari.load import load_himawari_file
from itipy.data.msg.load import load_msg_file

load_functions = {
    "goes": load_goes_file,
    "himawari": load_himawari_file,
    "msg": load_msg_file,
}


class GeoDataset(BaseDataset):
    """
    Class to load geostationary satellite data (GOES, HIMAWARI, MSG).

    Args:
        satellite (str): The satellite name. Options are "goes", "himawari", "msg".
        data_dir (List[str]): A list of directories containing the data files.
        editors (List[Editor]): A list of editors for data preprocessing.
        splits_dict (Dict, optional): A dictionary specifying the splits for the dataset. Defaults to None.
        ext (str, optional): The file extension of the data files. Defaults to "nc".
        limit (int, optional): The maximum number of files to load. Defaults to None.
        load_zenith (bool, optional): Whether to load the zenith angle. Defaults to True.
        load_solar (bool, optional): Whether to load the solar angle. Defaults to True.
        patch_size (tuple[int, int], optional): The size of the patches to crop. Defaults to None.
        center_crop (bool, optional): Whether to crop the data to the center. Defaults to False.
        radius (int, optional): The radius for cropping, if center_crop is True. Defaults to 0.
        **kwargs: Additional keyword arguments.
    """

    def __init__(
        self,
        satellite: str,
        data_dir: list[str],
        splits_dict: dict,
        editors: list[Editor] = None,
        ext: str = "nc",
        limit: int = None,
        load_zenith: bool = True,
        load_solar: bool = True,
        patch_size: list[int] | None = None,  # Patch size for cropping the data
        center_crop: bool = False,  # If True, will crop to the center of the image
        radius: int = 0,  # Radius for cropping, if center_crop is True
        **kwargs,
    ):
        if satellite.lower() not in ["goes", "himawari", "msg"]:
            raise ValueError(
                f"Satellite {satellite} not recognized. Options are 'goes', 'himawari', 'msg'."
            )
        self.satellite = satellite.lower()
        self.data_dir = data_dir
        self.splits_dict = splits_dict
        self.editors = editors
        self.ext = ext
        self.limit = limit
        self.patch_size = patch_size
        self.load_zenith = load_zenith
        self.load_solar = load_solar
        self.patch_size = patch_size  # Patch size for cropping the data
        self.center_crop = center_crop  # If True, will crop to the center of the image
        self.radius = radius
        self.max_attempts = 20  # Maximum number of attempts to load valid data

        self.files = self.get_files()

        super().__init__(
            data=self.files,
            editors=self.editors,
            ext=self.ext,
            limit=self.limit,
            **kwargs,
        )

    def setup(self, stage):
        pass

    def prepare_data(self):
        pass

    def get_files(self):
        # Get filenames from data_dir
        files = get_list_filenames(data_path=self.data_dir, ext=self.ext)
        # split files based on split criteria
        files = get_split(files=files, split_dict=self.splits_dict)
        return files

    def getIndex(self, data_dict, idx):
        # Attempt applying editors
        try:
            return self.convertData(data_dict)
        except Exception as ex:
            logging.error(f"Unable to convert {self.files[idx]}: {ex}")
            raise ex

    def __len__(self):
        return len(self.files)

    def __getitem__(self, idx):  # can output array or dict depending on transforms
        attempts_remaining = self.max_attempts  # Local copy for this call
        while attempts_remaining > 0:
            try:  # Check that there are no errors loading the file
                file_path = self.files[idx]

                data_dict = load_functions[self.satellite](
                    file=file_path,
                    load_zenith=self.load_zenith,
                    load_solar=self.load_solar,
                    patch_size=self.patch_size,
                    center_crop=self.center_crop,
                    radius=self.radius,
                )

                break  # If the file is successfully loaded, break the loop

            except Exception as e:
                # If we have no attempts left, raise an error
                if attempts_remaining <= 0:
                    raise ValueError(
                        f"Could not load valid file after {self.max_attempts} attempts. "
                        f"Error: {e}"
                    )

                # KeyErrors can arise if any of the variables are missing
                logger.warning(
                    f"Error loading {self.files[idx]}. "
                    f"Attempting with other files. "
                    f"Error: {e}"
                )

                # If there is an error, try to load another file
                idx = np.random.randint(0, len(self.files))
                attempts_remaining -= 1
                continue

        data_dict["satellite"] = self.satellite

        # Apply transformations
        if self.editors is not None:
            # Apply editors
            data_dict, _ = self.getIndex(data_dict, idx)
            return data_dict["data"]
        else:
            return data_dict


class GeoDataset_FullDisk(BaseDataset):
    def __init__(
        self,
        data_dir: list[str],
        splits_dict: dict,
        editors: list[Editor] = None,
        ext: str = "nc",
        limit: int = None,
        fov_radius: float = 0.6,
        load_coords: bool = True,
        load_cloudmask: bool = True,
        patch_size: tuple[int, int] = None,  # (256, 256),
        **kwargs,
    ):
        """
        Initializes the GeoDataset_FullDisk class. Designed to load full-disk satellite data as processed via rs_tools.

        Args:
            data_dir (List[str]): A list of directories containing the data files.
            editors (List[Editor]): A list of editors for data preprocessing.
            splits_dict (Dict, optional): A dictionary specifying the splits for the dataset. Defaults to None.
            ext (str, optional): The file extension of the data files. Defaults to "nc".
            limit (int, optional): The maximum number of files to load. Defaults to None.
            fov_radius (float, optional): The radius of the field of view. Defaults to 0.6.
            load_coords (bool, optional): Whether to load the coordinates. Defaults to True.
            load_cloudmask (bool, optional): Whether to load the cloud mask. Defaults to True.
            patch_size (tuple[int, int], optional): The size of the patches to crop. Defaults to None.
            **kwargs: Additional keyword arguments.

        """
        self.data_dir = data_dir
        self.editors = editors
        self.splits_dict = splits_dict
        self.ext = ext
        self.limit = limit
        self.fov_radius = fov_radius
        self.load_coords = load_coords
        self.load_cloudmask = load_cloudmask
        self.patch_size = patch_size

        self.files = self.get_files()

        if self.patch_size is not None:
            self.crop = CenterWeightedCropDatasetEditor(
                patch_shape=self.patch_size, fov_radius=self.fov_radius
            )

        super().__init__(
            data=self.files,
            editors=self.editors,
            ext=self.ext,
            limit=self.limit,
            **kwargs,
        )

    def get_files(self):
        # Get filenames from data_dir
        files = get_list_filenames(data_path=self.data_dir, ext=self.ext)
        # split files based on split criteria
        files = get_split(files=files, split_dict=self.splits_dict)
        return files

    def __len__(self):
        return len(self.files)

    def getIndex(self, data_dict, idx):
        # Attempt applying editors
        try:
            return self.convertData(data_dict)
        except Exception as ex:
            logging.error(f"Unable to convert {self.files[idx]}: {ex}")
            raise ex

    def __getitem__(self, idx):
        data_dict = {}

        ds: xr.Dataset = xr.load_dataset(self.files[idx], engine="netcdf4")
        if self.patch_size is not None:
            ds, xmin, ymin = self.crop(ds)
        else:
            xmin, ymin = 0, 0  # Set to 0 if no cropping is done
        data = ds.Rad.compute().to_numpy()

        data_dict["data"] = data
        del data  # Delete data to reduce memory usage
        # Extract wavelengths
        wavelengths = ds.band_wavelength.compute().to_numpy()
        data_dict["wavelengths"] = wavelengths
        del wavelengths  # Delete data to reduce memory usage

        # Extract coordinates
        if self.load_coords:
            latitude = ds.latitude.compute().to_numpy()
            longitude = ds.longitude.compute().to_numpy()
            coords = np.stack([latitude, longitude], axis=0)
            data_dict["coords"] = coords
            del latitude, longitude  # Delete data to reduce memory usage
            del coords  # Delete data to reduce memory usage

        # Extract cloud mask
        if self.load_cloudmask:
            cloud_mask = ds.cloud_mask.compute().to_numpy()
            data_dict["cloud_mask"] = cloud_mask
            del cloud_mask  # Delete data to reduce memory usage

        # Delete dataset to reduce memory usage
        del ds

        if self.editors is not None:
            # Apply editors
            data, _ = self.getIndex(data_dict, idx)

            if np.any(np.nanstd(data, axis=(1, 2)) == 0):
                print(f"Constant channel in patch")
                print(f"File: {self.files[idx]}")
                print(f"Patch x/y: {xmin}/{ymin}")
            return data
        else:
            return data_dict
