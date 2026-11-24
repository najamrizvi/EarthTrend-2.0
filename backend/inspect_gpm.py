
import h5py
import numpy as np
from pathlib import Path

data_dir = Path("../data/raw/gpm_imerg").resolve()
files = sorted(data_dir.glob("*.HDF5"))[:2]

rates = []
valid_masks = []
lat_bounds = None

for file_path in files:
    with h5py.File(file_path, "r") as f:
        grid = f["Grid"]
        dataset = grid["precipitation"]

        values = dataset[0].astype(np.float64)
        fill = dataset.attrs["_FillValue"]

        valid = np.isfinite(values) & (values != fill)

        rates.append(values)
        valid_masks.append(valid)

        if lat_bounds is None:
            lat_bounds = grid["lat_bnds"][:]

south = np.deg2rad(lat_bounds[:, 0])
north = np.deg2rad(lat_bounds[:, 1])

latitude_weights = np.sin(north) - np.sin(south)

weights = np.broadcast_to(
    latitude_weights[np.newaxis, :],
    rates[0].shape
)

paired = valid_masks[0] & valid_masks[1]

hourly = (
    rates[0][paired] * 0.5
    + rates[1][paired] * 0.5
)

hourly_weights = weights[paired]

simple_mean = float(np.mean(hourly))

weighted_mean = float(
    np.sum(hourly * hourly_weights)
    / np.sum(hourly_weights)
)

difference = weighted_mean - simple_mean

print("===== AREA-WEIGHTING VALIDATION =====")
print("Valid paired cells:", int(paired.sum()))
print("Unweighted global mean (mm):", simple_mean)
print("Area-weighted global mean (mm):", weighted_mean)
print("Weighted minus unweighted (mm):", difference)
print(
    "Relative difference (%):",
    difference / simple_mean * 100 if simple_mean else None
)

print("\n===== WEIGHT VALIDATION =====")
print("Minimum latitude weight:", float(latitude_weights.min()))
print("Maximum latitude weight:", float(latitude_weights.max()))
print("Equatorial weight:", float(latitude_weights[899]))
print("High-latitude weight:", float(latitude_weights[0]))
