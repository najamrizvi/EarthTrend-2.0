
import re
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path

import earthaccess
import h5py
import numpy as np


PROJECT = Path(
    r"C:\Users\Administrator\Documents\EarthTrend-2.0"
)

PILOT_DIR = (
    PROJECT / "data" / "processed" / "gpm_imerg"
    / "historical_pilot_20200101"
)

OUTPUT_DIR = (
    PROJECT / "data" / "processed" / "gpm_imerg"
    / "historical_20200101_20200130_raw"
)

ENDPOINT = (
    "https://harmony.earthdata.nasa.gov/"
    "GPM_3IMERGHH/ogc-api-coverages/1.0.0/"
    "collections/parameter_vars/coverage/rangeset"
)

START_DATE = "2020-01-01"

# Initial test: retrieve January 2 only.
# After this passes, change to "2020-01-30".
END_DATE = "2020-01-30"

MIN_LATITUDE = -0.06
MAX_LATITUDE = 0.06
MIN_LONGITUDE = -0.06
MAX_LONGITUDE = 0.06

EXPECTED_LATITUDES = np.array([-0.05, 0.05])
EXPECTED_LONGITUDES = np.array([-0.05, 0.05])

VARIABLE = "Grid/precipitation"
EXPECTED_UNITS = "mm/hr"
EPOCH = datetime(1980, 1, 6, tzinfo=timezone.utc)


def expected_starts(day):
    return [
        datetime(
            day.year, day.month, day.day,
            hour, minute, tzinfo=timezone.utc
        )
        for hour in range(24)
        for minute in (0, 30)
    ]


def filename_for(timestamp):
    return (
        f"GPM_{timestamp:%Y%m%d}_"
        f"{timestamp:%H%M%S}_precipitation.nc4"
    )


def granule_filename(granule):
    return granule["umm"]["GranuleUR"].split(":", 1)[-1]


def validate_file(path, expected_start):
    if not path.is_file() or path.stat().st_size < 8:
        raise ValueError(f"Missing or empty file: {path}")

    with h5py.File(path, "r") as source:
        if "Grid" not in source:
            raise ValueError(f"Grid group missing: {path.name}")

        grid = source["Grid"]

        required = [
            "lat", "lon", "time", "time_bnds",
            "precipitation",
        ]

        for name in required:
            if name not in grid:
                raise ValueError(
                    f"Missing Grid/{name}: {path.name}"
                )

        header = source.attrs["FileHeader"]

        if isinstance(header, bytes):
            header = header.decode(
                "utf-8", errors="replace"
            )
        else:
            header = str(header)

        def header_value(key):
            match = re.search(
                rf"(?:^|[;\r\n])\s*{re.escape(key)}"
                rf"\s*=\s*([^;\r\n]+)",
                header,
            )
            if not match:
                raise ValueError(
                    f"Missing header field {key}: {path.name}"
                )
            return match.group(1).strip()

        source_start = datetime.fromisoformat(
            header_value("StartGranuleDateTime").replace(
                "Z", "+00:00"
            )
        )

        source_stop = datetime.fromisoformat(
            header_value("StopGranuleDateTime").replace(
                "Z", "+00:00"
            )
        )

        if source_start != expected_start:
            raise ValueError(
                f"Wrong source start in {path.name}: "
                f"{source_start}"
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
                f"Wrong source stop in {path.name}: "
                f"{source_stop}"
            )

        latitude = np.asarray(grid["lat"][:])
        longitude = np.asarray(grid["lon"][:])

        if not np.allclose(
            latitude, EXPECTED_LATITUDES, atol=1e-5
        ):
            raise ValueError(
                f"Unexpected latitude grid: {path.name}"
            )

        if not np.allclose(
            longitude, EXPECTED_LONGITUDES, atol=1e-5
        ):
            raise ValueError(
                f"Unexpected longitude grid: {path.name}"
            )

        precipitation = grid["precipitation"]

        if precipitation.shape != (1, 2, 2):
            raise ValueError(
                f"Unexpected precipitation shape: "
                f"{precipitation.shape}"
            )

        units = precipitation.attrs.get(
            "Units",
            precipitation.attrs.get("units", ""),
        )

        if isinstance(units, bytes):
            units = units.decode("utf-8", errors="replace")

        if str(units) != EXPECTED_UNITS:
            raise ValueError(
                f"Unexpected precipitation units: {units}"
            )

        bounds = np.asarray(grid["time_bnds"][:])
        times = np.asarray(grid["time"][:])

        if bounds.shape != (1, 2) or times.shape != (1,):
            raise ValueError(
                f"Unexpected time dimensions: {path.name}"
            )

        expected_seconds = int(
            (expected_start - EPOCH).total_seconds()
        )

        actual_start = int(bounds[0, 0])
        actual_end = int(bounds[0, 1])
        actual_time = int(times[0])

        if actual_start != expected_seconds:
            raise ValueError(
                f"Time-bound start mismatch: {path.name}"
            )

        if actual_end - actual_start != 1800:
            raise ValueError(
                f"Time bounds are not 30 minutes: {path.name}"
            )

        if not actual_start <= actual_time <= actual_end:
            raise ValueError(
                f"Time coordinate outside bounds: {path.name}"
            )

        values = np.asarray(
            precipitation[:], dtype=np.float64
        )

        fill_value = float(
            np.asarray(
                precipitation.attrs["_FillValue"]
            ).reshape(-1)[0]
        )

        missing = (
            ~np.isfinite(values)
            | np.isclose(values, fill_value)
        )

        valid_values = values[~missing]

        if np.any(valid_values < 0):
            raise ValueError(
                f"Negative precipitation: {path.name}"
            )

        return {
            "valid": int(valid_values.size),
            "missing": int(missing.sum()),
        }


