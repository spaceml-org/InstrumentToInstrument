import ast
import glob
import os
from datetime import datetime
from functools import partial
from random import randint
from typing import List, Tuple

import numpy as np
import pandas as pd
import xarray as xr
from loguru import logger
from omegaconf import DictConfig

import rioxarray
import xarray as xr
from rasterio.enums import Resampling
from typing import Tuple

rioxarray_samplers = {
    "bilinear": Resampling.bilinear,
    "cubic": Resampling.cubic,
    "cubic_spline": Resampling.cubic_spline,
    "nearest": Resampling.nearest,
}

def resample_rioxarray(ds: xr.Dataset, resolution: Tuple[int, int], method: str="bilinear") -> xr.Dataset:
    """
    Resamples a raster dataset using rasterio-xarray.

    Parameters:
        ds (xr.Dataset): The input dataset to be resampled.
        resolution (int): The desired resolution of the resampled dataset. Default is 1_000.
        method (str): The resampling method to be used. Default is "bilinear".

    Returns:
        xr.Dataset: The resampled dataset.
    """

    ds = ds.rio.reproject(
        ds.rio.crs,
        resolution=resolution,
        resample=rioxarray_samplers[method], 
    )
    return ds

def convert_coordinates(ds: xr.Dataset, satellite_type: str) -> xr.Dataset:
    """
    Convert satellite coordinates from radians to meters for geostationary projections.
    
    Parameters:
        ds (xr.Dataset): Input dataset with coordinates in radians
        satellite_type (str): Type of satellite ("goes", "himawari", "msg")
        
    Returns:
        xr.Dataset: Dataset with corrected coordinates in meters
    """
    # Satellite heights in meters
    satellite_heights = {
        "goes": 35786023,      # GOES-16/17
        "himawari": 35785863,  # Himawari-8/9  
        "msg": 35785831        # MSG/SEVIRI
    }
    
    if satellite_type.lower() not in satellite_heights:
        raise ValueError(f"Unknown satellite type: {satellite_type}")
    
    satellite_height = satellite_heights[satellite_type.lower()]
    
    # Check if coordinates are in radians
    x_units = ds.x.attrs.get('units', '')
    y_units = ds.y.attrs.get('units', '')
    
    if x_units == 'rad' and y_units == 'rad':
        # print(f"Converting {satellite_type.upper()} coordinates from radians to meters...")
        
        # Convert coordinates
        x_meters = ds.x.values * satellite_height
        y_meters = ds.y.values * satellite_height
        
        # Update dataset
        ds_corrected = ds.assign_coords(x=x_meters, y=y_meters)
        ds_corrected.x.attrs['units'] = 'm'
        ds_corrected.y.attrs['units'] = 'm'
        
        # print(f"Original resolution: {ds.rio.resolution()}")
        # print(f"Corrected resolution: {ds_corrected.rio.resolution()}")
        # print(f"Resolution in km: {abs(ds_corrected.rio.resolution()[0]/1000):.1f} km")
        
        return ds_corrected
    else:
        # print("Coordinates are already in proper units, no conversion needed.")
        return ds


def _check_any_constant_channels(data: np.array) -> bool:
    """
    Check if any channel in the data is constant.
    """
    return np.any(np.nanstd(data, axis=(1, 2)) == 0)


def _check_all_constant_channels(data: np.array) -> bool:
    """
    Check if all channels in the data are constant.
    """
    return np.all(np.nanstd(data, axis=(1, 2)) == 0)


def split_train_val(files: List, split_spec: DictConfig) -> Tuple[List, List]:
    """
    Split files into training and validation sets based on dataset specification.

    Args:
        files (List): A list of files to be split.
        split_spec (DictConfig): A dictionary-like object containing the dataset specification.

    Returns:
        Tuple[List, List]: A tuple containing two lists: the training set and the validation set.
    """
    if "train" not in split_spec.keys() or "val" not in split_spec.keys():
        raise ValueError("split_spec must contain 'train' and 'val' keys")

    train_files = get_split(files, split_spec["train"])
    val_files = get_split(files, split_spec["val"])

    return train_files, val_files


