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

mixed_coverage = None
zero_coverage = None
nonzero_coverage = None
longitude = None
latitude = None

for filename in granules:
    print("SCANNING:", filename)

    with h5py.File(raw_dir / filename, "r") as f:
        grid = f["Grid"]
        ds = grid["precipitation"]
        data = np.asarray(ds[0, :, :])
        fill = np.asarray(ds.attrs["_FillValue"]).item()

        if longitude is None:
            longitude = np.asarray(grid["lon"][:])
            latitude = np.asarray(grid["lat"][:])

        missing = np.isnan(data) | (data == fill)
        valid = ~missing
        zeros = valid & (data == 0)
        nonzero = valid & (data != 0)

        wm = sliding_window_view(missing, (3, 3)).sum(axis=(-1, -2))
        wz = sliding_window_view(zeros, (3, 3)).sum(axis=(-1, -2))
        wn = sliding_window_view(nonzero, (3, 3)).sum(axis=(-1, -2))

        mixed = (wm > 0) & (wm < 9)

        if mixed_coverage is None:
            mixed_coverage = np.zeros(mixed.shape, dtype=np.uint8)
            zero_coverage = np.zeros(mixed.shape, dtype=np.uint8)
            nonzero_coverage = np.zeros(mixed.shape, dtype=np.uint8)

        mixed_coverage += mixed.astype(np.uint8)
        zero_coverage += (wz > 0).astype(np.uint8)
        nonzero_coverage += (wn > 0).astype(np.uint8)

eligible_lat = np.abs(latitude[1:-1]) >= 80

eligible = (
    eligible_lat[np.newaxis, :] &
    (mixed_coverage > 0)
)

mixed_coverage = mixed_coverage.astype(np.int16)
zero_coverage = zero_coverage.astype(np.int16)
nonzero_coverage = nonzero_coverage.astype(np.int16)
scores = np.where(
    eligible,
    mixed_coverage * 100 +
    zero_coverage * 10 +
    nonzero_coverage,
    -1
)

flat = scores.ravel()
candidate_count = int(np.count_nonzero(flat >= 0))

print("\n" + "=" * 90)
print("FIXED POLAR WINDOW SEARCH")
print("=" * 90)
print("POLAR WINDOWS MIXED IN AT LEAST ONE GRANULE:", candidate_count)

if candidate_count:
    top = np.argpartition(flat, -min(5, candidate_count))[
        -min(5, candidate_count):
    ]
    top = sorted(top, key=lambda k: int(flat[k]), reverse=True)

    for rank, flat_index in enumerate(top, 1):
        i, j = np.unravel_index(flat_index, scores.shape)

        print(f"\nRANK {rank}: lon_index={i}, lat_index={j}")
        print("SCORE:", int(scores[i, j]))
        print("MIXED GRANULE COVERAGE:", int(mixed_coverage[i, j]), "/ 6")
        print("GRANULES WITH VALID ZERO:", int(zero_coverage[i, j]), "/ 6")
        print("GRANULES WITH VALID NONZERO:", int(nonzero_coverage[i, j]), "/ 6")
        print("LONGITUDE CENTRES:", longitude[i:i+3])
        print("LATITUDE CENTRES:", latitude[j:j+3])

        for filename in granules:
            with h5py.File(raw_dir / filename, "r") as f:
                ds = f["Grid/precipitation"]
                block = np.asarray(ds[0, i:i+3, j:j+3])
                fill = np.asarray(ds.attrs["_FillValue"]).item()

            missing = np.isnan(block) | (block == fill)
            valid_values = block[~missing]

            print("\n", filename)
            print("VALID:", int((~missing).sum()), "MISSING:", int(missing.sum()))
            print("VALID ZERO:", int(np.count_nonzero(valid_values == 0)))
            print("VALID NONZERO:", int(np.count_nonzero(valid_values != 0)))
            print(block)

print("\nFIXED POLAR WINDOW SEARCH COMPLETE")
