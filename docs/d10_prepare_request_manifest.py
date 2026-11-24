from pathlib import Path
import json

root = Path(r"C:\Users\Administrator\Documents\EarthTrend-2.0")
raw = root / "data" / "raw" / "gpm_imerg"

granules = [
    "3B-HHR.MS.MRG.3IMERG.20200201-S000000-E002959.0000.V07B.HDF5",
    "3B-HHR.MS.MRG.3IMERG.20200201-S003000-E005959.0030.V07B.HDF5",
    "3B-HHR.MS.MRG.3IMERG.20200501-S000000-E002959.0000.V07B.HDF5",
    "3B-HHR.MS.MRG.3IMERG.20200501-S003000-E005959.0030.V07B.HDF5",
    "3B-HHR.MS.MRG.3IMERG.20200801-S000000-E002959.0000.V07B.HDF5",
    "3B-HHR.MS.MRG.3IMERG.20200801-S003000-E005959.0030.V07B.HDF5",
]

variables = [
    "Grid/precipitation",
    "Grid/precipitationQualityIndex",
    "Grid/randomError",
]

regions = {
    "NONPOLAR": {
        "lon": (167.09999, 167.4),
        "lat": (-50.699997, -50.4),
        "granules": granules,
    },
    "SOUTH_POLAR": {
        "lon": (-67.6, -67.299995),
        "lat": (-89.700005, -89.399994),
        "granules": granules,
    },
    "NORTH_POLAR": {
        "lon": (-160.5, -160.2),
        "lat": (89.49999, 89.8),
        "granules": [granules[4]],
    },
}

endpoint = (
    "https://harmony.earthdata.nasa.gov/GPM_3IMERGHH/"
    "ogc-api-coverages/1.0.0/collections/parameter_vars/coverage/rangeset"
)

requests = []

for region_name, region in regions.items():
    west, east = region["lon"]
    south, north = region["lat"]

    for granule in region["granules"]:
        if not (raw / granule).is_file():
            raise FileNotFoundError(f"Missing source granule: {granule}")

        for variable in variables:
            variable_name = variable.split("/")[-1]

            requests.append({
                "region": region_name,
                "granule": granule,
                "variable": variable,
                "endpoint": endpoint,
                "query_parameters": [
                    ["granuleName", granule],
                    ["subset", f"lat({south}:{north})"],
                    ["subset", f"lon({west}:{east})"],
                    ["variable", variable],
                ],
                "expected_content_type": "application/x-netcdf4",
                "output_filename": (
                    f"D10_{region_name}_"
                    f"{granule.split('.202')[-1].split('-')[0]}_"
                    f"{granule.split('-S')[-1][:6]}_"
                    f"{variable_name}.nc4"
                ),
            })

assert len(requests) == 39
assert sum(1 for r in requests if r["region"] == "NONPOLAR") == 18
assert sum(1 for r in requests if r["region"] == "SOUTH_POLAR") == 18
assert sum(1 for r in requests if r["region"] == "NORTH_POLAR") == 3

manifest_path = root / "docs" / "D10_HARMONY_REQUEST_MANIFEST.json"
manifest_path.write_text(
    json.dumps({
        "experiment": "D10",
        "status": "PREPARED_NOT_EXECUTED",
        "request_count": len(requests),
        "endpoint": endpoint,
        "requests": requests,
    }, indent=2),
    encoding="utf-8",
)

print("=" * 78)
print("D10 HARMONY REQUEST MANIFEST")
print("=" * 78)
print("Total requests:", len(requests))
print("Nonpolar:", sum(r["region"] == "NONPOLAR" for r in requests))
print("Southern polar:", sum(r["region"] == "SOUTH_POLAR" for r in requests))
print("Northern polar:", sum(r["region"] == "NORTH_POLAR" for r in requests))
print("Variables per case:", len(variables))
print("All six source granules present:", all((raw / g).is_file() for g in granules))
print("Network requests made: 0")
print("Manifest:", manifest_path)

print("\nFIRST REQUEST — REVIEW")
print(json.dumps(requests[0], indent=2))

print("\nLAST REQUEST — REVIEW")
print(json.dumps(requests[-1], indent=2))

print("\nMANIFEST PREPARATION: PASS")
