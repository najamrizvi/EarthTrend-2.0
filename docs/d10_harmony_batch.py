import json
import h5py
import numpy as np
import earthaccess

from pathlib import Path
from datetime import datetime, timezone

PROJECT = Path(r"C:\Users\Administrator\Documents\EarthTrend-2.0")
DOCS = PROJECT / "docs"
RAW = PROJECT / "data" / "raw" / "gpm_imerg"
OUTPUT = PROJECT / "data" / "processed" / "gpm_imerg" / "d10_harmony"

MANIFEST = DOCS / "D10_HARMONY_REQUEST_MANIFEST.json"
REPORT = DOCS / "D10_HARMONY_BATCH_RESULTS.json"

def decode(value):
    if isinstance(value, (bytes, np.bytes_)):
        return bytes(value).decode("utf-8")
    return value

def coordinate_indices(source_coords, returned_coords, label):
    indices = []

    for value in returned_coords:
        matches = np.where(
            np.isclose(source_coords, value, atol=2e-5, rtol=0)
        )[0]

        if len(matches) != 1:
            raise ValueError(
                f"{label} coordinate mapping is not unique: {value}"
            )

        indices.append(int(matches[0]))

    return indices

def validate_file(request_spec, output_path):
    source_path = RAW / request_spec["granule"]
    variable_name = request_spec["variable"].split("/", 1)[1]

    checks = {}

    with h5py.File(source_path, "r") as src, \
         h5py.File(output_path, "r") as out:

        sg = src["Grid"]
        rg = out["Grid"]

        source_ds = sg[variable_name]
        returned_ds = rg[variable_name]

        source_values = source_ds[:]
        returned_values = returned_ds[:]

        source_lon = sg["lon"][:]
        source_lat = sg["lat"][:]

        returned_lon = rg["lon"][:]
        returned_lat = rg["lat"][:]

        lon_indices = coordinate_indices(
            source_lon, returned_lon, "Longitude"
        )
        lat_indices = coordinate_indices(
            source_lat, returned_lat, "Latitude"
        )

        checks["shape_and_dimensions"] = (
            returned_values.ndim == 3
            and returned_values.shape[0] == 1
            and decode(returned_ds.attrs.get("DimensionNames"))
                == "time,lon,lat"
        )

        checks["coordinates"] = (
            len(lon_indices) == len(returned_lon)
            and len(lat_indices) == len(returned_lat)
        )

        checks["timestamp"] = np.array_equal(
            sg["time"][:], rg["time"][:]
        )

        expected = source_values[
            0,
            np.asarray(lon_indices)[:, None],
            np.asarray(lat_indices)[None, :]
        ]

        actual = returned_values[0]

        checks["mapped_shape"] = expected.shape == actual.shape

        if not checks["mapped_shape"]:
            raise ValueError("Mapped source and returned shapes differ.")

        source_fill = float(source_ds.attrs["_FillValue"])
        returned_fill = float(
            np.asarray(returned_ds.attrs["_FillValue"]).reshape(-1)[0]
        )

        source_missing = np.isclose(
            expected, source_fill, atol=0.01, rtol=0
        )
        returned_missing = np.isclose(
            actual, returned_fill, atol=0.01, rtol=0
        )

        checks["fill_value"] = abs(
            source_fill - returned_fill
        ) <= 0.01

        checks["missing_mask"] = np.array_equal(
            source_missing, returned_missing
        )

        valid = ~source_missing & ~returned_missing

        max_difference = None

        if np.any(valid):
            max_difference = float(
                np.max(np.abs(expected[valid] - actual[valid]))
            )
            checks["valid_values"] = bool(
                np.allclose(
                    expected[valid],
                    actual[valid],
                    atol=1e-6,
                    rtol=0
                )
            )
        else:
            checks["valid_values"] = True

        source_has_units = "Units" in source_ds.attrs
        returned_has_units = "Units" in returned_ds.attrs

        checks["units_presence"] = (
            source_has_units == returned_has_units
        )

        if source_has_units and returned_has_units:
            checks["units"] = (
                decode(source_ds.attrs["Units"])
                == decode(returned_ds.attrs["Units"])
            )
        else:
            checks["units"] = True

        checks["long_name"] = (
            decode(source_ds.attrs.get("LongName"))
            == decode(returned_ds.attrs.get("LongName"))
        )

        details = {
            "source_shape": list(source_values.shape),
            "returned_shape": list(returned_values.shape),
            "returned_longitude_count": len(returned_lon),
            "returned_latitude_count": len(returned_lat),
            "source_longitude_indices": lon_indices,
            "source_latitude_indices": lat_indices,
            "valid_cells": int((~source_missing).sum()),
            "missing_cells": int(source_missing.sum()),
            "maximum_absolute_difference": max_difference,
            "source_units_present": source_has_units,
            "returned_units_present": returned_has_units,
            "checks": checks,
        }

    return all(checks.values()), details

def save_report(report):
    REPORT.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8"
    )

