from random import randint

import numpy as np
import torch
from loguru import logger

from itipy.data.editor import Editor
from itipy.data.geo_utils import convert_units


def _patch_valid(patch_ds):
    all_nan_rad = np.all(
        np.isnan(patch_ds["Rad"].values)
    )  # Check if all values are NaN
    all_nan_lat = np.all(
        np.isnan(patch_ds["latitude"].values)
    )  # Check if all values are NaN
    all_nan_lon = np.all(
        np.isnan(patch_ds["longitude"].values)
    )  # Check if all values are NaN
    if all_nan_rad or all_nan_lat or all_nan_lon:
        return False
    else:
        return True


def create_fov_mask(shape, fov_radius):
    """
    Function to create mask for specified field of view.
    """
    # Create coordinate grids
    y, x = np.ogrid[: shape[0], : shape[1]]
    # Calculate center points
    center_y, center_x = shape[0] // 2, shape[1] // 2
    # Calculate distance from center for each point
    dist_from_center = np.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
    # Normalize distances by max possible distance (corner to center)
    max_dist = np.sqrt((center_x) ** 2 + (center_y) ** 2)
    normalized_dist = dist_from_center / max_dist
    # Create mask for specified field of view
    mask = normalized_dist <= fov_radius
    return mask


class CenterWeightedCropDatasetEditor:
    def __init__(self, patch_shape, data_key="Rad", fov_radius=0.6):
        self.patch_shape = patch_shape
        self.data_key = data_key
        self.fov_radius = fov_radius
        self.max_attempts = 5

    def __call__(self, ds):
        assert (
            ds["x"].shape[0] >= self.patch_shape[0]
        ), "Invalid dataset shape: %s" % str(ds["x"].shape)
        assert (
            ds["y"].shape[0] >= self.patch_shape[1]
        ), "Invalid dataset shape: %s" % str(ds["y"].shape)

        # get x/y grid
        x_grid, y_grid = np.meshgrid(
            np.arange(0, ds.x.shape[0], 1), np.arange(0, ds.y.shape[0], 1)
        )

        # create mask for valid coordinates within desired field of view
        # NOTE: This masks from the center to the image edge, rather than disk edge
        valid_mask = create_fov_mask(
            shape=(ds.x.shape[0], ds.y.shape[0]), fov_radius=self.fov_radius
        )

        # get coordinate pairs for valid points
        coords_on_disk = np.column_stack((x_grid[valid_mask], y_grid[valid_mask]))
        del x_grid, y_grid

        # TODO: Add while loop to ensure valid patch is found?
        # pick random x/y index

        attempts = 0
        while attempts <= self.max_attempts:
            random_idx = np.random.randint(0, len(coords_on_disk))
            x, y = tuple(coords_on_disk[random_idx])
            # define patch boundaries
            xmin = x - self.patch_shape[0] // 2
            ymin = y - self.patch_shape[1] // 2
            xmax = x + self.patch_shape[0] // 2
            ymax = y + self.patch_shape[1] // 2

            # crop patch
            patch_ds = ds.sel(
                {
                    "x": slice(ds["x"][xmin], ds["x"][xmax - 1]),
                    "y": slice(ds["y"][ymin], ds["y"][ymax - 1]),
                }
            )
            # check that there are no constant channels
            if not np.any(np.nanstd(ds.Rad.values, axis=(1, 2)) == 0):
                return patch_ds, xmin, ymin
            attempts += 1
        logger.info(
            "Could not find patch without constant channels after 5 cropping attempts"
        )
        return patch_ds, xmin, ymin


class RandomCropDatasetEditor:
    def __init__(self, patch_shape, x="x", y="y", data_key="Rad"):
        self.patch_shape = patch_shape
        self.x = x
        self.y = y
        self.data_key = data_key

    def __call__(self, ds):
        assert (
            ds[self.x].shape[0] >= self.patch_shape[0]
        ), "Invalid dataset shape: %s" % str(dataset[self.x].shape)
        assert (
            ds[self.y].shape[0] >= self.patch_shape[1]
        ), "Invalid dataset shape: %s" % str(dataset[self.y].shape)

        max_attempts = 20
        while True:
            xmin = randint(0, ds[self.x].shape[0] - self.patch_shape[0])
            ymin = randint(0, ds[self.y].shape[0] - self.patch_shape[1])
            patch_ds = ds.sel(
                {
                    self.x: slice(
                        ds[self.x][xmin], ds[self.x][xmin + self.patch_shape[0] - 1]
                    ),  # 0-based index
                    self.y: slice(
                        ds[self.y][ymin], ds[self.y][ymin + self.patch_shape[1] - 1]
                    ),
                }
            )  # 0-based index
            if _patch_valid(patch_ds):
                break
            else:
                max_attempts -= 1
                if max_attempts == 0:
                    logger.info(
                        "Could not find valid coordinates in patch after 20 cropping attempts"
                    )
                    break
        return patch_ds


