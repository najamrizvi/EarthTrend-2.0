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
    "Grid/precipitation",
    "Grid/precipitationQualityIndex",
    "Grid/randomError",
]

for filename in granules:
    path = raw_dir / filename

    print("\n" + "=" * 90)
    print("GRANULE:", filename)
    print("=" * 90)

    if not path.is_file():
        print("FILE MISSING")
        continue

    with h5py.File(path, "r") as f:
        masks = {}
        arrays = {}

        for variable in variables:
            print("\nVARIABLE:", variable)

            if variable not in f:
                print("DATASET NOT FOUND")
                continue

            ds = f[variable]
            data = np.asarray(ds[0, :, :])
            fill = np.asarray(ds.attrs.get("_FillValue", -9999.9)).item()

            missing = np.isnan(data) | (data == fill)
            valid = ~missing
            masks[variable] = missing
            arrays[variable] = data

            print("SHAPE:", ds.shape)
            print("DTYPE:", ds.dtype)
            print("FILL VALUE:", fill)
            print("UNITS:", ds.attrs.get("units", "NOT PRESENT"))
            print("LONG NAME:", ds.attrs.get("LongName", "NOT PRESENT"))
            print("MISSING CELLS:", int(missing.sum()))
            print("VALID CELLS:", int(valid.sum()))

            if variable == "Grid/precipitation":
                print("NONZERO VALID CELLS:", int(np.count_nonzero(data[valid])))

        if len(masks) == 3:
            names = list(masks)

            print("\nPAIRWISE MISSING-MASK DIFFERENCES:")
            for i in range(len(names)):
                for j in range(i + 1, len(names)):
                    a, b = names[i], names[j]
                    differences = np.count_nonzero(masks[a] != masks[b])
                    print(f"{a} vs {b}: {differences:,} cells")

print("\n" + "=" * 90)
print("D10 SOURCE INSPECTION COMPLETE")
print("=" * 90)
