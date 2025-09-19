from __future__ import annotations

import autoroot  # required for imports from src
import numpy as np
import xarray as xr

from itipy.data.geo_utils import (
    CropDataset,
    convert_to_datetime,
    get_satellite_viewing_angles,
    get_sza_and_azi,
    parse_time,
)
from itipy.data.goes.utils import GOES_WAVELENGTHS


def scale_reflectance(data_dict):
    """
    Scale the reflectance data to the range [0, 100].
    """
    for i, band_name in enumerate(data_dict["band_names"]):
        if "Reflectance" in data_dict["sensor_info"][band_name]["band_type"]:
            # Scale reflectance data to [0, 100] range
            data_dict["data"][i] = data_dict["data"][i] * 100
    return data_dict


def load_goes_file(
    file: str,
    load_zenith: bool = True,
    load_solar: bool = True,
    patch_size: list
    | None = None,  # Whether to crop the data to a smaller patch size (e.g. [128, 128] for pre-training
    center_crop: bool = False,  # If True, will crop to the center of the image
    radius: int = 0,  # Radius for cropping, if center_crop is True
):
    if not file.endswith(".nc"):
        raise NotImplementedError("Unsupported file format.")

    # define an empty dictionary
    data_dict = {}
    # open file
    with xr.open_dataset(file) as ds:
        if patch_size is not None:
            crop_ds = CropDataset(
                patch_size=patch_size,
                center_crop=center_crop,  # If True, will crop to the center of the image
                radius=radius,
            )
            ds = crop_ds(ds)

        # extract data
        if "data" in ds.data_vars:
            data_dict["data"] = ds.data.values.astype(np.float32)
        else:
            data_dict["data"] = (
                ds[list(GOES_WAVELENGTHS.keys())].to_array().values.astype(np.float32)
            )

        # extract coordinates
        # calculate latitude and longitude coordinates
        # Fix lat/lon encoding bug
        if "latitude" in ds.data_vars and "longitude" in ds.data_vars:
            lat_offset = (
                (
                    ds.latitude.encoding["scale_factor"]
                    + ds.latitude.encoding["add_offset"]
                )
                * 2
                if ds.latitude.encoding["add_offset"] > 0
                else 0
            )
            lon_offset = (
                (
                    ds.longitude.encoding["scale_factor"]
                    + ds.longitude.encoding["add_offset"]
                )
                * 2
                if ds.longitude.encoding["add_offset"] > 0
                else 0
            )
            latitudes = (ds.latitude - lat_offset).fillna(
                ds.latitude.encoding["add_offset"]
            )
            longitudes = (ds.longitude - lon_offset).fillna(
                ds.longitude.encoding["add_offset"]
            )

            data_dict["coords"] = np.stack(
                [latitudes.values, longitudes.values], axis=0
            )
        else:
            data_dict["coords"] = np.stack([*get_abi_lat_lon(ds)], axis=0)

        # get time from file name
        data_dict["time"] = parse_time(file)

        # add band names and wavelengths
        data_dict["band_names"] = list(GOES_WAVELENGTHS.keys())
        data_dict["wavelengths"] = [
            val.get("center_wavelength") for val in GOES_WAVELENGTHS.values()
        ]
        data_dict["sensor_info"] = GOES_WAVELENGTHS

        if "data" not in ds.data_vars:
            # Scale reflectance data to [0, 100] range
            data_dict = scale_reflectance(data_dict)

        # calculate the zenith angle
        if load_zenith:
            if "sat_angle" in ds.data_vars:
                data_dict["sat_angle"] = ds.sat_angle.values
            else:
                zenith, azimuth = get_satellite_viewing_angles(
                    lat=data_dict["coords"][0],
                    lon=data_dict["coords"][1],
                    sat_lat=ds.goes_imager_projection.latitude_of_projection_origin,
                    sat_lon=ds.goes_imager_projection.longitude_of_projection_origin,
                    sat_alt=ds.goes_imager_projection.perspective_point_height
                    / 1e3,  # convert to km
                )
                data_dict["sat_angle"] = np.stack([zenith, azimuth], axis=0)
        if load_solar:
            if "solar_angle" in ds.data_vars:
                data_dict["solar_angle"] = ds.solar_angle.values
            else:
                time = convert_to_datetime(data_dict["time"])
                zenith, azimuth = get_sza_and_azi(
                    date=time, lat=data_dict["coords"][0], lon=data_dict["coords"][1]
                )
                data_dict["solar_angle"] = np.stack([zenith, azimuth], axis=0)

    return data_dict
