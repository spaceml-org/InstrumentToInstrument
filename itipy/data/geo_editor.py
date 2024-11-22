import torch
import numpy as np
from random import randint
from loguru import logger

from itipy.data.editor import Editor
from itipy.data.geo_utils import convert_units

def _patch_valid(patch_ds):
    all_nan_rad = np.all(np.isnan(patch_ds['Rad'].values)) # Check if all values are NaN
    all_nan_lat = np.all(np.isnan(patch_ds['latitude'].values)) # Check if all values are NaN
    all_nan_lon = np.all(np.isnan(patch_ds['longitude'].values)) # Check if all values are NaN
    if all_nan_rad or all_nan_lat or all_nan_lon:
        return False
    else:
        return True

def create_fov_mask(shape, fov_radius):
    """
    Function to create mask for specified field of view.
    """
    # Create coordinate grids
    y, x = np.ogrid[:shape[0], :shape[1]]
    # Calculate center points
    center_y, center_x = shape[0] // 2, shape[1] // 2
    # Calculate distance from center for each point
    dist_from_center = np.sqrt((x - center_x)**2 + (y - center_y)**2)
    # Normalize distances by max possible distance (corner to center)
    max_dist = np.sqrt((center_x)**2 + (center_y)**2)
    normalized_dist = dist_from_center / max_dist
    # Create mask for specified field of view
    mask = normalized_dist <= fov_radius
    return mask

class CenterWeightedCropDatasetEditor():
    def __init__(self, patch_shape, data_key='Rad', fov_radius=0.6):
        self.patch_shape = patch_shape
        self.data_key = data_key
        self.fov_radius = fov_radius
    def __call__(self, ds):
        assert ds['x'].shape[0] >= self.patch_shape[0], 'Invalid dataset shape: %s' % str(dataset[self.x].shape)
        assert ds['y'].shape[0] >= self.patch_shape[1], 'Invalid dataset shape: %s' % str(dataset[self.y].shape)

        # get x/y grid
        x_grid, y_grid = np.meshgrid(np.arange(0, ds.x.shape[0], 1), np.arange(0, ds.y.shape[0], 1))

        # create mask for valid coordinates within desired field of view
        # NOTE: This masks from the center to the image edge, rather than disk edge
        valid_mask = create_fov_mask(shape=(ds.x.shape[0], ds.y.shape[0]), fov_radius=self.fov_radius)

        # get coordinate pairs for valid points
        coords_on_disk = np.column_stack((x_grid[valid_mask], y_grid[valid_mask]))
        del x_grid, y_grid

        # pick random x/y index
        random_idx = np.random.randint(0, len(coords_on_disk))
        x, y = tuple(coords_on_disk[random_idx])
        del coords_on_disk
        # define patch boundaries
        xmin = x - self.patch_shape[0] // 2
        ymin = y - self.patch_shape[1] // 2
        xmax = x + self.patch_shape[0] // 2
        ymax = y + self.patch_shape[1] // 2

        # crop patch
        patch_ds = ds.sel({'x': slice(ds['x'][xmin], ds['x'][xmax - 1]),
                            'y': slice(ds['y'][ymin], ds['y'][ymax - 1])})
        return patch_ds, xmin, ymin

class RandomCropDatasetEditor():
    def __init__(self, patch_shape, x='x', y='y', data_key='Rad'):
        self.patch_shape = patch_shape
        self.x = x
        self.y = y
        self.data_key = data_key
    def __call__(self, ds):
        assert ds[self.x].shape[0] >= self.patch_shape[0], 'Invalid dataset shape: %s' % str(dataset[self.x].shape)
        assert ds[self.y].shape[0] >= self.patch_shape[1], 'Invalid dataset shape: %s' % str(dataset[self.y].shape)
        
        max_attempts = 20
        while True:
            # xmin = randint(0, ds[self.x].shape[0] - self.patch_shape[0])
            # ymin = randint(0, ds[self.y].shape[0] - self.patch_shape[1])
            xmin = randint(1200, 2400)
            ymin = randint(1200, 2400)
            patch_ds = ds.sel({self.x: slice(ds[self.x][xmin], ds[self.x][xmin + self.patch_shape[0] - 1]), # 0-based index
                                self.y: slice(ds[self.y][ymin], ds[self.y][ymin + self.patch_shape[1] - 1])}) # 0-based index
            if _patch_valid(patch_ds):
                break
            else:
                max_attempts -= 1
                if max_attempts == 0:
                    logger.info('Could not find valid coordinates in patch after 20 cropping attempts')
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
        assert len(source_order) == len(self.target_order), "Length of source and target wavelengths must match."
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
    def __init__(self, target_bands, key="data"):
        """
        Args:
            target_bands (list): List of bands to select
            key (str): Key in dictionary to apply transformation
        """
        self.target_bands = target_bands
        self.key = key

    def call(self, data_dict, **kwargs):
        source_bands = data_dict["wavelengths"]
        # Get indexes of bands to select
        indexes = [np.where(source_bands == wvl)[0][0] for wvl in self.target_bands]
        # Extract data
        data = data_dict[self.key]
        # Subselect bands
        data = data[indexes]
        assert data.shape[0] == len(self.target_bands)
        # Update dictionary
        data_dict[self.key] = data
        data_dict["wavelengths"] = np.array(self.target_bands)
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
    
