from pathlib import Path

import xarray as xr


PROJECT_ROOT = Path(__file__).resolve().parents[3]

DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "gpm_imerg"
    / "gpm_imerg_sample_20200101_0000_0100_metadata_v4.zarr"
)


def get_gpm_dataset_metadata() -> dict:
    """Return metadata without loading the full scientific arrays."""

    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Processed GPM dataset not found: {DATASET_PATH}"
        )

    dataset = xr.open_zarr(DATASET_PATH, consolidated=None)

    try:
        times = [
            str(value)
            for value in dataset.time.values.astype("datetime64[ns]")
        ]

        return {
            "dataset": {
                "name": "GPM IMERG Final Half-Hourly",
                "collection": dataset.attrs.get(
                    "collection_short_name"
                ),
                "version": dataset.attrs.get(
                    "collection_version"
                ),
                "source": dataset.attrs.get("source"),
                "spatial_resolution": dataset.attrs.get(
                    "spatial_resolution"
                ),
                "time_interval": dataset.attrs.get("time_interval"),
                "time_standard": dataset.attrs.get("time_standard"),
            },
            "dimensions": {
                name: int(size)
                for name, size in dataset.sizes.items()
            },
            "variables": list(dataset.data_vars),
            "coordinates": {
                "latitude": {
                    "minimum": float(dataset.latitude.min().values),
                    "maximum": float(dataset.latitude.max().values),
                    "count": int(dataset.sizes["latitude"]),
                },
                "longitude": {
                    "minimum": float(dataset.longitude.min().values),
                    "maximum": float(dataset.longitude.max().values),
                    "count": int(dataset.sizes["longitude"]),
                },
                "time": times,
            },
            "attributes": {
                str(key): str(value)
                for key, value in dataset.attrs.items()
            },
        }

    finally:
        dataset.close()
