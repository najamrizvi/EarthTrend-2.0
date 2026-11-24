
import re
from pathlib import Path

import earthaccess
import h5py
import requests


# ---------------------------------------------------------
# PROJECT SETTINGS
# ---------------------------------------------------------

PROJECT = Path(
    r"C:\Users\Administrator\Documents\EarthTrend-2.0"
)

OUTPUT_DIR = (
    PROJECT
    / "data"
    / "processed"
    / "gpm_imerg"
    / "historical_pilot_20200101"
)

ENDPOINT = (
    "https://harmony.earthdata.nasa.gov/"
    "GPM_3IMERGHH/ogc-api-coverages/1.0.0/"
    "collections/parameter_vars/coverage/rangeset"
)

DATE = "20200101"

MIN_LATITUDE = -0.06
MAX_LATITUDE = 0.06
MIN_LONGITUDE = -0.06
MAX_LONGITUDE = 0.06

VARIABLE = "Grid/precipitation"

EXPECTED_OBSERVATIONS = 48

GRANULE_PATTERN = re.compile(
    r"3B-HHR\.MS\.MRG\.3IMERG\."
    r"20200101-S(\d{6})-E\d{6}\.\d{4}\.V07B\.HDF5$"
)


# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------

def get_granule_filename(granule):
    granule_ur = granule["umm"]["GranuleUR"]
    return granule_ur.split(":", 1)[-1]


def validate_hdf5_file(path):
    if not path.is_file() or path.stat().st_size < 8:
        raise RuntimeError(
            f"Missing or empty scientific file: {path.name}"
        )

    with h5py.File(path, "r") as dataset:
        if "Grid" not in dataset:
            raise RuntimeError(
                f"Grid group missing: {path.name}"
            )

        if "precipitation" not in dataset["Grid"]:
            raise RuntimeError(
                f"Precipitation variable missing: {path.name}"
            )

        variable = dataset["Grid"]["precipitation"]

        if variable.size == 0:
            raise RuntimeError(
                f"Precipitation variable is empty: {path.name}"
            )

        return {
            "shape": variable.shape,
            "dtype": str(variable.dtype),
        }


def expected_start_times():
    return [
        f"{hour:02d}{minute:02d}00"
        for hour in range(24)
        for minute in (0, 30)
    ]


# ---------------------------------------------------------
# START
# ---------------------------------------------------------

print("=" * 70)
print("EARTHTREND 2.0 - HISTORICAL PRECIPITATION PILOT")
print("=" * 70)

print("Date: 2020-01-01")
print("Region: 0 degrees / 0 degrees")
print("Latitude:", MIN_LATITUDE, "to", MAX_LATITUDE)
print("Longitude:", MIN_LONGITUDE, "to", MAX_LONGITUDE)
print("Variable:", VARIABLE)
print("Expected observations:", EXPECTED_OBSERVATIONS)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------
# EARTHDATA AUTHENTICATION
# ---------------------------------------------------------

print("\nAuthenticating with NASA Earthdata...")

auth = earthaccess.login(strategy="interactive")

if not auth or not getattr(auth, "authenticated", False):
    raise RuntimeError(
        "NASA Earthdata authentication failed."
    )

print("EARTHDATA AUTHENTICATION: PASS")


# ---------------------------------------------------------
# FIND THE 48 ORIGINAL GRANULES
# ---------------------------------------------------------

print("\nSearching NASA GPM IMERG granules...")

granules = earthaccess.search_data(
    short_name="GPM_3IMERGHH",
    version="07",
    temporal=(
        "2020-01-01T00:00:00",
        "2020-01-01T23:59:59",
    ),
    count=200,
)

matched = {}

for granule in granules:
    filename = get_granule_filename(granule)
    match = GRANULE_PATTERN.fullmatch(filename)

    if match:
        start_time = match.group(1)
        matched[start_time] = filename

expected_times = expected_start_times()

missing_times = [
    value
    for value in expected_times
    if value not in matched
]

unexpected_times = [
    value
    for value in matched
    if value not in expected_times
]

print("Matching granules:", len(matched))

if missing_times or unexpected_times:
    print("Missing timestamps:", missing_times)
    print("Unexpected timestamps:", unexpected_times)

    raise RuntimeError(
        "The complete sequence of 48 half-hourly "
        "granules was not found. No Harmony requests sent."
    )

print("GRANULE SEQUENCE: PASS")
print("Coverage: 00:00 through 23:30 UTC")


# ---------------------------------------------------------
# HARMONY AUTHENTICATED SESSION
# ---------------------------------------------------------

session = earthaccess.get_requests_https_session()

print("\nAuthenticated Harmony session prepared.")


# ---------------------------------------------------------
# DOWNLOAD AND VALIDATE EACH OBSERVATION
# ---------------------------------------------------------

successful = 0
already_validated = 0

for index, start_time in enumerate(expected_times, start=1):

    granule_name = matched[start_time]

    output_path = (
        OUTPUT_DIR
        / f"GPM_20200101_{start_time}_precipitation.nc4"
    )

    print("\n" + "-" * 60)
    print(f"OBSERVATION {index}/{EXPECTED_OBSERVATIONS}")
    print("Granule:", granule_name)

    # Allow safe continuation after an interrupted run.
    if output_path.exists():
        metadata = validate_hdf5_file(output_path)

        already_validated += 1
        successful += 1

        print("EXISTING FILE: VALIDATED")
        print("Shape:", metadata["shape"])
        continue

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

    print("Sending Harmony request...")

    response = session.get(
        ENDPOINT,
        params=params,
        timeout=300,
    )

    print("HTTP status:", response.status_code)

    response.raise_for_status()

    actual_type = (
        response.headers
        .get("Content-Type", "")
        .split(";")[0]
        .strip()
    )

    if actual_type != "application/x-netcdf4":
        raise RuntimeError(
            f"Unexpected response type: {actual_type}"
        )

    if response.content[:8] != b"\x89HDF\r\n\x1a\n":
        raise RuntimeError(
            "Response does not have the expected "
            "NetCDF4/HDF5 signature."
        )

    temporary_path = output_path.with_suffix(
        output_path.suffix + ".tmp"
    )

    try:
        temporary_path.write_bytes(response.content)

        metadata = validate_hdf5_file(temporary_path)

        temporary_path.replace(output_path)

    except Exception:
        if temporary_path.exists():
            temporary_path.unlink()
        raise

    successful += 1

    print("VALIDATION: PASS")
    print("Variable shape:", metadata["shape"])
    print("Variable dtype:", metadata["dtype"])
    print("Saved bytes:", output_path.stat().st_size)


# ---------------------------------------------------------
# FINAL RESULT
# ---------------------------------------------------------

print("\n" + "=" * 70)
print("HISTORICAL PILOT SUMMARY")
print("=" * 70)

print("Expected observations:", EXPECTED_OBSERVATIONS)
print("Successfully validated:", successful)
print("Previously validated:", already_validated)
print(
    "Newly retrieved:",
    successful - already_validated,
)

if successful != EXPECTED_OBSERVATIONS:
    raise RuntimeError(
        "Pilot did not produce all 48 validated observations."
    )

print("\nPILOT RESULT: PASS")
print("Variable: precipitation")
print("Date: 2020-01-01")
print("Region: existing 0-degree region")
print("Output directory:", OUTPUT_DIR)
print("\nNo D10 files or existing ingestion outputs were modified.")