print("=" * 78)
print("D10 CONTROLLED HARMONY BATCH")
print("=" * 78)

manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
requests_list = manifest["requests"]

if len(requests_list) != 39:
    raise RuntimeError("Manifest does not contain exactly 39 requests.")

# First request is already retrieved and independently validated.
remaining = requests_list[1:]

if len(remaining) != 38:
    raise RuntimeError("Expected exactly 38 remaining requests.")

OUTPUT.mkdir(parents=True, exist_ok=True)

for request_spec in remaining:
    expected_path = OUTPUT / request_spec["output_filename"]

    if expected_path.exists():
        raise FileExistsError(
            f"Refusing to overwrite existing output: {expected_path.name}"
        )

print("Manifest requests:", len(requests_list))
print("Previously validated pilot: 1")
print("Remaining requests:", len(remaining))
print("Output directory:", OUTPUT)

print("\nAuthenticating with Earthdata...")
auth = earthaccess.login(strategy="interactive")

if not auth:
    raise RuntimeError("Earthdata authentication failed.")

session = earthaccess.get_requests_https_session()
print("Authentication: PASS")

report = {
    "experiment": "D10",
    "started_utc": datetime.now(timezone.utc).isoformat(),
    "manifest_request_count": 39,
    "pilot_previously_validated": 1,
    "batch_request_count": 38,
    "completed": [],
    "failed": [],
    "status": "RUNNING",
}

save_report(report)

for number, request_spec in enumerate(remaining, start=2):
    filename = request_spec["output_filename"]
    output_path = OUTPUT / filename
    temporary_path = output_path.with_suffix(
        output_path.suffix + ".tmp"
    )

    print("\n" + "=" * 78)
    print(f"REQUEST {number}/39")
    print("Region:", request_spec["region"])
    print("Granule:", request_spec["granule"])
    print("Variable:", request_spec["variable"])
    print("Output:", filename)

    try:
        response = session.get(
            request_spec["endpoint"],
            params=request_spec["query_parameters"],
            timeout=300
        )

        print("HTTP status:", response.status_code)

        response.raise_for_status()

        content_type = response.headers.get(
            "Content-Type", ""
        ).split(";")[0].strip()

        print("Content type:", content_type)
        print("Response bytes:", len(response.content))

        if content_type != request_spec["expected_content_type"]:
            raise ValueError("Unexpected response content type.")

        if response.content[:8] != b"\x89HDF\r\n\x1a\n":
            raise ValueError("Invalid NetCDF4/HDF5 signature.")

        temporary_path.write_bytes(response.content)

        passed, details = validate_file(
            request_spec, temporary_path
        )

        print("\nVALIDATION CHECKS:")

        for name, result in details["checks"].items():
            print(f"{name}: {'PASS' if result else 'FAIL'}")

        print(
            "Maximum absolute difference:",
            details["maximum_absolute_difference"]
        )

        if not passed:
            failed_path = output_path.with_suffix(
                ".failed.nc4"
            )

            if failed_path.exists():
                raise FileExistsError(
                    "Failed-output preservation file already exists."
                )

            temporary_path.replace(failed_path)

            raise ValueError(
                "Source-to-Harmony validation failed. "
                "Output preserved with .failed.nc4 suffix."
            )

        temporary_path.replace(output_path)

        result = {
            "request_number": number,
            "region": request_spec["region"],
            "granule": request_spec["granule"],
            "variable": request_spec["variable"],
            "output": filename,
            "http_status": response.status_code,
            "content_type": content_type,
            "response_bytes": len(response.content),
            "status": "PASS",
            **details,
        }

        report["completed"].append(result)
        print("\nREQUEST RESULT: PASS")

    except Exception as exc:
        if temporary_path.exists():
            temporary_path.unlink()

        report["failed"].append({
            "request_number": number,
            "region": request_spec["region"],
            "granule": request_spec["granule"],
            "variable": request_spec["variable"],
            "output": filename,
            "error_type": type(exc).__name__,
            "error": str(exc) if isinstance(
                exc, (ValueError, FileExistsError)
            ) else "Request or validation operation failed.",
        })

        report["status"] = "STOPPED_ON_FAILURE"
        report["stopped_at_request"] = number
        report["updated_utc"] = datetime.now(
            timezone.utc
        ).isoformat()

        save_report(report)

        print("\nBATCH STOPPED:", type(exc).__name__)
        print("Checkpoint report saved:", REPORT)
        break

    report["updated_utc"] = datetime.now(
        timezone.utc
    ).isoformat()

    save_report(report)

else:
    report["status"] = "ALL_38_PASSED"
    report["finished_utc"] = datetime.now(
        timezone.utc
    ).isoformat()
    save_report(report)

print("\n" + "=" * 78)
print("D10 BATCH SUMMARY")
print("=" * 78)
print("Completed:", len(report["completed"]))
print("Failed:", len(report["failed"]))
print("Status:", report["status"])
print("Report:", REPORT)