class BandOrderEditor(Editor):
    """
    Reorders bands in data dictionary.
    """

    def __init__(self, target_order, key="data"):
        """
        Args:
            target_order (list): Order of bands
            key (str): Key in dictionary to apply transformation
        """
        self.target_order = target_order
        self.key = key

    def call(self, data_dict, **kwargs):
        source_order = data_dict["wavelengths"]
        assert len(source_order) == len(
            self.target_order
        ), "Length of source and target wavelengths must match."
        # Get indexes of bands to select
        indexes = [np.where(source_order == wvl)[0][0] for wvl in self.target_order]
        # Extract data
        data = data_dict[self.key]
        # Subselect bands
        data = data[indexes]
        # Update dictionary
        data_dict[self.key] = data
        data_dict["wavelengths"] = np.array(self.target_order)
        return data_dict


class BandSelectionEditor(Editor):
    """
    Selects a subset of available bands from data dictionary
    """

    def __init__(
        self,
        target_bands,
        keys=["data", "wavelengths", "sensor_info"],
    ):
        """
        Args:
            target_bands (list): List of bands to select
            key (str): Key in dictionary to apply transformation
        """
        self.target_bands = target_bands
        self.keys = keys

    def call(self, data_dict, **kwargs):
        source_bands = data_dict["band_names"]
        # Get indexes of bands to select
        indexes = [source_bands.index(band) for band in self.target_bands]

        for key in self.keys:
            # Extract data
            try:
                data = data_dict[key]
            except KeyError:
                continue
            if type(data) is list:
                data = [data[i] for i in indexes]
                assert len(data) == len(self.target_bands)
            elif type(data) is dict:
                data = {k: data[k] for k in self.target_bands}
            else:
                # Subselect bands
                data = data[indexes]
                assert data.shape[0] == len(self.target_bands)
            # Update dictionary
            data_dict[key] = data
        data_dict["band_names"] = self.target_bands
        return data_dict


class WavelengthSelectionEditor(Editor):
    """
    Selects a subset of available bands from data dictionary
    """

    def __init__(
        self,
        wavelengths,
        keys=["data", "wavelengths", "sensor_info"],
    ):
        """
        Args:
            wavelengths (list): List of wavelengths to select closest matching band for
            key (str): Key in dictionary to apply transformation
        """
        self.wavelengths = wavelengths
        self.keys = keys

    def call(self, data_dict, **kwargs):
        source_wavelengths = data_dict["wavelengths"]

        # match wavelengths to bands
        # find distance between self.wavelengths and source_wavelengths
        distances = np.abs(
            np.array(source_wavelengths)[:, None] - np.array(self.wavelengths)[None, :]
        )
        # for each, find the index of the closest wavelength
        indexes = np.argmin(distances, axis=0)

        closest_bands = [data_dict["band_names"][i] for i in indexes]
        wavelength_keys = [str(w) for w in self.wavelengths]

        for key in self.keys:
            # Extract data
            try:
                data = data_dict[key]
            except KeyError:
                continue
            if type(data) is list:
                data = [data[i] for i in indexes]
                assert len(data) == len(closest_bands)
            elif type(data) is dict:
                data = {w: data[k] for w, k in zip(wavelength_keys, closest_bands)}
                assert len(data) == len(closest_bands)
            else:
                # Subselect bands
                data = data[indexes]
                assert data.shape[0] == len(closest_bands)
            # Update dictionary
            data_dict[key] = data
        data_dict["band_names"] = wavelength_keys
        return data_dict


