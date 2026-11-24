
from pathlib import Path
from datetime import datetime, timezone

import h5py
import numpy as np
import xarray as xr


# ---------------------------------------------------------------------
# PATHS AND CONFIGURATION
# ---------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[3]

RAW_DIR = PROJECT_ROOT / "data" / "raw" / "gpm_imerg"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "gpm_imerg"

# A new output name protects all previously validated datasets.
OUTPUT_NAME = (
    "gpm_imerg_sample_20200101_0000_0100_metadata_v4.zarr"
)

EXPECTED_TIME_UNITS = (
    "seconds since 1980-01-06 00:00:00 UTC"
)

EXPECTED_INTERVAL_SECONDS = 1800

VARIABLES = {
    "precipitation": "Grid/precipitation",
    "precipitation_quality_index": (
        "Grid/precipitationQualityIndex"
    ),
    "random_error": "Grid/randomError",
}


# ---------------------------------------------------------------------
# ATTRIBUTE DECODING
# ---------------------------------------------------------------------

def decode_attribute(value):
    """Decode HDF5 byte attributes into clean Python strings."""

    if isinstance(value, (bytes, np.bytes_)):
        return value.decode("utf-8").strip()

    return value


# ---------------------------------------------------------------------
# SOURCE VARIABLE READING
# ---------------------------------------------------------------------

def read_variable(dataset, variable_path):
    """Read a NASA variable and convert fill values to NaN."""

    source = dataset[variable_path]

    if "_FillValue" not in source.attrs:
        raise ValueError(
            f"Missing _FillValue attribute: {variable_path}"
        )

    values = source[:].astype(np.float32)

    fill_value = float(source.attrs["_FillValue"])

    valid = (
        np.isfinite(values)
        & (values != fill_value)
    )

    values[~valid] = np.nan

    metadata = {
        "original_fill_value": fill_value,
    }

    for attribute_name in ("Units", "units"):
        if attribute_name in source.attrs:
            unit_value = decode_attribute(
                source.attrs[attribute_name]
            )

            if unit_value:
                metadata["units"] = unit_value

            break

    for attribute_name in ("LongName", "long_name"):
        if attribute_name in source.attrs:
            long_name = decode_attribute(
                source.attrs[attribute_name]
            )

            if long_name:
                metadata["long_name"] = long_name

            break

    return values, metadata


# ---------------------------------------------------------------------
# GRANULE READING
# ---------------------------------------------------------------------

def read_granule(file_path):
    """Read one GPM IMERG half-hourly HDF5 granule."""

    with h5py.File(file_path, "r") as source:

        grid = source["Grid"]

        latitude = grid["lat"][:].astype(np.float64)
        longitude = grid["lon"][:].astype(np.float64)

        latitude_bounds = grid["lat_bnds"][:]
        longitude_bounds = grid["lon_bnds"][:]

        time_values = grid["time"][:]
        time_bounds = grid["time_bnds"][:]

        time_units = decode_attribute(
            grid["time"].attrs["Units"]
        )

        if time_units != EXPECTED_TIME_UNITS:
            raise ValueError(
                f"Unexpected time units in {file_path.name}: "
                f"{time_units}"
            )

        if time_values.shape != (1,):
            raise ValueError(
                f"Expected one timestamp in {file_path.name}; "
                f"received shape {time_values.shape}"
            )

        if time_bounds.shape != (1, 2):
            raise ValueError(
                f"Unexpected time-bounds shape in {file_path.name}: "
                f"{time_bounds.shape}"
            )

        epoch = np.datetime64(
            "1980-01-06T00:00:00",
            "s",
        )

        timestamps = (
            epoch + time_values.astype("timedelta64[s]")
        )

        interval_bounds = (
            epoch + time_bounds.astype("timedelta64[s]")
        )

        expected_shape = (
            1,
            len(longitude),
            len(latitude),
        )

        arrays = {}
        metadata = {}

        for name, variable_path in VARIABLES.items():

            values, attrs = read_variable(
                source,
                variable_path,
            )

            if values.shape != expected_shape:
                raise ValueError(
                    f"Unexpected shape for {name} "
                    f"in {file_path.name}: {values.shape}; "
                    f"expected {expected_shape}"
                )

            # NASA source order:
            # time, longitude, latitude
            #
            # Standardized output order:
            # time, latitude, longitude

            arrays[name] = np.transpose(
                values,
                (0, 2, 1),
            )

            metadata[name] = attrs

        return {
            "timestamps": timestamps,
            "time_bounds": interval_bounds,
            "latitude": latitude,
            "longitude": longitude,
            "latitude_bounds": latitude_bounds,
            "longitude_bounds": longitude_bounds,
            "arrays": arrays,
            "metadata": metadata,
            "filename": file_path.name,
        }


