import h5py
import numpy as np
from pathlib import Path
from numpy.lib.stride_tricks import sliding_window_view

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
    print("=" * 85)

    with h5py.File(raw_dir / filename, "r") as f:
        grid = f["Grid"]
        ds = grid["precipitation"]
        data = np.asarray(ds[0, :, :])
        fill = np.asarray(ds.attrs["_FillValue"]).item()
        lon = np.asarray(grid["lon"][:])
        lat = np.asarray(grid["lat"][:])

        missing = np.isnan(data) | (data == fill)
        valid = ~missing

        wm = sliding_window_view(missing, (3, 3)).sum(axis=(-1, -2))
        wv = 9 - wm

        eligible = np.abs(lat[1:-1]) < 80
        candidates = np.argwhere(
            (wm > 0) & (wv > 0) & eligible[np.newaxis, :]
        )

        print("NON-POLAR MIXED MISSING/VALID WINDOWS:", len(candidates))

        ranked = sorted(
            candidates.tolist(),
            key=lambda ij: (
                min(int(wm[tuple(ij)]), int(wv[tuple(ij)])),
                int(wv[tuple(ij)])
            ),
            reverse=True
        )

        for rank, (i, j) in enumerate(ranked[:3], 1):
            block = data[i:i+3, j:j+3]
            mask = missing[i:i+3, j:j+3]
            vals = block[~mask]

            print(f"\nRANK {rank}: lon_index={i}, lat_index={j}")
            print("LONGITUDE:", lon[i:i+3])
            print("LATITUDE:", lat[j:j+3])
            print("VALID:", int((~mask).sum()), "MISSING:", int(mask.sum()))
            print("VALID ZERO:", int(np.count_nonzero(vals == 0)))
            print("VALID NONZERO:", int(np.count_nonzero(vals != 0)))
            print("PRECIPITATION:")
            print(block)

print("\nNON-POLAR MIXED MISSING/VALID SEARCH COMPLETE")