def get_split(files: List, split_dict: DictConfig) -> Tuple[List, List]:
    """
    Split files based on dataset specification.

    Args:
        files (List): A list of files to be split.
        split_dict (DictConfig): A dictionary-like object containing the dataset specification.

    Returns:
        Tuple[List, List]: A tuple containing two lists: the training set and the validation set.
    """
    # Extract dates from filenames
    filenames = [file.split("/")[-1] for file in files]
    dates = get_dates_from_files(filenames)
    # Convert to dataframe for easier manipulation
    df = pd.DataFrame({"filename": filenames, "files": files, "date": dates})

    # Check if years, months, and days are specified
    if "years" not in split_dict.keys() or split_dict["years"] is None:
        logger.info("No years specified for split. Using all years.")
        split_dict["years"] = df.date.dt.year.unique().tolist()
    if "months" not in split_dict.keys() or split_dict["months"] is None:
        logger.info("No months specified for split. Using all months.")
        split_dict["months"] = df.date.dt.month.unique().tolist()
    if "days" not in split_dict.keys() or split_dict["days"] is None:
        logger.info("No days specified for split. Using all days.")
        split_dict["days"] = df.date.dt.day.unique().tolist()

    # Determine conditions specified split
    condition = (
        (df.date.dt.year.isin(split_dict["years"]))
        & (df.date.dt.month.isin(split_dict["months"]))
        & (df.date.dt.day.isin(split_dict["days"]))
    )

    # Extract filenames based on conditions
    split_files = df[condition].files.tolist()

    # Check if files are allocated properly
    if len(split_files) == 0:
        raise ValueError("No files found. Check split specification.")

    return split_files


