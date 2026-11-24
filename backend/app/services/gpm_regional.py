import numpy as np
import xarray as xr

from app.services.gpm_catalog import DATASET_PATH


SUPPORTED_VARIABLES = {
    "precipitation",
    "precipitation_quality_index",
    "random_error",
}

MAX_REGION_CELLS = 10_000


def get_regional_gpm_data(
    variable: str,
    min_latitude: float,
    max_latitude: float,
    min_longitude: float,
    max_longitude: float,
    time_index: int = 0,
) -> dict:
    """Read a bounded geographic subset from the processed GPM Zarr dataset."""

    if variable not in SUPPORTED_VARIABLES:
        raise ValueError("Unsupported GPM variable.")

    if not (-90 <= min_latitude < max_latitude <= 90):
        raise ValueError("Invalid latitude range.")

    if not (-180 <= min_longitude < max_longitude <= 180):
        raise ValueError("Invalid longitude range.")

    if time_index not in (0, 1):
        raise ValueError("Invalid time index for the sample dataset.")

    if not DATASET_PATH.exists():
        raise FileNotFoundError("Processed GPM dataset not found.")

    dataset = xr.open_zarr(DATASET_PATH, consolidated=None)

    try:
        selected = dataset[variable].isel(time=time_index).sel(
            latitude=slice(min_latitude, max_latitude),
            longitude=slice(min_longitude, max_longitude),
        )

        latitude = selected.latitude.values
        longitude = selected.longitude.values

        rows = len(latitude)
        columns = len(longitude)
        cell_count = rows * columns

        if cell_count == 0:
            raise ValueError(
                "The requested region contains no grid cells."
            )

        if cell_count > MAX_REGION_CELLS:
            raise ValueError(
                f"Region exceeds the {MAX_REGION_CELLS}-cell limit."
            )

        values = np.asarray(selected.values)
        values = values.astype(object)
        values[~np.isfinite(np.asarray(selected.values))] = None

        timestamp = dataset.time.values[time_index]
        timestamp_text = str(
            timestamp.astype("datetime64[ns]")
        )

        return {
            "dataset": "GPM IMERG Final Half-Hourly V07",
            "variable": variable,
            "units": (
                selected.attrs.get("Units")
                or selected.attrs.get("units")
            ),
            "timestamp": timestamp_text,
            "time_standard": "UTC",
            "spatial_resolution": "0.1 degree",
            "shape": {
                "latitude": rows,
                "longitude": columns,
                "total_cells": cell_count,
            },
            "coordinates": {
                "latitude": latitude.tolist(),
                "longitude": longitude.tolist(),
            },
            "values": values.tolist(),
        }

    finally:
        dataset.close()
