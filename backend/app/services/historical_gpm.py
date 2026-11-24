
from pathlib import Path

import numpy as np
import xarray as xr


PROJECT_ROOT = Path(__file__).resolve().parents[3]

HISTORICAL_DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "gpm_imerg"
    / "historical_pilot_20200101.zarr"
)


def get_historical_gpm_data() -> dict:
    """Read the consolidated historical GPM precipitation dataset."""

    if not HISTORICAL_DATASET_PATH.exists():
        raise FileNotFoundError(
            "Historical GPM dataset not found."
        )

    dataset = xr.open_zarr(
        HISTORICAL_DATASET_PATH,
        consolidated=True,
    )

    try:
        if "precipitation" not in dataset:
            raise ValueError(
                "Historical precipitation variable is missing."
            )

        values = np.asarray(
            dataset["precipitation"].values,
            dtype=np.float64,
        )

        timestamps = [
            str(value)
            for value in dataset.time.values.astype(
                "datetime64[ns]"
            )
        ]

        latitude = dataset.latitude.values.tolist()
        longitude = dataset.longitude.values.tolist()

        if values.shape != (
            len(timestamps),
            len(latitude),
            len(longitude),
        ):
            raise ValueError(
                "Historical dataset dimensions are inconsistent."
            )

        valid_values = np.where(
            np.isfinite(values),
            values,
            np.nan,
        )

        time_series = []

        for index, timestamp in enumerate(timestamps):
            observation = values[index]

            valid = observation[np.isfinite(observation)]

            time_series.append({
                "timestamp": timestamp,
                "mean": (
                    float(valid.mean())
                    if valid.size else None
                ),
                "minimum": (
                    float(valid.min())
                    if valid.size else None
                ),
                "maximum": (
                    float(valid.max())
                    if valid.size else None
                ),
                "valid_cells": int(valid.size),
                "missing_cells": int(
                    observation.size - valid.size
                ),
            })

        safe_values = values.astype(object)
        safe_values[~np.isfinite(values)] = None

        return {
            "dataset": "GPM IMERG Final Half-Hourly V07",
            "source": "NASA GPM IMERG",
            "variable": "precipitation",
            "units": (
                dataset["precipitation"].attrs.get("units")
            ),
            "time_standard": "UTC",
            "spatial_resolution": "0.1 degree",
            "dimensions": {
                "time": len(timestamps),
                "latitude": len(latitude),
                "longitude": len(longitude),
            },
            "coordinates": {
                "latitude": latitude,
                "longitude": longitude,
                "time": timestamps,
            },
            "values": safe_values.tolist(),
            "time_series": time_series,
            "summary": {
                "total_observations": int(values.shape[0]),
                "total_grid_cells": int(
                    values.shape[1] * values.shape[2]
                ),
                "valid_measurements": int(
                    np.isfinite(values).sum()
                ),
                "missing_measurements": int(
                    np.isnan(values).sum()
                ),
            },
        }

    finally:
        dataset.close()
