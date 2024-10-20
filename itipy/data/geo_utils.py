from typing import Optional, List, Union, Tuple
from omegaconf import DictConfig
from datetime import datetime
import pandas as pd
from loguru import logger
import glob, os
import numpy as np
import pandas as pd
import ast

import xarray as xr
from functools import partial


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
    
    
def get_split(files: List, 
              split_dict: DictConfig) -> Tuple[List, List]:
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
    condition = (df.date.dt.year.isin(split_dict["years"])) & \
                (df.date.dt.month.isin(split_dict["months"])) & \
                (df.date.dt.day.isin(split_dict["days"]))
        
    # Extract filenames based on conditions
    split_files = df[condition].files.tolist()

    # Check if files are allocated properly
    if len(split_files) == 0:
        raise ValueError("No files found. Check split specification.")
    
    return split_files


def get_split_norm(norm_df: pd.DataFrame, split_dict: DictConfig) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Split normalization statistics based on dataset specification.

    Args:
        norm_df (pd.DataFrame): A dataframe containing the normalization statistics.
        split_dict (DictConfig): A dictionary-like object containing the dataset specification.

    Returns:
        Tuple[List, List]: A tuple containing two lists: the training set and the validation set.
    """
    # Extract dates from filenames
    datetime_strs = [str(f) for f in norm_df['datetime'].values]
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
    condition = (df.date.dt.year.isin(split_dict["years"])) & \
                (df.date.dt.month.isin(split_dict["months"])) & \
                (df.date.dt.day.isin(split_dict["days"]))
        
    # Extract filenames based on conditions
    split_indexes = df[condition].indexes.tolist()

    # Check if files are allocated properly
    if len(split_indexes) == 0:
        raise ValueError("No files found for normalization. Check split specification.")
    
    return split_indexes

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
    dates = [datetime.strptime(filename.split("_")[0], "%Y%m%d%H%M%S") for filename in filenames]
    return dates

def get_list_filenames(data_path: str="./", ext: str="*"):
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
        corr_data = data[i] * 0.001 # to convert mW to W
        corr_data = corr_data * 10000 / wvl**2 # to convert cm^-1 to um
        corrected_data.append(corr_data)
    return np.stack(corrected_data, axis=0)

def get_dict_norm(norm_df, column):
    """
    Get a dictionary of normalization statistics from a DataFrame.
    """
    norm_df = norm_df.reset_index(drop=True)
    if column not in ['mean', 'std']:
        raise ValueError("Column must be either 'mean' or 'std'.")
    wavelengths = sorted(ast.literal_eval(norm_df['wavelengths'][0]))
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
        dict_means[wvl] = np.mean(means[wvl])
    return dict_means

def calculate_overall_std(means, stds):
    """
    Calculate the overall standard deviation from a list of means and standard deviations.
    """
    wavelengths = list(means.keys())
    dict_stds = {}
    for wvl in wavelengths:
        vars_wvl = [stds[wvl][i]**2 for i in range(len(stds[wvl]))]
        mean_var = np.mean(vars_wvl)
        var_means = np.std(means[wvl])**2
        dict_stds[wvl] = np.sqrt(mean_var + var_means)
    return dict_stds

def compile_norm_dict(mean_dict, std_dict):
    """
    Compiles the normalization statistics into a dictionary.
    """
    wavelengths = list(mean_dict.keys())
    norm_dict = {}
    for wvl in wavelengths:
        norm_dict[wvl] = {
            "mean": round(mean_dict[wvl], 6),
            "std": round(std_dict[wvl], 6)
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
    # Extract dictionary of means and stds
    means = get_dict_norm(split_df, 'mean')
    stds = get_dict_norm(split_df, 'std')
    # Calculate overall mean & std from list of means & stds
    overall_mean = calculate_overall_mean(means=means)
    overall_std = calculate_overall_std(means=means, stds=stds)
    # Compile json file
    norm_dict = compile_norm_dict(overall_mean, overall_std)
    return norm_dict

def spatial_mean(ds: xr.Dataset, spatial_variables: List[str]) -> xr.Dataset:
    return ds.mean(spatial_variables)


def normalize(
        files: List[str],
        temporal_variables: List[str]=["time"], 
        spatial_variables: List[str]=["x","y"], 
) -> xr.Dataset:
    
    preprocess = partial(spatial_mean, spatial_variables=spatial_variables)

    # calculate mean
    ds_mean = xr.open_mfdataset(files, preprocess=preprocess, combine="by_coords",  engine="netcdf4")

    ds_mean = ds_mean.mean(temporal_variables)

    def preprocess(ds: xr.Dataset):
        # calculate the std
        N = ds.x.size * ds.y.size
        ds = np.sqrt(((ds - ds_mean) ** 2).sum(['x','y']) / N)
        return ds
    
    ds_std = xr.open_mfdataset(files, preprocess=preprocess, combine="by_coords",  engine="netcdf4")

    ds_std = ds_std.mean(temporal_variables)

    ds_mean = ds_mean.rename({'Rad':'mean'})
    ds_std = ds_std.rename({'Rad':'std'})

    # Drop any variables that are not used (e.g. DQF for GOES)
    ds_mean = ds_mean.drop_vars([v for v in ds_mean.var() if v not in ['std', 'mean']])
    ds_std = ds_std.drop_vars([v for v in ds_std.var() if v not in ['std', 'mean']])

    ds = xr.combine_by_coords([ds_mean, ds_std])
    return ds

