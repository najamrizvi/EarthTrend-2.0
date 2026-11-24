import h5py
import numpy as np
from pathlib import Path

raw_dir = Path(r"C:\Users\Administrator\Documents\EarthTrend-2.0\data\raw\gpm_imerg")

candidates = [
    ("3B-HHR.MS.MRG.3IMERG.20200201-S000000-E002959.0000.V07B.HDF5", 46, 3),
    ("3B-HHR.MS.MRG.3IMERG.20200201-S003000-E005959.0030.V07B.HDF5", 46, 3),
    ("3B-HHR.MS.MRG.3IMERG.20200501-S000000-E002959.0000.V07B.HDF5", 6, 1),
    ("3B-HHR.MS.MRG.3IMERG.20200501-S003000-E005959.0030.V07B.HDF5", 9, 1),
    ("3B-HHR.MS.MRG.3IMERG.20200801-S000000-E002959.0000.V07B.HDF5", 195, 1795),
    ("3B-HHR.MS.MRG.3IMERG.20200801-S003000-E005959.0030.V07B.HDF5", 176, 1795),
]

variables = [
    "Grid/precipitation",
    "Grid/precipitationQualityIndex",
    "Grid/randomError",
]

for filename, i, j in candidates:
    print("\n" + "=" * 90)
    print("GRANULE:", filename)
    print("WINDOW INDICES: longitude", i, "to", i+2, "| latitude", j, "to", j+2)
    print("=" * 90)

    with h5py.File(raw_dir / filename, "r") as f:
        grid = f["Grid"]

        print("GRID DATASETS:", list(grid.keys()))

        lon = np.asarray(grid["lon"][:])
        lat = np.asarray(grid["lat"][:])

        print("LONGITUDE CENTRES:", lon[i:i+3])
        print("LATITUDE CENTRES:", lat[j:j+3])

        for name in ("lon_bnds", "lat_bnds"):
            if name in grid:
                bounds = np.asarray(grid[name][:])
                print(name.upper(), "WINDOW:")
                print(bounds[i:i+3] if name == "lon_bnds" else bounds[j:j+3])

        if "time" in grid:
            print("TIME:", np.asarray(grid["time"][:]))

        for variable in variables:
            ds = grid[variable.split("/")[-1]]
            block = np.asarray(ds[0, i:i+3, j:j+3])
            fill = np.asarray(ds.attrs["_FillValue"]).item()

            print("\n", variable)
            print(block)
            print("MISSING:", int(np.count_nonzero(block == fill)))
            print("VALID ZERO:", int(np.count_nonzero(block == 0)))
            print("VALID NONZERO:", int(np.count_nonzero((block != fill) & (block != 0))))

print("\nCOORDINATE AND MULTI-VARIABLE WINDOW INSPECTION COMPLETE")
