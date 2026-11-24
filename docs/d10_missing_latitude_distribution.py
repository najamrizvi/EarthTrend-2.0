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

for filename in granules:
    print("\n" + "=" * 85)
    print("GRANULE:", filename)

    with h5py.File(raw_dir / filename, "r") as f:
        ds = f["Grid/precipitation"]
        data = np.asarray(ds[0, :, :])
        fill = np.asarray(ds.attrs["_FillValue"]).item()
        lat = np.asarray(f["Grid/lat"][:])

        missing = np.isnan(data) | (data == fill)
        row_counts = missing.sum(axis=0)

        print("TOTAL MISSING:", int(missing.sum()))
        print("LATITUDE RANGE:", float(lat.min()), "to", float(lat.max()))
        print("ROWS WITH MISSING:", int(np.count_nonzero(row_counts)))

        print("\nMISSING CELLS BY 10-DEGREE LATITUDE BAND:")
        for lower in range(-90, 90, 10):
            upper = lower + 10
            rows = (lat >= lower) & (lat < upper)
            count = int(row_counts[rows].sum())
            if count:
                print(f"{lower:>4} to {upper:>4}: {count:,}")

        affected = np.flatnonzero(row_counts > 0)
        if len(affected):
            print("\nSOUTHERNMOST AFFECTED LATITUDE:", float(lat[affected[0]]))
            print("NORTHERNMOST AFFECTED LATITUDE:", float(lat[affected[-1]]))

print("\nLATITUDE DISTRIBUTION AUDIT COMPLETE")