class NanMaskEditor(Editor):
    """
    Returns mask for NaN values in data dictionary
    """

    def __init__(self, key="data"):
        self.key = key

    def call(self, data_dict, **kwargs):
        data = data_dict[self.key]
        # Check if any band contains NaN values
        mask = np.isnan(data).any(axis=0)
        mask = mask.astype(int)
        # Update dictionary
        data_dict["nan_mask"] = mask
        return data_dict


class NanDictEditor(Editor):
    """
    Removes NaN values from data dictionary.
    Can also be used to replace NaN values of coordinates to remove off limb data.
    """

    def __init__(self, key="data", fill_value=0):
        self.key = key
        self.fill_value = fill_value

    def call(self, data_dict, **kwargs):
        data = data_dict[self.key]
        # Replace NaN values
        data = np.nan_to_num(data, nan=self.fill_value)
        # Update dictionary
        data_dict[self.key] = data
        return data_dict


class RadUnitEditor(Editor):
    """
    Convert radiance values from mW/m^2/sr/cm^-1 to W/m^2/sr/um
    """

    def __init__(self, key="data"):
        self.key = key

    def call(self, data_dict, **kwargs):
        data = data_dict[self.key]
        wavelengths = data_dict["wavelengths"]
        # Convert units
        data = convert_units(data, wavelengths)
        # Update dictionary
        data_dict[self.key] = data
        return data_dict


class Rotate180Editor(Editor):
    """
    Rotate data by 180 degrees
    """

    def __init__(self, key="data"):
        self.key = key

    def call(self, data_dict, **kwargs):
        data = data_dict[self.key]
        # Rotate data
        data = np.rot90(data, k=2, axes=(1, 2))
        # Update dictionary
        data_dict[self.key] = data
        return data_dict


class StackDictEditor(Editor):
    """
    Stack data dictionary into a single array
    """

    def __init__(
        self,
        keys=["data", "coords", "sat_angle", "solar_angle", "time"],
        stack_key="data",
        only_fractional_time=True,
        norm_angles=False,
        axis=0,
    ):
        self.keys = keys
        self.axis = axis
        self.stack_key = stack_key
        self.only_fractional_time = only_fractional_time
        self.norm_angles = norm_angles  # whether to normalize the angles between [0, 1] or keep as [0, 2*pi]
        self.convert2radians = ConvertToRadiansEditor(norm_angles=self.norm_angles)
        self.convert2d = TimeTo2DEditor()

    def call(self, data_dict):
        # Convert angles to radians
        data_dict = self.convert2radians.call(data_dict)
        # Convert 1D time arrays to 2D arrays
        data_dict = self.convert2d.call(data_dict)
        # Select data
        data = []
        for key in self.keys:
            values = data_dict[key]
            if len(values.shape) == 2:
                # if the variable has no channel dimension, add a new axis
                values = np.expand_dims(values, axis=self.axis)
            if key == "time" and self.only_fractional_time:
                # if the variable is time, only keep the fraction of year/day
                values = values[-2:, :, :]
            data.append(values)
        # Stack data
        data = np.concatenate(data, axis=self.axis).astype(np.float32)
        # Update dictionary
        data_dict[self.stack_key] = data
        # Return numpy array
        return data_dict


class ConvertToRadiansEditor(Editor):
    """
    Convert angles in degrees to radians.
    """

    def __init__(
        self,
        keys=["coords", "sat_angle", "solar_angle"],
        norm_angles: bool = False,
    ):
        self.keys = keys
        self.norm_angles = norm_angles
        self.ranges = {
            "coords": {
                "zenith": {  # scaling for latitude
                    "min": -90,
                    "max": 90,
                },
                "azimuth": {  # scaling for longitude
                    "min": -180,
                    "max": 180,
                },
            },
            "sat_angle": {
                "zenith": {
                    "min": 0,
                    "max": 180,
                },
                "azimuth": {
                    "min": 0,
                    "max": 360,
                },
            },
            "solar_angle": {
                "zenith": {
                    "min": 0,
                    "max": 180,
                },
                "azimuth": {
                    "min": 0,
                    "max": 360,
                },
            },
        }

    def convert_angle(self, data, min, max):
        """
        Convert angles in degrees to radians and scale to [0, 2*pi].
        """
        # convert to radians and scale to [0, 2*pi]
        val_radians = 2 * np.pi * (data - min) / (max - min)
        return val_radians

    def convert_half_angle(self, data, min, max):
        """
        Convert angles in degrees to radians and scale to [0, pi].
        """
        # convert to radians and scale to [0, pi]
        val_radians = np.pi * (data - min) / (max - min)
        return val_radians

    def call(self, data_dict):
        # Convert angles to radians
        for key in self.keys:
            data = data_dict[key]
            data[0] = self.convert_half_angle(
                data[0],
                self.ranges[key]["zenith"]["min"],
                self.ranges[key]["zenith"]["max"],
            )
            data[1] = self.convert_angle(
                data[1],
                self.ranges[key]["azimuth"]["min"],
                self.ranges[key]["azimuth"]["max"],
            )
            if self.norm_angles:  # normalize between [0, 1] if self.norm
                data[0] = data[0] / (2 * np.pi)
                data[1] = data[1] / (2 * np.pi)
            # Update dictionary
            data_dict[key] = data
        return data_dict


