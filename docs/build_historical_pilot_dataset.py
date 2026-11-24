
from pathlib import Path

import h5py
import numpy as np
import xarray as xr


PROJECT = Path(
    r"C:\Users\Administrator\Documents\EarthTrend-2.0"
)

SOURCE_DIR = (
    PROJECT
    / "data"
    / "processed"
    / "gpm_imerg"
    / "historical_pilot_20200101"
)

OUTPUT_PATH = (
    PROJECT
    / "data"
    / "processed"
    / "gpm_imerg"
    / "historical_pilot_20200101.zarr"
)

EXPECTED_FILES = 48

EPOCH = np.datetime64("1980-01-06T00:00:00", "s")


def read_observation(path):
    with h5py.File(path, "r") as source:
        grid = source["Grid"]

        latitude = np.asarray(grid["lat"][:], dtype=np.float32)
        longitude = np.asarray(grid["lon"][:], dtype=np.float32)

        precipitation = grid["precipitation"]

        values = np.asarray(
            precipitation[0],
            dtype=np.float32,
        )

        fill_value = float(
            np.asarray(
                precipitation.attrs["_FillValue"]
            ).reshape(-1)[0]
        )

        # NASA stores precipitation as (longitude, latitude).
        # EarthTrend uses (latitude, longitude).
        values = values.T.copy()

        values[
            ~np.isfinite(values)
            | np.isclose(values, fill_value)
        ] = np.nan

        time_seconds = int(grid["time"][0])

        bounds_seconds = np.asarray(
            grid["time_bnds"][0],
            dtype=np.int64,
        )

        timestamp = (
            EPOCH + np.timedelta64(time_seconds, "s")
        )

        time_bounds = (
            EPOCH
            + bounds_seconds.astype("timedelta64[s]")
        )

        return (
            latitude,
            longitude,
            timestamp,
            time_bounds,
            values,
        )


def main():
    print("=" * 68)
    print("EARTHTREND 2.0 - HISTORICAL DATASET BUILDER")
    print("=" * 68)

    if not SOURCE_DIR.is_dir():
        raise FileNotFoundError(
            f"Source directory not found: {SOURCE_DIR}"
        )

    if OUTPUT_PATH.exists():
        raise FileExistsError(
            "Output already exists. Refusing to overwrite: "
            f"{OUTPUT_PATH}"
        )

    files = sorted(SOURCE_DIR.glob("*.nc4"))

    if len(files) != EXPECTED_FILES:
        raise RuntimeError(
            f"Expected {EXPECTED_FILES} files, found {len(files)}."
        )

    observations = [
        read_observation(path)
        for path in files
    ]

    reference_latitude = observations[0][0]
    reference_longitude = observations[0][1]

    for index, observation in enumerate(observations, start=1):
        latitude, longitude = observation[:2]

        if not np.array_equal(
            latitude, reference_latitude
        ):
            raise ValueError(
                f"Latitude grid changed at observation {index}."
            )

        if not np.array_equal(
            longitude, reference_longitude
        ):
            raise ValueError(
                f"Longitude grid changed at observation {index}."
            )

    times = np.array(
        [item[2] for item in observations],
        dtype="datetime64[ns]",
    )

    bounds = np.array(
        [item[3] for item in observations],
        dtype="datetime64[ns]",
    )

    precipitation_values = np.stack(
        [item[4] for item in observations],
        axis=0,
    )

    if precipitation_values.shape != (48, 2, 2):
        raise ValueError(
            "Unexpected consolidated array shape: "
            f"{precipitation_values.shape}"
        )

    differences = np.diff(times)

    if not np.all(
        differences == np.timedelta64(30, "m")
    ):
        raise ValueError(
            "Historical timestamps are not continuous."
        )

    if not np.all(
        bounds[:, 1] - bounds[:, 0]
        == np.timedelta64(30, "m")
    ):
        raise ValueError(
            "One or more time bounds are not 30 minutes."
        )

    valid_count = int(
        np.isfinite(precipitation_values).sum()
    )

    missing_count = int(
        np.isnan(precipitation_values).sum()
    )

    dataset = xr.Dataset(
        data_vars={
            "precipitation": (
                ("time", "latitude", "longitude"),
                precipitation_values,
                {
                    "long_name": (
                        "GPM IMERG precipitation estimate"
                    ),
                    "units": "mm/hr",
                    "source_variable": "Grid/precipitation",
                    "missing_value": "NaN; source fill value -9999.9",
                },
            ),
            "time_bounds": (
                ("time", "bounds"),
                bounds,
            ),
        },
        coords={
            "time": times,
            "latitude": (
                "latitude",
                reference_latitude,
                {
                    "units": "degrees_north",
                    "standard_name": "latitude",
                },
            ),
            "longitude": (
                "longitude",
                reference_longitude,
                {
                    "units": "degrees_east",
                    "standard_name": "longitude",
                },
            ),
            "bounds": [0, 1],
        },
        attrs={
            "title": (
                "EarthTrend Historical GPM IMERG Pilot"
            ),
            "source": "NASA GPM IMERG Final Half-Hourly V07",
            "source_collection": "GPM_3IMERGHH",
            "source_version": "V07B",
            "variable": "precipitation",
            "spatial_resolution": "0.1 degree",
            "time_interval": "30 minutes",
            "time_standard": "UTC",
            "region": (
                "Latitude -0.06 to 0.06; "
                "longitude -0.06 to 0.06"
            ),
            "source_observations": EXPECTED_FILES,
            "valid_grid_cell_observations": valid_count,
            "missing_grid_cell_observations": missing_count,
            "scientific_note": (
                "Single-day, four-cell regional pilot. "
                "Not a global dataset."
            ),
        },
    )

    dataset.time.attrs["bounds"] = "time_bounds"
    dataset.time.attrs["standard_name"] = "time"
    dataset.time.attrs["time_standard"] = "UTC"

    print("\nDataset prepared.")
    print("Dimensions:", dict(dataset.sizes))
    print("Valid observations:", valid_count)
    print("Missing observations:", missing_count)

    print("\nWriting separate Zarr dataset...")

    dataset.to_zarr(
        OUTPUT_PATH,
        mode="w",
        consolidated=True,
        zarr_format=2,
    )

    print("Reopening dataset for verification...")

    reopened = xr.open_zarr(
        OUTPUT_PATH,
        consolidated=True,
    )

    try:
        if dict(reopened.sizes) != {
            "time": 48,
            "latitude": 2,
            "longitude": 2,
            "bounds": 2,
        }:
            raise RuntimeError(
                f"Unexpected saved dimensions: {dict(reopened.sizes)}"
            )

        if "precipitation" not in reopened:
            raise RuntimeError(
                "Precipitation variable missing after saving."
            )

        saved_values = reopened["precipitation"].values

        if not np.allclose(
            saved_values,
            precipitation_values,
            equal_nan=True,
        ):
            raise RuntimeError(
                "Saved precipitation values do not match source data."
            )

        if not np.array_equal(
            reopened.time.values,
            times,
        ):
            raise RuntimeError(
                "Saved timestamps do not match source timestamps."
            )

        print("\nSaved dataset verification: PASS")
        print("Precipitation shape:", saved_values.shape)
        print("Time range:", str(reopened.time.values[0]), "to", str(reopened.time.values[-1]))
        print("Units:", reopened.precipitation.attrs["units"])
        print("Output:", OUTPUT_PATH)

    finally:
        reopened.close()
        dataset.close()

    print("\nHISTORICAL DATASET BUILD: PASS")


if __name__ == "__main__":
    main()