# ---------------------------------------------------------------------
# GRANULE CONSISTENCY VALIDATION
# ---------------------------------------------------------------------

def validate_granules(records):
    """Validate grid, metadata, and temporal consistency."""

    reference = records[0]

    for record in records[1:]:

        for coordinate in ("latitude", "longitude"):

            if not np.array_equal(
                record[coordinate],
                reference[coordinate],
            ):
                raise ValueError(
                    f"Grid mismatch in {record['filename']}"
                )

        for coordinate in (
            "latitude_bounds",
            "longitude_bounds",
        ):

            if not np.array_equal(
                record[coordinate],
                reference[coordinate],
            ):
                raise ValueError(
                    f"{coordinate} mismatch "
                    f"in {record['filename']}"
                )

        for name in VARIABLES:

            if (
                record["metadata"][name]
                != reference["metadata"][name]
            ):
                raise ValueError(
                    f"Source metadata mismatch for {name} "
                    f"in {record['filename']}"
                )

    timestamps = np.concatenate(
        [record["timestamps"] for record in records]
    )

    if len(np.unique(timestamps)) != len(timestamps):
        raise ValueError(
            "Duplicate observation timestamps detected"
        )

    if not np.all(
        np.diff(timestamps) > np.timedelta64(0, "s")
    ):
        raise ValueError(
            "Granule timestamps are not strictly increasing"
        )

    time_bounds = np.concatenate(
        [record["time_bounds"] for record in records],
        axis=0,
    )

    if not np.all(
        time_bounds[:, 1] > time_bounds[:, 0]
    ):
        raise ValueError(
            "Invalid observation time bounds"
        )

    interval_durations = (
        time_bounds[:, 1] - time_bounds[:, 0]
    )

    if not np.all(
        interval_durations
        == np.timedelta64(EXPECTED_INTERVAL_SECONDS, "s")
    ):
        raise ValueError(
            "Unexpected observation interval duration"
        )

    if not np.array_equal(
        timestamps,
        time_bounds[:, 0],
    ):
        raise ValueError(
            "Observation timestamps do not match "
            "the beginning of their time bounds"
        )

    for index in range(1, len(time_bounds)):

        if (
            time_bounds[index, 0]
            != time_bounds[index - 1, 1]
        ):
            raise ValueError(
                "Gap or overlap detected between "
                "granule observation intervals"
            )

    return timestamps, time_bounds


# ---------------------------------------------------------------------
# DATASET CONSTRUCTION
# ---------------------------------------------------------------------