class CoordNormEditor(Editor):
    """
    Normalize latitude and longitude coordinates
    """
    def __init__(self, key="coords"):
        self.key = key
    def call(self, data_dict, **kwargs):
        lats, lons = data_dict["coords"]
        # Normalize latitude and longitude to range [-1, 1]
        lats = lats/90
        lons = lons/180
        # Update dictionary
        data_dict["coords"] = np.stack([lats, lons], axis=0)
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
    
class StackDictEditor(Editor):
    """
    Stack data dictionary into a single array
    """
    def __init__(self, allowed_keys=["data", "cloud_mask", "nan_mask", "coords"], axis=0):
        self.allowed_keys = allowed_keys
        self.axis = axis
    def call(self, data_dict, **kwargs):
        # Select keys
        self.keys = [key for key in self.allowed_keys if key in data_dict.keys()]
        # Select data
        data = []
        for key in self.keys:
            values = data_dict[key]
            if len(values.shape) == 2:
                values = np.expand_dims(values, axis=self.axis)
            data.append(values)
        # Stack data
        data = np.concatenate(data, axis=self.axis)
        # Return numpy array
        return data
    
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

class MeanStdNormEditor_ds(Editor):
    """
    Normalise each band using the mean and std from a normalization dataset.
    """
    def __init__(self, norm_ds, key="data"):
        """
        Args:
            norm_ds (xarray.Dataset): Dataset with normalization values (mean and std)
            key (str): Key in dictionary to apply transformation
        """
        self.key = key
        self.norm = norm_ds

    def call(self, data_dict, **kwargs):
        data = data_dict[self.key]
        # use wavelengths and only normalise the bands that we have in the data
        data_wavelengths = data_dict["wavelengths"]
        # Get indeces of bands to select
        indeces = [np.where(self.norm.band_wavelength == wvl)[0][0] for wvl in data_wavelengths]
        
        # extract relevant means and stds
        means = self.norm['mean'][indeces].values
        stds = self.norm['std'][indeces].values

        # check that number of channels equals number of means & stds
        assert data.shape[0] == means.shape[0]
        assert data.shape[0] == stds.shape[0]

        # apply normalization
        data = (data - means[:, None, None]) / stds[:, None, None]
        
        # Update dictionary
        data_dict[self.key] = data
        return data_dict

class MeanStdNormEditor(Editor):
    """
    Normalises data to have zero mean and unit variance.
    """

    def __init__(self, norm_dict, key="data", band_info_key="wavelengths"):
        """
        Args:
            norm_dict (dict): Dictionary with mean and std for each band
            key (str): Key in dictionary to apply transformation
            band_info_key (str): Key in dictionary to get band information
        """
        self.band_info = norm_dict
        self.key = key
        self.band_info_key = band_info_key

    def call(self, data_dict, **kwargs):
        # get data to be normalised
        data = data_dict[self.key]  
        # get the mean and std for each band - type conversion needed as json keys and values are strings
        means = np.array(
            [
                float(self.band_info[key]["mean"])
                for key in data_dict[self.band_info_key]
            ]
        )
        stds = np.array(
            [
                float(self.band_info[key]["std"])
                for key in data_dict[self.band_info_key]
            ]
        )
        # normalise each band using mean and std
        data = (data - means[:, None, None]) / stds[:, None, None]
        # update dictionary
        data_dict[self.key] = data
        return data_dict

class MinMaxNormEditor(Editor):
    """
    Normalises data to have values between -1 and 1.
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
            [
                float(self.band_info[key]["min"])
                for key in data_dict[self.band_info_key]
            ]
        )
        maxs = np.array(
            [
                float(self.band_info[key]["max"])
                for key in data_dict[self.band_info_key]
            ]
        )
        # normalise each band using min and max
        data = (data - mins[:, None, None]) / (maxs - mins)[:, None, None]*2 - 1
        # update dictionary
        data_dict[self.key] = data
        return data_dict



