import h5py
from pathlib import Path

raw = Path(r"C:\Users\Administrator\Documents\EarthTrend-2.0\data\raw\gpm_imerg")

cases = [
    ("NONPOLAR", 3471, 393, [
        "3B-HHR.MS.MRG.3IMERG.20200201-S000000-E002959.0000.V07B.HDF5",
        "3B-HHR.MS.MRG.3IMERG.20200201-S003000-E005959.0030.V07B.HDF5",
        "3B-HHR.MS.MRG.3IMERG.20200501-S000000-E002959.0000.V07B.HDF5",
        "3B-HHR.MS.MRG.3IMERG.20200501-S003000-E005959.0030.V07B.HDF5",
        "3B-HHR.MS.MRG.3IMERG.20200801-S000000-E002959.0000.V07B.HDF5",
        "3B-HHR.MS.MRG.3IMERG.20200801-S003000-E005959.0030.V07B.HDF5",
    ]),
    ("SOUTH_POLAR", 1124, 3, [
        "3B-HHR.MS.MRG.3IMERG.20200201-S000000-E002959.0000.V07B.HDF5",
        "3B-HHR.MS.MRG.3IMERG.20200201-S003000-E005959.0030.V07B.HDF5",
        "3B-HHR.MS.MRG.3IMERG.20200501-S000000-E002959.0000.V07B.HDF5",
        "3B-HHR.MS.MRG.3IMERG.20200501-S003000-E005959.0030.V07B.HDF5",
        "3B-HHR.MS.MRG.3IMERG.20200801-S000000-E002959.0000.V07B.HDF5",
        "3B-HHR.MS.MRG.3IMERG.20200801-S003000-E005959.0030.V07B.HDF5",
    ]),
    ("NORTH_POLAR", 195, 1795, [
        "3B-HHR.MS.MRG.3IMERG.20200801-S000000-E002959.0000.V07B.HDF5",
    ]),
]

for case, i, j, filenames in cases:
    print("\n" + "=" * 90)
    print("CASE:", case)

    for filename in filenames:
        with h5py.File(raw / filename, "r") as f:
            grid = f["Grid"]
            print("\nGRANULE:", filename)

            for name in ["lon_bnds", "lat_bnds"]:
                if name not in grid:
                    print(name, "NOT FOUND")
                    continue

                if name == "lon_bnds":
                    values = grid[name][i:i+3]
                else:
                    values = grid[name][j:j+3]

                print(name.upper() + ":")
                print(values)

print("\nSOURCE BOUNDARY INSPECTION COMPLETE")
