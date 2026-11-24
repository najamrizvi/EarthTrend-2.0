
from pathlib import Path

import numpy as np
import xarray as xr


PROJECT_ROOT = Path(__file__).resolve().parents[3]

HISTORICAL_DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "gpm_imerg"
    / "historical_20200101_20200130.zarr"
)


def get_historical_gpm_expanded_data() -> dict:
    """Return the verified 30-day historical GPM precipitation dataset."""

    if not HISTORICAL_DATASET_PATH.exists():
        raise FileNotFoundError(
            "Expanded historical GPM dataset not found."
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

        selected = dataset["precipitation"]

        expected_dimensions = (
            "time",
            "latitude",
            "longitude",
        )

        if selected.dims != expected_dimensions:
            raise ValueError(
                "Unexpected historical dataset dimensions."
            )

        raw_values = np.asarray(
            selected.values,
            dtype=np.float64,
        )

        values = raw_values.astype(object)
        values[~np.isfinite(raw_values)] = None

        timestamps = [
            str(value)
            for value in dataset.time.values.astype(
                "datetime64[ns]"
            )
        ]

        time_bounds = None

        if "time_bounds" in dataset:
            time_bounds = [
                [
                    str(value)
                    for value in row.astype("datetime64[ns]")
                ]
                for row in dataset["time_bounds"].values
            ]

        latitude = dataset.latitude.values
        longitude = dataset.longitude.values

        valid_count = int(
            np.isfinite(raw_values).sum()
        )

        missing_count = int(
            (~np.isfinite(raw_values)).sum()
        )

        return {
            "dataset": {
                "name": dataset.attrs.get("title"),
                "source": dataset.attrs.get("source"),
                "collection": dataset.attrs.get(
                    "source_collection"
                ),
                "version": dataset.attrs.get(
                    "source_version"
                ),
                "spatial_resolution": dataset.attrs.get(
                    "spatial_resolution"
                ),
                "time_interval": dataset.attrs.get(
                    "time_interval"
                ),
                "time_standard": dataset.attrs.get(
                    "time_standard"
                ),
                "region": dataset.attrs.get("region"),
                "scientific_note": dataset.attrs.get(
                    "scientific_note"
                ),
            },
            "variable": "precipitation",
            "units": selected.attrs.get("units"),
            "dimensions": {
                "time": int(dataset.sizes["time"]),
                "latitude": int(dataset.sizes["latitude"]),
                "longitude": int(dataset.sizes["longitude"]),
            },
            "summary": {
                "total_observations": int(raw_values.size),
                "valid_observations": valid_count,
                "missing_observations": missing_count,
                "minimum": (
                    float(np.nanmin(raw_values))
                    if valid_count else None
                ),
                "maximum": (
                    float(np.nanmax(raw_values))
                    if valid_count else None
                ),
                "mean": (
                    float(np.nanmean(raw_values))
                    if valid_count else None
                ),
            },
            "coordinates": {
                "time": timestamps,
                "latitude": latitude.tolist(),
                "longitude": longitude.tolist(),
                "time_bounds": time_bounds,
            },
            "values": values.tolist(),
        }

    finally:
        dataset.close()
