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

common_valid = None
coverage = None
total_nonzero = None
longitude = None
latitude = None

for filename in granules:
    print("INSPECTING:", filename)

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

        if common_valid is None:
            common_valid = valid.copy()
            coverage = np.zeros(
                (data.shape[0] - 2, data.shape[1] - 2),
                dtype=np.uint8
            )
            total_nonzero = np.zeros_like(coverage, dtype=np.uint8)
        else:
            common_valid &= valid

        nonzero = valid & (data != 0)
        nonzero_windows = sliding_window_view(
            nonzero, (3, 3)
        ).sum(axis=(-1, -2))

        coverage += (nonzero_windows > 0).astype(np.uint8)
        total_nonzero += nonzero_windows.astype(np.uint8)

fully_valid_windows = sliding_window_view(
    common_valid, (3, 3)
).all(axis=(-1, -2))

eligible_latitude = np.abs(latitude[1:-1]) < 80
eligible = fully_valid_windows & eligible_latitude[np.newaxis, :]

scores = np.where(
    eligible,
    coverage.astype(np.int16) * 100 + total_nonzero,
    -1
)

flat = scores.ravel()
candidate_count = int(np.count_nonzero(flat >= 0))

print("\n" + "=" * 85)
print("COMMON NON-POLAR FULLY VALID WINDOW SEARCH")
print("=" * 85)
print("FULLY VALID NON-POLAR WINDOWS:", candidate_count)

if candidate_count == 0:
    print("NO COMMON NON-POLAR WINDOW FOUND")
else:
    top_indices = np.argpartition(flat, -min(5, candidate_count))[
        -min(5, candidate_count):
    ]
    top_indices = sorted(
        top_indices,
        key=lambda k: int(flat[k]),
        reverse=True
    )

    for rank, flat_index in enumerate(top_indices, 1):
        i, j = np.unravel_index(flat_index, scores.shape)

        print(f"\nRANK {rank}: longitude index={i}, latitude index={j}")
        print("SCORE:", int(scores[i, j]))
        print("NONZERO GRANULE COVERAGE:", int(coverage[i, j]), "/ 6")
        print("TOTAL NONZERO CELLS ACROSS GRANULES:", int(total_nonzero[i, j]))
        print("LONGITUDE CENTRES:", longitude[i:i+3])
        print("LATITUDE CENTRES:", latitude[j:j+3])

        for filename in granules:
            with h5py.File(raw_dir / filename, "r") as f:
                block = np.asarray(
                    f["Grid/precipitation"][0, i:i+3, j:j+3]
                )

            print("\n", filename)
            print("NONZERO CELLS:", int(np.count_nonzero(block != 0)))
            print(block)

print("\nCOMMON NON-POLAR REGION SEARCH COMPLETE")
