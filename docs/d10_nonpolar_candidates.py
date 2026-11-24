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
        data = np.asarray(grid["precipitation"][0, :, :])
        fill = np.asarray(grid["precipitation"].attrs["_FillValue"]).item()
        lon = np.asarray(grid["lon"][:])
        lat = np.asarray(grid["lat"][:])

        missing = np.isnan(data) | (data == fill)
        valid = ~missing
        zeros = valid & (data == 0)
        nonzero = valid & (data != 0)

        w_missing = sliding_window_view(missing, (3, 3)).sum(axis=(-1, -2))
        w_zero = sliding_window_view(zeros, (3, 3)).sum(axis=(-1, -2))
        w_nonzero = sliding_window_view(nonzero, (3, 3)).sum(axis=(-1, -2))

        eligible_lat = np.abs(lat[1:-1]) < 80

        candidates = np.argwhere(
            (w_missing > 0) &
            (w_missing < 9) &
            (w_zero > 0) &
            (w_nonzero > 0) &
            eligible_lat[np.newaxis, :]
        )

        print("NON-POLAR MIXED-VALUE WINDOWS:", len(candidates))

        if len(candidates) == 0:
            continue

        ranked = sorted(
            candidates.tolist(),
            key=lambda ij: (
                min(int(w_missing[tuple(ij)]),
                    9 - int(w_missing[tuple(ij)])),
                -abs(float(lat[ij[1] + 1]))
            ),
            reverse=True
        )

        for rank, (i, j) in enumerate(ranked[:3], 1):
            print(f"\nRANK {rank}: longitude index={i}, latitude index={j}")
            print("LONGITUDE CENTRES:", lon[i:i+3])
            print("LATITUDE CENTRES:", lat[j:j+3])
            print("VALID:", int(9 - w_missing[i, j]))
            print("MISSING:", int(w_missing[i, j]))
            print("ZERO:", int(w_zero[i, j]))
            print("NONZERO:", int(w_nonzero[i, j]))
            print("PRECIPITATION WINDOW:")
            print(data[i:i+3, j:j+3])

print("\nNON-POLAR CANDIDATE SEARCH COMPLETE")
