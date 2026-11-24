
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
    / "historical_pilot_20200101"
)

EXPECTED_COUNT = 48
EXPECTED_UNITS = "mm/hr"
EXPECTED_LATITUDES = np.array([-0.05, 0.05])
EXPECTED_LONGITUDES = np.array([-0.05, 0.05])

FILENAME_PATTERN = re.compile(
    r"GPM_20200101_(\d{6})_precipitation\.nc4"
)


def decode(value):
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value)



def parse_header(header, key):
    pattern = rf"(?:^|[;\r\n])\s*{re.escape(key)}\s*=\s*([^;\r\n]+)"

    match = re.search(pattern, header)

    if not match:
        raise ValueError(
            f"Missing metadata field: {key}"
        )

    return match.group(1).strip()



def expected_times():
    return [
        datetime(
            2020, 1, 1, hour, minute,
            tzinfo=timezone.utc,
        )
        for hour in range(24)
        for minute in (0, 30)
    ]


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
                raise ValueError(
                    f"Missing Grid/{name}"
                )

        header = decode(
            dataset.attrs["FileHeader"]
        )

        source_start_text = parse_header(
            header,
            "StartGranuleDateTime",
        )

        source_stop_text = parse_header(
            header,
            "StopGranuleDateTime",
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
            + timedelta(minutes=29, seconds=59, milliseconds=999)
        )

        if source_stop != expected_stop:
            raise ValueError(
                f"Wrong source stop: {source_stop}"
            )

        latitude = np.asarray(grid["lat"][:])
        longitude = np.asarray(grid["lon"][:])

        if not np.allclose(
            latitude,
            EXPECTED_LATITUDES,
            atol=1e-5,
        ):
            raise ValueError(
                f"Unexpected latitude coordinates: {latitude}"
            )

        if not np.allclose(
            longitude,
            EXPECTED_LONGITUDES,
            atol=1e-5,
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
            raise ValueError(
                f"Unexpected units: {units}"
            )

        bounds = np.asarray(grid["time_bnds"][:])
        time_values = np.asarray(grid["time"][:])

        if bounds.shape != (1, 2):
            raise ValueError(
                f"Unexpected time bounds shape: {bounds.shape}"
            )

        if time_values.shape != (1,):
            raise ValueError(
                f"Unexpected time coordinate shape: {time_values.shape}"
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
            raise ValueError(
                "Internal time-bound start does not match "
                "the expected observation."
            )

        if actual_end - actual_start != 1800:
            raise ValueError(
                "Time bounds do not span exactly 30 minutes."
            )

        if not actual_start <= actual_time <= actual_end:
            raise ValueError(
                "Internal time coordinate falls outside its bounds."
            )

        values = np.asarray(
            precipitation[:],
            dtype=np.float64,
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
                "Negative precipitation value detected."
            )

        return {
            "timestamp": source_start.isoformat(),
            "valid_cells": int(valid_values.size),
            "missing_cells": int(missing_mask.sum()),
            "minimum": (
                float(valid_values.min())
                if valid_values.size else None
            ),
            "maximum": (
                float(valid_values.max())
                if valid_values.size else None
            ),
            "mean": (
                float(valid_values.mean())
                if valid_values.size else None
            ),
        }


print("=" * 72)
print("EARTHTREND 2.0 - COMPLETE HISTORICAL PILOT VALIDATION")
print("=" * 72)

if not DATA_DIR.is_dir():
    raise FileNotFoundError(
        f"Pilot directory not found: {DATA_DIR}"
    )

files = sorted(DATA_DIR.glob("*.nc4"))

if len(files) != EXPECTED_COUNT:
    raise RuntimeError(
        f"Expected {EXPECTED_COUNT} files; found {len(files)}."
    )

expected = expected_times()

results = []
total_valid = 0
total_missing = 0

for index, (path, expected_start) in enumerate(
    zip(files, expected),
    start=1,
):
    match = FILENAME_PATTERN.fullmatch(path.name)

    if not match:
        raise RuntimeError(
            f"Unexpected filename: {path.name}"
        )

    filename_time = datetime.strptime(
        match.group(1),
        "%H%M%S",
    ).time()

    if (
        filename_time.hour != expected_start.hour
        or filename_time.minute != expected_start.minute
        or filename_time.second != 0
    ):
        raise RuntimeError(
            f"Filename timestamp mismatch: {path.name}"
        )

    result = validate_file(path, expected_start)

    results.append(result)
    total_valid += result["valid_cells"]
    total_missing += result["missing_cells"]

    print(
        f"{index:02d}/48 PASS | "
        f"{expected_start.strftime('%H:%M')} UTC | "
        f"Valid: {result['valid_cells']}/4 | "
        f"Missing: {result['missing_cells']}/4"
    )


print("\n" + "=" * 72)
print("VALIDATION SUMMARY")
print("=" * 72)

print("Files checked:", len(results))
print("Timestamp sequence: PASS")
print("Source granule metadata: PASS")
print("Latitude coordinates: PASS")
print("Longitude coordinates: PASS")
print("Precipitation dimensions: PASS")
print("Units:", EXPECTED_UNITS)
print("Half-hour time bounds: PASS")

print("\nTotal grid-cell observations:", len(results) * 4)
print("Valid grid-cell observations:", total_valid)
print("Missing grid-cell observations:", total_missing)

if total_valid + total_missing != EXPECTED_COUNT * 4:
    raise RuntimeError(
        "Grid-cell accounting does not match expectations."
    )

if total_valid:
    valid_results = [
        item for item in results
        if item["valid_cells"] > 0
    ]

    print(
        "Lowest file-level minimum:",
        min(item["minimum"] for item in valid_results),
    )

    print(
        "Highest file-level maximum:",
        max(item["maximum"] for item in valid_results),
    )

print("\nFULL PILOT VALIDATION: PASS")