def build_dataset(records, timestamps, time_bounds):

    reference = records[0]

    data_vars = {}

    for name in VARIABLES:

        values = np.concatenate(
            [
                record["arrays"][name]
                for record in records
            ],
            axis=0,
        )

        data_vars[name] = (
            ("time", "latitude", "longitude"),
            values,
            reference["metadata"][name].copy(),
        )

    data_vars["time_bounds"] = (
        ("time", "bounds"),
        time_bounds,
    )

    data_vars["latitude_bounds"] = (
        ("latitude", "bounds"),
        reference["latitude_bounds"],
    )

    data_vars["longitude_bounds"] = (
        ("longitude", "bounds"),
        reference["longitude_bounds"],
    )

    # Scalar geographic coordinate reference.
    data_vars["latitude_longitude"] = (
        (),
        np.int8(0),
        {
            "grid_mapping_name": "latitude_longitude",
            "longitude_of_prime_meridian": 0.0,
        },
    )

    dataset = xr.Dataset(
        data_vars=data_vars,

        coords={
            "time": timestamps,

            "latitude": reference["latitude"],

            "longitude": reference["longitude"],

            "bounds": [0, 1],

            "source_granule_index": (
                "time",
                np.arange(
                    len(timestamps),
                    dtype=np.int32,
                ),
            ),
        },

        attrs={
            "title": (
                "EarthTrend 2.0 - "
                "GPM IMERG sample dataset"
            ),

            "source": (
                "NASA GPM IMERG "
                "Final Half-Hourly V07"
            ),

            "collection_short_name": "GPM_3IMERGHH",

            "collection_version": "07",

            "granule_product_version": "V07B",

            "source_files": "; ".join(
                record["filename"]
                for record in records
            ),

            "spatial_resolution": "0.1 degree",

            "time_interval": "30 minutes",

            "time_standard": "UTC",

            "spatial_dimension_order": (
                "latitude, longitude"
            ),

            "processing_note": (
                "Original precipitation rate retained "
                "in its source units. "
                "Source fill values converted to NaN. "
                "Source HDF5 files remain unchanged."
            ),

            "created_utc": datetime.now(
                timezone.utc
            ).isoformat(),
        },
    )

    # -------------------------------------------------------------
    # GRID MAPPING AND ANCILLARY VARIABLES
    # -------------------------------------------------------------

    # All three gridded scientific variables use the same
    # geographic latitude-longitude reference.

    for name in VARIABLES:

        dataset[name].attrs["grid_mapping"] = (
            "latitude_longitude"
        )

    dataset["precipitation"].attrs[
        "ancillary_variables"
    ] = (
        "precipitation_quality_index random_error"
    )

    # -------------------------------------------------------------
    # TIME COORDINATE METADATA
    # -------------------------------------------------------------

    dataset["time"].attrs.update({
        "standard_name": "time",
        "axis": "T",
        "bounds": "time_bounds",
    })

    # -------------------------------------------------------------
    # SPATIAL COORDINATE METADATA
    # -------------------------------------------------------------

    dataset["latitude"].attrs.update({
        "standard_name": "latitude",
        "units": "degrees_north",
        "axis": "Y",
        "bounds": "latitude_bounds",
    })

    dataset["longitude"].attrs.update({
        "standard_name": "longitude",
        "units": "degrees_east",
        "axis": "X",
        "bounds": "longitude_bounds",
    })

    # -------------------------------------------------------------
    # BOUNDS METADATA
    # -------------------------------------------------------------

    dataset["time_bounds"].attrs["description"] = (
        "Start and end of each half-hourly "
        "observation interval"
    )

    dataset["latitude_bounds"].attrs["units"] = (
        "degrees_north"
    )

    dataset["longitude_bounds"].attrs["units"] = (
        "degrees_east"
    )

    # Do not claim formal CF compliance without
    # independent compliance validation.

    dataset.attrs.pop("Conventions", None)

    return dataset


# ---------------------------------------------------------------------
# MAIN INGESTION WORKFLOW
# ---------------------------------------------------------------------

def ingest_granules():

    files = sorted(
        RAW_DIR.glob("*.HDF5")
    )

    if not files:
        raise FileNotFoundError(
            f"No HDF5 granules found in {RAW_DIR}"
        )

    print("Reading source granules...")

    records = [
        read_granule(path)
        for path in files
    ]

    print("Validating source consistency...")

    timestamps, time_bounds = validate_granules(
        records
    )

    print("Constructing standardized dataset...")

    dataset = build_dataset(
        records,
        timestamps,
        time_bounds,
    )

    output_path = OUTPUT_DIR / OUTPUT_NAME

    # Never overwrite an existing validated dataset.

    if output_path.exists():
        raise FileExistsError(
            "Output already exists; refusing to overwrite: "
            f"{output_path}"
        )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    encoding = {
        name: {
            "chunks": (1, 360, 360),
            "dtype": "float32",
        }
        for name in VARIABLES
    }

    print("Writing Zarr dataset...")

    dataset.to_zarr(
        output_path,
        mode="w",
        zarr_format=2,
        encoding=encoding,
    )

    output_size = sum(
        path.stat().st_size
        for path in output_path.rglob("*")
        if path.is_file()
    )

    print()
    print("===== GPM INGESTION COMPLETE =====")

    print("Source granules:", len(files))

    print("Output:", output_path)

    print("Dimensions:", dict(dataset.sizes))

    print("Variables:", list(dataset.data_vars))

    print(
        "Time range:",
        str(timestamps[0]),
        "to",
        str(timestamps[-1]),
    )

    print("Time intervals:", len(timestamps))

    print(
        "Precipitation units:",
        dataset["precipitation"].attrs.get(
            "units",
            "Not provided by source",
        ),
    )

    for name in VARIABLES:

        values = dataset[name].values

        print(
            f"{name}: "
            f"valid={int(np.isfinite(values).sum())}, "
            f"missing={int(np.isnan(values).sum())}"
        )

    print("Output size (bytes):", output_size)


# ---------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------

if __name__ == "__main__":
    ingest_granules()
