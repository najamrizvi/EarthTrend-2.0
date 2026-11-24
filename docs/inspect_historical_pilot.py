
from pathlib import Path
import h5py

folder = Path(
    r"C:\Users\Administrator\Documents\EarthTrend-2.0"
    r"\data\processed\gpm_imerg\historical_pilot_20200101"
)

files = sorted(folder.glob("*.nc4"))

if not files:
    raise RuntimeError("No pilot files found.")

path = files[0]

print("FILE:", path.name)

with h5py.File(path, "r") as dataset:

    print("\nTOP-LEVEL GROUPS:")
    for name in dataset:
        print(name)

    if "Grid" not in dataset:
        raise RuntimeError("Grid group missing.")

    grid = dataset["Grid"]

    print("\nGRID DATASETS AND GROUPS:")
    for name, item in grid.items():
        print("\nNAME:", name)

        if isinstance(item, h5py.Dataset):
            print("SHAPE:", item.shape)
            print("DTYPE:", item.dtype)

            print("ATTRIBUTES:")
            for key, value in item.attrs.items():
                print(f"  {key}: {value}")

    print("\nGRID GROUP ATTRIBUTES:")
    for key, value in grid.attrs.items():
        print(f"  {key}: {value}")

    print("\nROOT ATTRIBUTES:")
    for key, value in dataset.attrs.items():
        print(f"  {key}: {value}")

print("\nINSPECTION COMPLETE")
