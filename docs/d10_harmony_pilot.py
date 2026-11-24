import json
from pathlib import Path

import earthaccess
import h5py
import requests

PROJECT = Path(r"C:\Users\Administrator\Documents\EarthTrend-2.0")
DOCS = PROJECT / "docs"
MANIFEST = DOCS / "D10_HARMONY_REQUEST_MANIFEST.json"
OUTPUT_DIR = PROJECT / "data" / "processed" / "gpm_imerg" / "d10_harmony"

print("=" * 78)
print("D10 FIRST HARMONY PILOT RETRIEVAL")
print("=" * 78)

data = json.loads(MANIFEST.read_text(encoding="utf-8"))
request_spec = data["requests"][0]

endpoint = request_spec["endpoint"]
params = request_spec["query_parameters"]
expected_type = request_spec["expected_content_type"]
output_path = OUTPUT_DIR / request_spec["output_filename"]

print("Region:", request_spec["region"])
print("Granule:", request_spec["granule"])
print("Variable:", request_spec["variable"])
print("Output:", output_path.name)
print("Manifest request count:", len(data["requests"]))

if output_path.exists():
    raise FileExistsError(
        f"Refusing to overwrite existing output: {output_path}"
    )

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("\nAuthenticating with Earthdata...")
auth = earthaccess.login(strategy="interactive")

if not auth:
    raise RuntimeError("Earthdata authentication was not successful.")

session = earthaccess.get_requests_https_session()

print("Authentication: PASS")
print("Sending first manifest request...")

response = session.get(
    endpoint,
    params=params,
    timeout=300,
)

print("HTTP status:", response.status_code)
print("Content type:", response.headers.get("Content-Type", ""))
print("Response bytes:", len(response.content))

response.raise_for_status()

actual_type = response.headers.get("Content-Type", "").split(";")[0].strip()

if actual_type != expected_type:
    raise RuntimeError(
        f"Unexpected content type: {actual_type!r}; "
        f"expected {expected_type!r}"
    )

if len(response.content) < 8:
    raise RuntimeError("Response is too small to be a valid NetCDF4 file.")

if response.content[:8] != b"\x89HDF\r\n\x1a\n":
    raise RuntimeError("Response does not have the expected HDF5 signature.")

temporary_path = output_path.with_suffix(output_path.suffix + ".tmp")

try:
    temporary_path.write_bytes(response.content)

    with h5py.File(temporary_path, "r") as dataset:
        print("\nNetCDF4/HDF5 structure:")
        print("Top-level groups:", list(dataset.keys()))

        if "Grid" not in dataset:
            raise RuntimeError("Expected Grid group is missing.")

        variable_name = request_spec["variable"].split("/", 1)[1]

        if variable_name not in dataset["Grid"]:
            raise RuntimeError(
                f"Expected Grid/{variable_name} is missing."
            )

        variable = dataset["Grid"][variable_name]
        print("Variable:", request_spec["variable"])
        print("Shape:", variable.shape)
        print("Dtype:", variable.dtype)

    temporary_path.replace(output_path)

except Exception:
    if temporary_path.exists():
        temporary_path.unlink()
    raise

print("\nPILOT RESULT: PASS")
print("Saved file:", output_path)
print("Saved bytes:", output_path.stat().st_size)
print("Only one Harmony request was made.")