def main():
    start_day = datetime.strptime(
        START_DATE, "%Y-%m-%d"
    ).date()

    end_day = datetime.strptime(
        END_DATE, "%Y-%m-%d"
    ).date()

    if end_day < start_day:
        raise ValueError("END_DATE precedes START_DATE.")

    if not PILOT_DIR.is_dir():
        raise FileNotFoundError(PILOT_DIR)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 68)
    print("EARTHTREND - HISTORICAL EXPANSION")
    print("=" * 68)
    print("Period:", START_DATE, "through", END_DATE)
    print("Region:", MIN_LATITUDE, MAX_LATITUDE,
          MIN_LONGITUDE, MAX_LONGITUDE)
    print("Output:", OUTPUT_DIR)

    # Preserve and reuse the already validated January 1 files.
    print("\nChecking original January 1 pilot...")

    for timestamp in expected_starts(start_day):
        source_path = PILOT_DIR / filename_for(timestamp)
        target_path = OUTPUT_DIR / filename_for(timestamp)

        if not source_path.is_file():
            raise FileNotFoundError(source_path)

        validate_file(source_path, timestamp)

        if not target_path.exists():
            shutil.copy2(source_path, target_path)

        validate_file(target_path, timestamp)

    print("January 1 pilot reuse: PASS (48/48)")

    print("\nAuthenticating with NASA Earthdata...")

    auth = earthaccess.login(strategy="interactive")

    if not auth or not getattr(auth, "authenticated", False):
        raise RuntimeError("NASA Earthdata authentication failed.")

    session = earthaccess.get_requests_https_session()

    total_validated = 48

    current_day = start_day + timedelta(days=1)

    while current_day <= end_day:
        date_text = current_day.strftime("%Y%m%d")

        print("\nSearching granules for", current_day)

        pattern = re.compile(
            rf"3B-HHR\.MS\.MRG\.3IMERG\.{date_text}"
            rf"-S(\d{{6}})-E\d{{6}}\.\d{{4}}\.V07B\.HDF5$"
        )

        granules = earthaccess.search_data(
            short_name="GPM_3IMERGHH",
            version="07",
            temporal=(
                f"{current_day.isoformat()}T00:00:00",
                f"{current_day.isoformat()}T23:59:59",
            ),
            count=200,
        )

        matched = {}

        for granule in granules:
            name = granule_filename(granule)
            match = pattern.fullmatch(name)

            if match:
                matched[match.group(1)] = name

        starts = expected_starts(current_day)

        expected_keys = {
            timestamp.strftime("%H%M%S")
            for timestamp in starts
        }

        if set(matched) != expected_keys:
            missing = sorted(expected_keys - set(matched))
            unexpected = sorted(set(matched) - expected_keys)

            raise RuntimeError(
                f"Incomplete granule sequence for {current_day}. "
                f"Missing: {missing}; unexpected: {unexpected}"
            )

        print("Granule sequence: PASS (48/48)")

        for index, timestamp in enumerate(starts, start=1):
            output_path = OUTPUT_DIR / filename_for(timestamp)

            if output_path.exists():
                validate_file(output_path, timestamp)
                print(
                    f"{index:02d}/48 REUSED "
                    f"{timestamp:%Y-%m-%d %H:%M} UTC"
                )
                total_validated += 1
                continue

            granule_name = matched[timestamp.strftime("%H%M%S")]

            params = [
                ("granuleName", granule_name),
                (
                    "subset",
                    f"lat({MIN_LATITUDE}:{MAX_LATITUDE})",
                ),
                (
                    "subset",
                    f"lon({MIN_LONGITUDE}:{MAX_LONGITUDE})",
                ),
                ("variable", VARIABLE),
            ]

            response = session.get(
                ENDPOINT,
                params=params,
                timeout=300,
            )

            response.raise_for_status()

            content_type = (
                response.headers.get("Content-Type", "")
                .split(";")[0].strip()
            )

            if content_type != "application/x-netcdf4":
                raise RuntimeError(
                    f"Unexpected content type: {content_type}"
                )

            if response.content[:8] != b"\x89HDF\r\n\x1a\n":
                raise RuntimeError(
                    "Response is not a NetCDF4/HDF5 file."
                )

            temporary_path = output_path.with_suffix(
                output_path.suffix + ".tmp"
            )

            try:
                temporary_path.write_bytes(response.content)
                validate_file(temporary_path, timestamp)
                temporary_path.replace(output_path)
            except Exception:
                if temporary_path.exists():
                    temporary_path.unlink()
                raise

            total_validated += 1

            print(
                f"{index:02d}/48 PASS "
                f"{timestamp:%Y-%m-%d %H:%M} UTC"
            )

        current_day += timedelta(days=1)

    expected_total = (
        (end_day - start_day).days + 1
    ) * 48

    final_files = list(OUTPUT_DIR.glob("*.nc4"))

    if len(final_files) != expected_total:
        raise RuntimeError(
            f"Expected {expected_total} files; "
            f"found {len(final_files)}."
        )

    print("\n" + "=" * 68)
    print("HISTORICAL EXPANSION RETRIEVAL: PASS")
    print("Expected observations:", expected_total)
    print("Validated observations:", total_validated)
    print("Files present:", len(final_files))
    print("Output:", OUTPUT_DIR)


if __name__ == "__main__":
    main()
