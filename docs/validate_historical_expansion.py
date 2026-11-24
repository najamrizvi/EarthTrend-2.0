
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

import h5py
import numpy as np


PROJECT = Path(
    r"C:\Users\Administrator\Documents\EarthTrend-2.0"
)

DATA_DIR = (
    PROJECT
    / "data"
    / "processed"
    / "gpm_imerg"
    / "historical_20200101_20200130_raw"
)

START_DATE = datetime(2020, 1, 1, tzinfo=timezone.utc)
END_DATE = datetime(2020, 1, 31, tzinfo=timezone.utc)

EXPECTED_COUNT = 1440
EXPECTED_UNITS = "mm/hr"

EXPECTED_LATITUDES = np.array([-0.05, 0.05])
EXPECTED_LONGITUDES = np.array([-0.05, 0.05])

FILENAME_PATTERN = re.compile(
    r"GPM_(\d{8})_(\d{6})_precipitation\.nc4"
)


def decode(value):
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value)


def parse_header(header, key):
    pattern = (
        rf"(?:^|[;\r\n])\s*{re.escape(key)}\s*=\s*([^;\r\n]+)"
    )

    match = re.search(pattern, header)

    if not match:
        raise ValueError(f"Missing metadata field: {key}")

    return match.group(1).strip()


def expected_times():
    timestamps = []
    current = START_DATE

    while current < END_DATE:
        timestamps.append(current)
        current += timedelta(minutes=30)

    return timestamps


def validate_file(path, expected_start):

    with h5py.File(path, "r") as dataset:

        if "Grid" not in dataset:
            raise ValueError("Grid group missing")

        grid = dataset["Grid"]

        required = [
            "lat",
            "lon",
            "time",
            "time_bnds",
            "precipitation",
        ]

        for name in required:
            if name not in grid:
                raise ValueError(f"Missing Grid/{name}")

        if "FileHeader" not in dataset.attrs:
            raise ValueError("FileHeader metadata missing")

        header = decode(dataset.attrs["FileHeader"])

        source_start_text = parse_header(
            header, "StartGranuleDateTime"
        )

        source_stop_text = parse_header(
            header, "StopGranuleDateTime"
        )

        source_start = datetime.fromisoformat(
            source_start_text.replace("Z", "+00:00")
        )

        source_stop = datetime.fromisoformat(
            source_stop_text.replace("Z", "+00:00")
        )

        if source_start != expected_start:
            raise ValueError(
                f"Wrong source start: {source_start}"
            )

        expected_stop = (
            expected_start
            + timedelta(
                minutes=29,
                seconds=59,
                milliseconds=999,
            )
        )

        if source_stop != expected_stop:
            raise ValueError(
                f"Wrong source stop: {source_stop}"
            )

        latitude = np.asarray(grid["lat"][:])
        longitude = np.asarray(grid["lon"][:])

        if not np.allclose(
            latitude, EXPECTED_LATITUDES, atol=1e-5
        ):
            raise ValueError(
                f"Unexpected latitude coordinates: {latitude}"
            )

        if not np.allclose(
            longitude, EXPECTED_LONGITUDES, atol=1e-5
        ):
            raise ValueError(
                f"Unexpected longitude coordinates: {longitude}"
            )

        precipitation = grid["precipitation"]

        if precipitation.shape != (1, 2, 2):
            raise ValueError(
                f"Unexpected precipitation shape: "
                f"{precipitation.shape}"
            )

        units = decode(
            precipitation.attrs.get(
                "Units",
                precipitation.attrs.get("units", ""),
            )
        )

        if units != EXPECTED_UNITS:
            raise ValueError(f"Unexpected units: {units}")

        bounds = np.asarray(grid["time_bnds"][:])
        time_values = np.asarray(grid["time"][:])

        if bounds.shape != (1, 2):
            raise ValueError(
                f"Unexpected time bounds shape: {bounds.shape}"
            )

        if time_values.shape != (1,):
            raise ValueError(
                f"Unexpected time coordinate shape: "
                f"{time_values.shape}"
            )

        epoch = datetime(
            1980, 1, 6, tzinfo=timezone.utc
        )

        expected_seconds = int(
            (expected_start - epoch).total_seconds()
        )

        actual_start = int(bounds[0, 0])
        actual_end = int(bounds[0, 1])
        actual_time = int(time_values[0])

        if actual_start != expected_seconds:
            raise ValueError("Time-bound start mismatch")

        if actual_end - actual_start != 1800:
            raise ValueError(
                "Time bounds do not span exactly 30 minutes"
            )

        if not actual_start <= actual_time <= actual_end:
            raise ValueError(
                "Time coordinate falls outside its bounds"
            )

        values = np.asarray(
            precipitation[:], dtype=np.float64
        )

        if "_FillValue" not in precipitation.attrs:
            raise ValueError(
                "Precipitation fill-value metadata missing"
            )

        fill_value = float(
            np.asarray(
                precipitation.attrs["_FillValue"]
            ).reshape(-1)[0]
        )

        missing_mask = (
            ~np.isfinite(values)
            | np.isclose(values, fill_value)
        )

        valid_values = values[~missing_mask]

        if np.any(valid_values < 0):
            raise ValueError(
                "Negative precipitation value detected"
            )

        return {
            "valid": int(valid_values.size),
            "missing": int(missing_mask.sum()),
            "minimum": (
                float(valid_values.min())
                if valid_values.size else None
            ),
            "maximum": (
                float(valid_values.max())
                if valid_values.size else None
            ),
        }


