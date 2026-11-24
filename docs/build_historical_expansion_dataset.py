
import re
from datetime import datetime, timedelta, timezone
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
    / "historical_20200101_20200130_raw"
)

OUTPUT_PATH = (
    PROJECT
    / "data"
    / "processed"
    / "gpm_imerg"
    / "historical_20200101_20200130.zarr"
)

EXPECTED_FILES = 1440
EXPECTED_SHAPE = (1440, 2, 2)

START_DATE = datetime(
    2020, 1, 1, tzinfo=timezone.utc
)

EPOCH = np.datetime64("1980-01-06T00:00:00", "s")

FILENAME_PATTERN = re.compile(
    r"GPM_(\d{8})_(\d{6})_precipitation\.nc4"
)


def expected_times():
    result = []
    current = START_DATE

    for _ in range(EXPECTED_FILES):
        result.append(current)
        current += timedelta(minutes=30)

    return result


def read_observation(path):

    with h5py.File(path, "r") as source:

        grid = source["Grid"]

        latitude = np.asarray(
            grid["lat"][:],
            dtype=np.float32,
        )

        longitude = np.asarray(
            grid["lon"][:],
            dtype=np.float32,
        )

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

        # NASA stores (longitude, latitude).
        # EarthTrend stores (latitude, longitude).
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

    print("=" * 72)
    print("EARTHTREND 2.0 - 30-DAY HISTORICAL ZARR BUILDER")
    print("=" * 72)

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

    expected = expected_times()

    observations = []

    print("\nReading and checking source observations...")

    for index, (path, expected_start) in enumerate(
        zip(files, expected),
        start=1,
    ):

        match = FILENAME_PATTERN.fullmatch(path.name)

        if not match:
            raise RuntimeError(
                f"Unexpected filename: {path.name}"
            )

        filename_timestamp = datetime.strptime(
            match.group(1) + match.group(2),
            "%Y%m%d%H%M%S",
        ).replace(tzinfo=timezone.utc)

        if filename_timestamp != expected_start:
            raise RuntimeError(
                f"Filename sequence mismatch: {path.name}"
            )

        observation = read_observation(path)

        latitude, longitude, timestamp, bounds, values = (
            observation
        )

        if values.shape != (2, 2):
            raise ValueError(
                f"Unexpected grid shape in {path.name}: "
                f"{values.shape}"
            )

        if index == 1:
            reference_latitude = latitude.copy()
            reference_longitude = longitude.copy()

        else:
            if not np.array_equal(
                latitude, reference_latitude
            ):
                raise ValueError(
                    f"Latitude grid changed at {path.name}"
                )

            if not np.array_equal(
                longitude, reference_longitude
            ):
                raise ValueError(
                    f"Longitude grid changed at {path.name}"
                )

        observations.append(observation)

        if index % 240 == 0:
            print(
                f"Read: {index}/{EXPECTED_FILES} observations"
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

    if precipitation_values.shape != EXPECTED_SHAPE:
        raise ValueError(
            "Unexpected consolidated array shape: "
            f"{precipitation_values.shape}"
        )

    if not np.all(
        np.diff(times) == np.timedelta64(30, "m")
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

    if not np.all(
        (times >= bounds[:, 0])
        & (times <= bounds[:, 1])
    ):
        raise ValueError(
            "One or more time coordinates fall outside their bounds."
        )

    valid_count = int(
        np.isfinite(precipitation_values).sum()
    )

    missing_count = int(
        np.isnan(precipitation_values).sum()
    )

    if valid_count + missing_count != EXPECTED_FILES * 4:
        raise RuntimeError(
            "Grid-cell accounting does not match expectations."
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
                    "missing_value": (
                        "NaN; source fill value -9999.9"
                    ),
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
                "EarthTrend 30-Day Historical GPM IMERG Dataset"
            ),
            "source": (
                "NASA GPM IMERG Final Half-Hourly V07B"
            ),
            "source_collection": "GPM_3IMERGHH",
            "source_version": "V07B",
            "variable": "precipitation",
            "spatial_resolution": "0.1 degree",
            "time_interval": "30 minutes",
            "time_standard": "UTC",
            "period_start": "2020-01-01",
            "period_end": "2020-01-30",
            "region": (
                "Latitude -0.06 to 0.06; "
                "longitude -0.06 to 0.06"
            ),
            "source_observations": EXPECTED_FILES,
            "grid_cells_per_observation": 4,
            "valid_grid_cell_observations": valid_count,
            "missing_grid_cell_observations": missing_count,
            "scientific_note": (
                "Thirty-day, four-cell regional dataset. "
                "Not a global dataset."
            ),
        },
    )

    dataset.time.attrs["bounds"] = "time_bounds"
    dataset.time.attrs["standard_name"] = "time"
    dataset.time.attrs["time_standard"] = "UTC"

    print("\nDataset prepared.")
    print("Dimensions:", dict(dataset.sizes))
    print("Valid grid-cell observations:", valid_count)
    print("Missing grid-cell observations:", missing_count)

    print("\nWriting separate Zarr dataset...")

    dataset.to_zarr(
        OUTPUT_PATH,
        mode="w",
        consolidated=True,
        zarr_format=2,
    )

    print("Reopening saved dataset for verification...")

    reopened = xr.open_zarr(
        OUTPUT_PATH,
        consolidated=True,
    )

    try:

        expected_dimensions = {
            "time": 1440,
            "latitude": 2,
            "longitude": 2,
            "bounds": 2,
        }

        if dict(reopened.sizes) != expected_dimensions:
            raise RuntimeError(
                "Unexpected saved dimensions: "
                f"{dict(reopened.sizes)}"
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

        if not np.array_equal(
            reopened["time_bounds"].values,
            bounds,
        ):
            raise RuntimeError(
                "Saved time bounds do not match source time bounds."
            )

        if not np.array_equal(
            reopened.latitude.values,
            reference_latitude,
        ):
            raise RuntimeError(
                "Saved latitude coordinates do not match."
            )

        if not np.array_equal(
            reopened.longitude.values,
            reference_longitude,
        ):
            raise RuntimeError(
                "Saved longitude coordinates do not match."
            )

        print("\nSaved dataset verification: PASS")
        print("Precipitation shape:", saved_values.shape)
        print("Time range:",
              str(reopened.time.values[0]),
              "to",
              str(reopened.time.values[-1]))
        print("Units:", reopened.precipitation.attrs["units"])
        print("Valid grid-cell observations:", valid_count)
        print("Missing grid-cell observations:", missing_count)
        print("Output:", OUTPUT_PATH)

    finally:
        reopened.close()
        dataset.close()

    print("\nHISTORICAL EXPANSION DATASET BUILD: PASS")


if __name__ == "__main__":
    main()
