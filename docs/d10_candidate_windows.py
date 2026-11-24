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

def find_windows(data, fill, limit=5):
    missing = np.isnan(data) | (data == fill)
    valid = ~missing
    results = []

    for i in range(data.shape[0] - 2):
        for j in range(data.shape[1] - 2):
            block = data[i:i+3, j:j+3]
            mask = valid[i:i+3, j:j+3]

            if mask.any() and (~mask).any():
                vals = block[mask]
                has_zero = np.any(vals == 0)
                has_nonzero = np.any(vals != 0)

                results.append({
                    "lon_index": i,
                    "lat_index": j,
                    "valid": int(mask.sum()),
                    "missing": int((~mask).sum()),
                    "zero": bool(has_zero),
                    "nonzero": bool(has_nonzero),
                    "mixed_zero_nonzero": bool(has_zero and has_nonzero),
                })

    results.sort(
        key=lambda x: (
            x["mixed_zero_nonzero"],
            min(x["valid"], x["missing"])
        ),
        reverse=True
    )
    return results[:limit]

for filename in granules:
    path = raw_dir / filename

    print("\n" + "=" * 85)
    print("GRANULE:", filename)
    print("=" * 85)

    with h5py.File(path, "r") as f:
        ds = f["Grid/precipitation"]
        data = np.asarray(ds[0, :, :])
        fill = np.asarray(ds.attrs["_FillValue"]).item()

        windows = find_windows(data, fill)

        for rank, item in enumerate(windows, 1):
            print(
                f"RANK {rank}: "
                f"lon_index={item['lon_index']}, "
                f"lat_index={item['lat_index']}, "
                f"valid={item['valid']}, "
                f"missing={item['missing']}, "
                f"zero={item['zero']}, "
                f"nonzero={item['nonzero']}, "
                f"mixed_zero_nonzero={item['mixed_zero_nonzero']}"
            )

            if rank == 1:
                i, j = item["lon_index"], item["lat_index"]
                print("TOP WINDOW:")
                print(data[i:i+3, j:j+3])

print("\nCANDIDATE WINDOW SEARCH COMPLETE")