def main():

    print("=" * 72)
    print("EARTHTREND 2.0 - 30-DAY HISTORICAL VALIDATION")
    print("=" * 72)

    if not DATA_DIR.is_dir():
        raise FileNotFoundError(
            f"Historical directory not found: {DATA_DIR}"
        )

    files = sorted(DATA_DIR.glob("*.nc4"))
    expected = expected_times()

    if len(expected) != EXPECTED_COUNT:
        raise RuntimeError(
            f"Expected timestamp configuration error: {len(expected)}"
        )

    if len(files) != EXPECTED_COUNT:
        raise RuntimeError(
            f"Expected {EXPECTED_COUNT} files; found {len(files)}"
        )

    files_by_timestamp = {}

    for path in files:

        match = FILENAME_PATTERN.fullmatch(path.name)

        if not match:
            raise RuntimeError(
                f"Unexpected filename: {path.name}"
            )

        timestamp_text = (
            match.group(1) + match.group(2)
        )

        timestamp = datetime.strptime(
            timestamp_text, "%Y%m%d%H%M%S"
        ).replace(tzinfo=timezone.utc)

        if timestamp in files_by_timestamp:
            raise RuntimeError(
                f"Duplicate timestamp: {timestamp}"
            )

        files_by_timestamp[timestamp] = path

    expected_set = set(expected)
    actual_set = set(files_by_timestamp)

    missing_timestamps = sorted(expected_set - actual_set)
    unexpected_timestamps = sorted(actual_set - expected_set)

    if missing_timestamps:
        raise RuntimeError(
            f"Missing timestamps: {missing_timestamps[:10]}"
        )

    if unexpected_timestamps:
        raise RuntimeError(
            f"Unexpected timestamps: {unexpected_timestamps[:10]}"
        )

    total_valid = 0
    total_missing = 0
    file_minima = []
    file_maxima = []

    for index, timestamp in enumerate(expected, start=1):

        path = files_by_timestamp[timestamp]

        result = validate_file(path, timestamp)

        total_valid += result["valid"]
        total_missing += result["missing"]

        if result["minimum"] is not None:
            file_minima.append(result["minimum"])
            file_maxima.append(result["maximum"])

        if index % 48 == 0:
            day = index // 48

            print(
                f"Day {day:02d}/30 PASS | "
                f"Observations: {index}/1440 | "
                f"Valid cells: {total_valid} | "
                f"Missing cells: {total_missing}"
            )

    print("\n" + "=" * 72)
    print("VALIDATION SUMMARY")
    print("=" * 72)

    print("Files checked:", len(files))
    print("Expected observations:", EXPECTED_COUNT)
    print("Unique timestamps:", len(files_by_timestamp))
    print("Timestamp continuity: PASS")
    print("Missing timestamps: 0")
    print("Duplicate timestamps: 0")
    print("Unexpected timestamps: 0")
    print("Source granule metadata: PASS")
    print("Latitude coordinates: PASS")
    print("Longitude coordinates: PASS")
    print("Precipitation dimensions: PASS")
    print("Units:", EXPECTED_UNITS)
    print("Half-hour time bounds: PASS")
    print("Negative precipitation values: NONE")

    print("\nTotal grid-cell observations:", EXPECTED_COUNT * 4)
    print("Valid grid-cell observations:", total_valid)
    print("Missing grid-cell observations:", total_missing)

    if total_valid + total_missing != EXPECTED_COUNT * 4:
        raise RuntimeError(
            "Grid-cell accounting does not match expectations"
        )

    if file_minima:
        print("Lowest file-level minimum:", min(file_minima))
        print("Highest file-level maximum:", max(file_maxima))

    print("\nFULL HISTORICAL EXPANSION VALIDATION: PASS")


if __name__ == "__main__":
    main()
