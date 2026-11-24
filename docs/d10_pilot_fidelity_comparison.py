from pathlib import Path
import h5py
import numpy as np

project = Path(r"C:\Users\Administrator\Documents\EarthTrend-2.0")

source_path = project / "data/raw/gpm_imerg/3B-HHR.MS.MRG.3IMERG.20200201-S000000-E002959.0000.V07B.HDF5"
returned_path = project / "data/processed/gpm_imerg/d10_harmony/D10_NONPOLAR_00201_000000_precipitation.nc4"

def decode(value):
    if isinstance(value, (bytes, np.bytes_)):
        return bytes(value).decode("utf-8")
    return value

def check(name, condition):
    passed = bool(condition)
    print(f"{name}: {'PASS' if passed else 'FAIL'}")
    return passed

print("=" * 78)
print("D10 PILOT — CORRECTED SOURCE-TO-HARMONY COMPARISON")
print("=" * 78)

with h5py.File(source_path, "r") as src, h5py.File(returned_path, "r") as out:
    sg, rg = src["Grid"], out["Grid"]

    source = sg["precipitation"][:]
    returned = rg["precipitation"][:]

    source_lon, source_lat = sg["lon"][:], sg["lat"][:]
    returned_lon, returned_lat = rg["lon"][:], rg["lat"][:]

    lon_indices = []
    lat_indices = []

    for value in returned_lon:
        matches = np.where(np.isclose(source_lon, value, atol=2e-5, rtol=0))[0]
        if len(matches) != 1:
            raise RuntimeError(f"Longitude mapping is not unique: {value}")
        lon_indices.append(int(matches[0]))

    for value in returned_lat:
        matches = np.where(np.isclose(source_lat, value, atol=2e-5, rtol=0))[0]
        if len(matches) != 1:
            raise RuntimeError(f"Latitude mapping is not unique: {value}")
        lat_indices.append(int(matches[0]))

    # Source and Harmony both use (time, longitude, latitude).
    expected = source[
        0,
        np.asarray(lon_indices)[:, None],
        np.asarray(lat_indices)[None, :]
    ]

    actual = returned[0]

    source_fill = float(np.asarray(sg["precipitation"].attrs["_FillValue"]).reshape(-1)[0])
    returned_fill = float(np.asarray(rg["precipitation"].attrs["_FillValue"]).reshape(-1)[0])

    expected_missing = np.isclose(expected, source_fill, atol=0.01, rtol=0)
    actual_missing = np.isclose(actual, returned_fill, atol=0.01, rtol=0)

    mask_match = np.array_equal(expected_missing, actual_missing)
    valid = ~expected_missing & ~actual_missing

    max_difference = (
        float(np.max(np.abs(expected[valid] - actual[valid])))
        if np.any(valid) else None
    )

    value_match = (
        bool(np.allclose(expected[valid], actual[valid], atol=1e-6, rtol=0))
        if np.any(valid) else False
    )

    source_units = decode(sg["precipitation"].attrs.get("Units"))
    returned_units = decode(rg["precipitation"].attrs.get("Units"))

    source_long = decode(sg["precipitation"].attrs.get("LongName"))
    returned_long = decode(rg["precipitation"].attrs.get("LongName"))

    print("\nSOURCE SHAPE:", source.shape)
    print("RETURNED SHAPE:", returned.shape)
    print("SOURCE LONGITUDE INDICES:", lon_indices)
    print("SOURCE LATITUDE INDICES:", lat_indices)

    print("\nEXPECTED SOURCE VALUES:")
    print(expected)

    print("\nHARMONY VALUES:")
    print(actual)

    print("\nMISSING MASK DIFFERENCES:", np.count_nonzero(expected_missing != actual_missing))
    print("SOURCE VALID CELLS:", int((~expected_missing).sum()))
    print("HARMONY VALID CELLS:", int((~actual_missing).sum()))
    print("MAXIMUM ABSOLUTE VALUE DIFFERENCE:", max_difference)

    results = [
        check("Returned coordinates map uniquely", True),
        check("Timestamp matches", np.array_equal(sg["time"][:], rg["time"][:])),
        check("Missing masks match", mask_match),
        check("Valid values match within 1e-6", value_match),
        check("Fill values match", abs(source_fill - returned_fill) <= 0.01),
        check("Units match", source_units == returned_units),
        check("LongName matches", source_long == returned_long),
    ]

    print("\n" + "=" * 78)
    print("PILOT FIDELITY RESULT:", "PASS" if all(results) else "FAIL")
    print("=" * 78)