class TimeTo2DEditor(Editor):
    """
    Copy 1D arrays to 2D arrays of shape (1, H, W).
    """

    def __init__(self, keys=["time"], height=256, width=256):
        self.keys = keys
        self.height = height
        self.width = width

    def call(self, data_dict):
        for key in self.keys:
            length = len(data_dict[key])
            data_2d = np.zeros(
                (length, self.height, self.width), dtype=data_dict[key].dtype
            )
            for i in range(length):
                data_2d[i, :, :] = np.tile(
                    data_dict[key][i], (1, self.height, self.width)
                )
            data_dict[key] = data_2d
        return data_dict


class ToTensorEditor(Editor):
    """
    Convert numpy array to PyTorch tensor
    """

    def __init__(self, dtype=torch.float32):
        self.dtype = dtype

    def call(self, data, **kwargs):
        # Convert to tensor
        tensor = torch.as_tensor(data, dtype=self.dtype)
        return tensor


class PrecomputedMinMaxNormEditor(Editor):
    """
    Normalises data to have values between -1 and 1 from precomputed min and max values.
    """

    def __init__(self, norm_dict, key="data", band_info_key="wavelengths"):
        """
        Args:
            norm_dict (dict): Dictionary with min and max for each band
            key (str): Key in dictionary to apply transformation
            band_info_key (str): Key in dictionary to get band information
        """
        self.band_info = norm_dict
        self.key = key
        self.band_info_key = band_info_key

    def call(self, data_dict, **kwargs):
        # get data to be normalised
        data = data_dict[self.key]
        # get the min and max for each band - type conversion needed as json keys and values are strings
        mins = np.array(
            [float(self.band_info[key]["min"]) for key in data_dict[self.band_info_key]]
        )
        maxs = np.array(
            [float(self.band_info[key]["max"]) for key in data_dict[self.band_info_key]]
        )
        # normalise each band using min and max
        data = ((data - mins[:, None, None]) / (maxs - mins)[:, None, None]) * 2 - 1
        # update dictionary
        data_dict[self.key] = data
        return data_dict


class MinMaxNormEditor(Editor):
    """
    Normalises data to a range of [-1, 1] using min-max scaling.
    """

    def __init__(self, bt_min=180, bt_max=350, nr_min=0, nr_max=100):
        self.bt_min = bt_min
        self.bt_max = bt_max
        self.nr_min = nr_min
        self.nr_max = nr_max

    def call(self, data_dict, **kwargs):
        for i, key in enumerate(data_dict["band_names"]):
            sensor_type = data_dict["sensor_info"][key]["band_type"]
            if sensor_type == "TOA Normalised Brightness Temperature":
                data_dict["data"][i] = np.clip(
                    data_dict["data"][i], self.bt_min, self.bt_max
                )
                # Apply min-max scaling to [-1, 1]
                data_dict["data"][i] = (
                    (data_dict["data"][i] - self.bt_min)
                    / (self.bt_max - self.bt_min)
                    * 2
                ) - 1
            if sensor_type == "TOA Reflectance":
                data_dict["data"][i] = np.clip(
                    data_dict["data"][i], self.nr_min, self.nr_max
                )
                # Apply min-max scaling to [-1, 1]
                data_dict["data"][i] = (
                    (data_dict["data"][i] - self.nr_min)
                    / (self.nr_max - self.nr_min)
                    * 2
                ) - 1
        return data_dict