def get_split_norm(
    norm_df: pd.DataFrame, split_dict: DictConfig
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Split normalization statistics based on dataset specification.

    Args:
        norm_df (pd.DataFrame): A dataframe containing the normalization statistics.
        split_dict (DictConfig): A dictionary-like object containing the dataset specification.

    Returns:
        Tuple[List, List]: A tuple containing two lists: the training set and the validation set.
    """
    # Extract dates from filenames
    datetime_strs = [str(f) for f in norm_df["datetime"].values]
    indexes = norm_df.index.values
    dates = get_dates_from_files(datetime_strs)
    # Convert to dataframe for easier manipulation
    df = pd.DataFrame({"indexes": indexes, "date": dates})

    # Check if years, months, and days are specified
    if "years" not in split_dict.keys() or split_dict["years"] is None:
        logger.info("No years specified for split. Using all years.")
        split_dict["years"] = df.date.dt.year.unique().tolist()
    if "months" not in split_dict.keys() or split_dict["months"] is None:
        logger.info("No months specified for split. Using all months.")
        split_dict["months"] = df.date.dt.month.unique().tolist()
    if "days" not in split_dict.keys() or split_dict["days"] is None:
        logger.info("No days specified for split. Using all days.")
        split_dict["days"] = df.date.dt.day.unique().tolist()

    # Determine conditions specified split
    condition = (
        (df.date.dt.year.isin(split_dict["years"]))
        & (df.date.dt.month.isin(split_dict["months"]))
        & (df.date.dt.day.isin(split_dict["days"]))
    )

    # Extract filenames based on conditions
    split_indexes = df[condition].indexes.tolist()

    # Check if files are allocated properly
    if len(split_indexes) == 0:
        raise ValueError("No files found for normalization. Check split specification.")

    return split_indexes


def parse_time(data_filename: str):
    """
    Parse the timestep from the given data filename.

    Args:
        data_filename (str): The filename of the data.

    Returns:
        numpy.ndarray: An array containing the year, month, day, hour, and minute of the timestep.

    """
    filename = data_filename.split("/")[-1]
    filename_bits = filename.split("_")
    datetime_str = filename_bits[0]

    datetime_obj = datetime.strptime(datetime_str, "%Y%m%d%H%M%S")
    fraction_of_year = np.clip(int(datetime_obj.strftime("%j")) / 365, 0, 1)
    fraction_of_day = np.clip(
        datetime_obj.hour / 24
        + datetime_obj.minute / 24 / 60
        + datetime_obj.second / 24 / 60 / 60,
        0,
        1,
    )
    return np.array(
        [
            int(datetime_obj.year),
            int(datetime_obj.month),
            int(datetime_obj.day),
            int(datetime_obj.hour),
            int(datetime_obj.minute),
            int(datetime_obj.second),
            fraction_of_year,
            fraction_of_day,
        ]
    )


def convert_to_datetime(time: np.array):
    """
    Function to convert an array to a datetime object.
    Time is structured as [YYYY, MM, DD, HH, MM, SS]
    """

    time_dt = datetime(
        year=int(time[0]),
        month=int(time[1]),
        day=int(time[2]),
        hour=int(time[3]),
        minute=int(time[4]),
        second=int(time[5]),
    )

    return time_dt


def get_date_from_file(filename: str) -> datetime:
    """
    Extract date from filename.

    Args:
        filenames (List[str]): A list of filenames.

    Returns:
        List[str]: A list of dates extracted from the filenames.
    """
    date = datetime.strptime(filename.split("_")[0], "%Y%m%d%H%M%S")
    return date


def get_dates_from_files(filenames: List[str]) -> List[datetime]:
    """
    Extract dates from a list of filenames.

    Args:
        filenames (List[str]): A list of filenames.

    Returns:
        List[str]: A list of dates extracted from the filenames.
    """
    dates = [
        datetime.strptime(filename.split("_")[0], "%Y%m%d%H%M%S")
        for filename in filenames
    ]
    return dates


def get_list_filenames(data_path: str = "./", ext: str = "*"):
    """
    Loads a list of file names within a directory.

    Args:
        data_path (str, optional): The directory path to search for files. Defaults to "./".
        ext (str, optional): The file extension to filter the search. Defaults to "*".

    Returns:
        List[str]: A sorted list of file names matching the given extension within the directory.
    """
    pattern = f"*{ext}"
    return sorted(glob.glob(os.path.join(data_path, "**", pattern), recursive=True))


def get_files(datasets_spec: DictConfig, ext=".nc"):
    """
    Get a list of filenames based on the provided datasets specification.

    Args:
        datasets_spec (DictConfig): The datasets specification containing the path and extension.
        ext (str, optional): The file extension to filter the search. Defaults to ".nc".

    Returns:
        List[str]: A list of filenames.

    """
    data_path = datasets_spec.data_path
    return get_list_filenames(data_path=data_path, ext=ext)


def filter_files_by_metric(files, stats_df, satellite, metric_column, threshold):
    """
    Filter files based on a metric threshold for a specific satellite.
    Args:
        files (List[str]): List of file paths to filter.
        stats_df (pd.DataFrame): DataFrame containing statistics with columns 'file', 'sensor', and the metric column.
        satellite (str): The satellite name to filter by (e.g., 'GOES', 'HIMAWARI').
        metric_column (str): The name of the metric column in stats_df to apply the threshold on.
        threshold (float): The threshold value for filtering.
    Returns:
        List[str]: Filtered list of file paths that meet the metric threshold.
    """
    
    # Filter stats in one operation
    stats_subset = (stats_df
                   .query(f'sensor == "{satellite}" and {metric_column} >= {threshold}')
                   .reset_index(drop=True))
    
    logger.info(f"Filtering files for satellite {satellite} using metric '{metric_column}' with threshold {threshold}")
    
    # Convert to set for O(1) lookup instead of O(n) for each file
    valid_files = set(stats_subset['file'].values)
    
    # Use list comprehension with set lookup (much faster than checking pandas Series)
    filtered_files = [file for file in files 
                     if os.path.basename(file) in valid_files]
    
    logger.info(f"{len(filtered_files)} remain after applying threshold.")
    
    return filtered_files


def convert_units(data: np.array, wavelengths: np.array) -> np.array:
    """
    Function to convert units from mW/m^2/sr/cm^-1 to W/m^2/sr/um in numpy array.
    Acts on each band separately.

    Parameters:
        data (np.array): The input data to be converted.
        wavelengths (np.array): The wavelengths of the input data.

    Returns:
        np.array: The converted data.
    """
    assert len(data) == len(wavelengths)
    corrected_data = []
    for i, wvl in enumerate(wavelengths):
        corr_data = data[i] * 0.001  # to convert mW to W
        corr_data = corr_data * 10000 / wvl**2  # to convert cm^-1 to um
        corrected_data.append(corr_data)
    return np.stack(corrected_data, axis=0)


def get_dict_norm(norm_df, column):
    """
    Get a dictionary of normalization statistics from a DataFrame.
    """
    norm_df = norm_df.reset_index(drop=True)
    if column not in ["mean", "std", "min", "max"]:
        raise ValueError("Column must be either 'mean', 'std', 'min' or 'max'.")
    wavelengths = ast.literal_eval(
        norm_df["wavelengths"][0]
    )  # No sorting to preserve order
    wavelengths = [round(wvl, 2) for wvl in wavelengths]

    dict_norm = {}
    for i, wvl in enumerate(wavelengths):
        values = [ast.literal_eval(norm_df[column][x])[i] for x in range(len(norm_df))]
        dict_norm[wvl] = values
    return dict_norm


def calculate_overall_mean(means):
    """
    Calculate the overall mean of list of means.
    """
    wavelengths = list(means.keys())
    dict_means = {}
    for wvl in wavelengths:
        dict_means[wvl] = np.nanmean(means[wvl])
    return dict_means


def calculate_overall_std(means, stds):
    """
    Calculate the overall standard deviation from a list of means and standard deviations.
    """
    wavelengths = list(means.keys())
    dict_stds = {}
    for wvl in wavelengths:
        vars_wvl = [stds[wvl][i] ** 2 for i in range(len(stds[wvl]))]
        mean_var = np.nanmean(vars_wvl)
        var_means = np.nanstd(means[wvl]) ** 2
        dict_stds[wvl] = np.sqrt(mean_var + var_means)
    return dict_stds


def calculate_overall_min(mins):
    """
    Calculate the overall minimum from a list of minimums.
    """
    wavelengths = list(mins.keys())
    dict_mins = {}
    for wvl in wavelengths:
        dict_mins[wvl] = np.nanmin(mins[wvl])
    return dict_mins


def calculate_overall_max(maxs):
    """
    Calculate the overall maximum from a list of maximums.
    """
    wavelengths = list(maxs.keys())
    dict_maxs = {}
    for wvl in wavelengths:
        dict_maxs[wvl] = np.nanmax(maxs[wvl])
    return dict_maxs


def compile_norm_dict(mean_dict, std_dict, min_dict, max_dict):
    """
    Compiles the normalization statistics into a dictionary.
    """
    wavelengths = list(mean_dict.keys())
    norm_dict = {}
    for wvl in wavelengths:
        norm_dict[wvl] = {
            "mean": round(mean_dict[wvl], 6),
            "std": round(std_dict[wvl], 6),
            "min": round(min_dict[wvl], 6),
            "max": round(max_dict[wvl], 6),
        }
    return norm_dict


def calculate_norm_from_metrics(file, split_dict):
    """
    Function to calculate the normalization statistics from a given file of summary statistics.
    File should contain the following columns: 'datetime', 'wavelengths', 'mean', 'std'.

    Args:
        file (str): The file containing the summary statistics.
        split_dict (DictConfig): The dataset specification for splitting the data.

    Returns:
        dict: A dictionary containing the normalization statistics.
    """
    # Read csv file
    df = pd.read_csv(file)
    # Extract indexes for specified split
    split_idx = get_split_norm(df, split_dict)
    # Extract relevant entries in df
    split_df = df.loc[split_idx]
    # Extract dictionary of means, stds, mins, and maxs
    means = get_dict_norm(split_df, "mean")
    stds = get_dict_norm(split_df, "std")
    maxs = get_dict_norm(split_df, "max")
    mins = get_dict_norm(split_df, "min")
    # Calculate overall mean & std from list of means & stds
    overall_mean = calculate_overall_mean(means=means)
    overall_std = calculate_overall_std(means=means, stds=stds)
    # Get absolute min and max
    overall_min = calculate_overall_min(mins=mins)
    overall_max = calculate_overall_max(maxs=maxs)
    # Compile json file
    norm_dict = compile_norm_dict(overall_mean, overall_std, overall_min, overall_max)
    return norm_dict


def spatial_mean(ds: xr.Dataset, spatial_variables: List[str]) -> xr.Dataset:
    return ds.mean(spatial_variables)


def normalize(
    files: List[str],
    temporal_variables: List[str] = ["time"],
    spatial_variables: List[str] = ["x", "y"],
) -> xr.Dataset:
    preprocess = partial(spatial_mean, spatial_variables=spatial_variables)

    # calculate mean
    ds_mean = xr.open_mfdataset(
        files, preprocess=preprocess, combine="by_coords", engine="netcdf4"
    )

    ds_mean = ds_mean.mean(temporal_variables)

    def preprocess(ds: xr.Dataset):
        # calculate the std
        N = ds.x.size * ds.y.size
        ds = np.sqrt(((ds - ds_mean) ** 2).sum(["x", "y"]) / N)
        return ds

    ds_std = xr.open_mfdataset(
        files, preprocess=preprocess, combine="by_coords", engine="netcdf4"
    )

    ds_std = ds_std.mean(temporal_variables)

    ds_mean = ds_mean.rename({"Rad": "mean"})
    ds_std = ds_std.rename({"Rad": "std"})

    # Drop any variables that are not used (e.g. DQF for GOES)
    ds_mean = ds_mean.drop_vars([v for v in ds_mean.var() if v not in ["std", "mean"]])
    ds_std = ds_std.drop_vars([v for v in ds_std.var() if v not in ["std", "mean"]])

    ds = xr.combine_by_coords([ds_mean, ds_std])
    return ds


def unnormalize(norm_dict, bands, data):
    """
    Unnormalize the data using the provided normalization dictionary.
    """
    for i, band in enumerate(bands):
        if len(data.shape) == 3:
            data[i] = (data[i] + 1) * 0.5 * (
                norm_dict[band]["max"] - norm_dict[band]["min"]
            ) + norm_dict[band]["min"]
        elif len(data.shape) == 4:
            data[:, i] = (data[:, i] + 1) * 0.5 * (
                norm_dict[band]["max"] - norm_dict[band]["min"]
            ) + norm_dict[band]["min"]
    return data


def get_satellite_viewing_angles(
    lat: np.ndarray,
    lon: np.ndarray,
    sat_lat: float,
    sat_lon: float,
    sat_alt: float,  # in km
) -> tuple[np.ndarray, np.ndarray]:
    """Calculate satellite zenith and azimuth angles.

    Satellite zenith angle measures the angle from vertical that an observation
    is made at the surface. 0 means that the satellite is directly overhead. 90
    means that the surface point is on the horizon of the satellite view.

    Satellite azimuth angle measures the angle from North from the surface point
    to the satellite, measured clockwise. 0 is due N, 90 is E, 180 is S and 270
    is W.

    Parameters
    ----------
    lat : np.ndarray
        latitudes of surface point in degrees
    lon : np.ndarray
        longitudes of surface point in degrees
    sat_lat : float, optional
        latitude of sub-satellite point in degrees, by default 0
    sat_lon : float, optional
        longitude of sub-satellite point in degrees, by default 0
    sat_alt : float, optional
        altitude of satellite in km, by default 35_793 (geostationary orbit
        height over average earth radius)

    Returns
    -------
    tuple[float, float]
        satellite zenith and azimuth angles in degrees
    """
    # TODO test for inf / nan coordinates
    # Approximate spherical Earth so use radius of 6,371 km
    Re = 6_371
    Rgeo = sat_alt + Re

    # Caclulate the beta angle
    cos_beta = np.cos(np.radians(lat - sat_lat)) * np.cos(np.radians(lon - sat_lon))
    sin_beta = np.sin(np.arccos(cos_beta))

    # Calculate satellite zenith angle
    geo_dist = (
        Rgeo**2 + Re**2 - 2 * Rgeo * Re * cos_beta
    ) ** 0.5  # distance from surface to satellite
    sin_theta = (Rgeo * sin_beta) / geo_dist
    zenith_angle = np.degrees(np.arcsin(sin_theta))

    # Find where satellite-surface path intersects the earth and make these > 90
    zenith_angle = np.where(
        geo_dist**2 < (Rgeo**2 - Re**2), zenith_angle, 180 - zenith_angle
    )

    # Calculate satellite azimuthal angle
    x_sat = np.cos(np.radians(lat - sat_lat)) * np.sin(np.radians(lon - sat_lon))
    y_sat = np.sin(np.radians(lat - sat_lat))
    azimuth_angle = np.where(
        np.isfinite(x_sat), np.degrees(np.arctan2(x_sat, y_sat)) % 360, np.nan
    )

    return zenith_angle, azimuth_angle


def get_sza_and_azi(
    date: datetime, lat: np.ndarray, lon: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """Get the solar zenith angle at a specific time/lat/lon

    Parameters
    ----------
    date : datetime | array of datetime like
        Dates of the points
    lat : np.ndarray
        Latitudes
    lon : np.ndarray
        Longitudes

    Returns
    -------
    sza: np.ndarray
        The solar zenith angle in degrees, where 0 is directly above, 90 is on
        the horizon and 180 is directly below
    saa: np.ndarray
        The solar azimuth angle in degrees, clockwise from North
    """
    # TODO test for inf / nan coordinates
    try:
        date = pd.DatetimeIndex(date)
    except TypeError:
        date = pd.DatetimeIndex([date])
    day_of_year = date.dayofyear.to_numpy()
    hour_of_day = (date.hour + date.minute / 60 + date.second / 60 / 60).to_numpy()

    # calculate approx time equation as angle for 365 day year
    equation_of_time_approx = 2.0 * np.pi * day_of_year / 365.0

    # calculate the solar declination for the given day
    # the declination varies due to the fact that the earth rotation axis
    # is not perpendicular to the ecliptic plane
    solar_declination = (
        0.006918
        - 0.399912 * np.cos(equation_of_time_approx)
        - 0.006758 * np.cos(2.0 * equation_of_time_approx)
        - 0.002697 * np.cos(3.0 * equation_of_time_approx)
        + 0.070257 * np.sin(equation_of_time_approx)
        + 0.000907 * np.sin(2.0 * equation_of_time_approx)
        + 0.001480 * np.sin(3.0 * equation_of_time_approx)
    )

    # equation of time, used to compensate for the earth's elliptical orbit
    # around the sun and its axial tilt when calculating solar time
    # eqt is the correction in hours
    equation_of_time = 2.0 * np.pi * day_of_year / 366.0
    equation_of_time = (
        0.0072 * np.cos(equation_of_time)
        - 0.0528 * np.cos(2.0 * equation_of_time)
        - 0.0012 * np.cos(3.0 * equation_of_time)
        - 0.1229 * np.sin(equation_of_time)
        - 0.1565 * np.sin(2.0 * equation_of_time)
        - 0.0041 * np.sin(3.0 * equation_of_time)
    )

    # calculate the solar zenith angle
    omega = np.radians(
        (360.0 / 24.0) * (hour_of_day + lon / 15.0 + equation_of_time - 12.0)
    )
    sunh = np.sin(solar_declination) * np.sin(np.radians(lat)) + np.cos(
        solar_declination
    ) * np.cos(np.radians(lat)) * np.cos(omega)

    solar_elevation = np.arcsin(np.clip(sunh, -1, 1))
    solar_zenith_angle = np.pi / 2.0 - solar_elevation

    azimuth = (
        np.sin(solar_declination) * np.cos(np.radians(lat))
        - np.cos(solar_declination) * np.sin(np.radians(lat)) * np.cos(omega)
    ) / np.cos(np.pi / 2.0 - solar_zenith_angle)

    solar_azimuth_angle = np.arccos(np.clip(azimuth, -1, 1))

    return np.degrees(solar_zenith_angle), np.degrees(solar_azimuth_angle)


class CropDataset:
    def __init__(
        self,
        patch_size: tuple[int, int],
        center_crop: bool = False,
        radius: int = 0,  # Defined in pixels
    ):
        self.patch_size = patch_size
        self.center_crop = center_crop
        self.radius = radius

    def __call__(
        self,
        ds,
    ):
        if self.center_crop:
            # crop around the center of the image, randomly within radius if desired
            central_idxx = ds.sizes["x"] // 2
            central_idxy = ds.sizes["y"] // 2

            central_x = randint(central_idxx - self.radius, central_idxx + self.radius)
            central_y = randint(central_idxy - self.radius, central_idxy + self.radius)

        else:
            # crop randomly
            central_x = randint(
                self.patch_size[0] // 2, ds.sizes["x"] - self.patch_size[0] // 2
            )
            central_y = randint(
                self.patch_size[1] // 2, ds.sizes["y"] - self.patch_size[1] // 2
            )

        ds = ds.isel(
            x=slice(
                central_x - self.patch_size[0] // 2, central_x + self.patch_size[0] // 2
            ),
            y=slice(
                central_y - self.patch_size[1] // 2, central_y + self.patch_size[1] // 2
            ),
        )
        return ds
