import h5py
import numpy as np
from pathlib import Path

raw_dir = Path(r"C:\Users\Administrator\Documents\EarthTrend-2.0\data\raw\gpm_imerg")

granules = [
    "3B-HHR.MS.MRG.3IMERG.20200201-S000000-E002959.0000.V07B.HDF5",
    "3B-HHR.MS.MRG.3IMERG.20200201-S003000-E005959.0030.V07B.HDF5",
    "3B-HHR.MS.MRG.3IMERG.20200501-S000000-E002959.0000.V07B.HDF5",
    "3B-HHR.MS.MRG.3IMERG.20200501-S003000-E005959.0030.V07B.HDF5",
    "3B-HHR.MS.MRG.3IMERG.20200801-S000000-E002959.0000.V07B.HDF5",
    "3B-HHR.MS.MRG.3IMERG.20200801-S003000-E005959.0030.V07B.HDF5",
]

variables = [
    "precipitation",
    "precipitationQualityIndex",
    "randomError",
]

i, j = 3471, 393

for filename in granules:
    print("\n" + "=" * 95)
    print("GRANULE:", filename)
    print("=" * 95)

    with h5py.File(raw_dir / filename, "r") as f:
        grid = f["Grid"]

        print("TIME:", np.asarray(grid["time"][:]))
        print("LONGITUDE CENTRES:", np.asarray(grid["lon"][i:i+3]))
        print("LATITUDE CENTRES:", np.asarray(grid["lat"][j:j+3]))

        for variable in variables:
            ds = grid[variable]
            block = np.asarray(ds[0, i:i+3, j:j+3])
            fill = np.asarray(ds.attrs["_FillValue"]).item()
            missing = np.isnan(block) | (block == fill)

            print("\nVARIABLE:", variable)
            print("SHAPE:", block.shape)
            print("DTYPE:", block.dtype)
            print("FILL VALUE:", fill)
            print("MISSING CELLS:", int(missing.sum()))
            print("VALID CELLS:", int((~missing).sum()))
            print("UNITS:", ds.attrs.get("units", "NOT PRESENT"))
            print("LONG NAME:", ds.attrs.get("LongName", "NOT PRESENT"))
            print("VALUES:")
            print(block)

print("\nCOMMON NON-POLAR THREE-VARIABLE INSPECTION COMPLETE")
