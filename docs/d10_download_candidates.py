import earthaccess
from pathlib import Path

raw_dir = Path(r"C:\Users\Administrator\Documents\EarthTrend-2.0\data\raw\gpm_imerg")
raw_dir.mkdir(parents=True, exist_ok=True)

selected = {
    "3B-HHR.MS.MRG.3IMERG.20200201-S000000-E002959.0000.V07B.HDF5",
    "3B-HHR.MS.MRG.3IMERG.20200201-S003000-E005959.0030.V07B.HDF5",
    "3B-HHR.MS.MRG.3IMERG.20200501-S000000-E002959.0000.V07B.HDF5",
    "3B-HHR.MS.MRG.3IMERG.20200501-S003000-E005959.0030.V07B.HDF5",
    "3B-HHR.MS.MRG.3IMERG.20200801-S000000-E002959.0000.V07B.HDF5",
    "3B-HHR.MS.MRG.3IMERG.20200801-S003000-E005959.0030.V07B.HDF5",
}

dates = [
    ("2020-02-01T00:00:00", "2020-02-01T01:00:00"),
    ("2020-05-01T00:00:00", "2020-05-01T01:00:00"),
    ("2020-08-01T00:00:00", "2020-08-01T01:00:00"),
]

print("Authenticating with Earthdata...")
auth = earthaccess.login(strategy="interactive")

if not auth.authenticated:
    raise RuntimeError("Earthdata authentication failed.")

print("AUTHENTICATED: True")

matches = {}

for start, end in dates:
    print(f"\nSearching {start[:10]}...")
    results = earthaccess.search_data(
        short_name="GPM_3IMERGHH",
        version="07",
        temporal=(start, end),
        count=10
    )

    for granule in results:
        filename = granule["umm"]["GranuleUR"].split(":", 1)[-1]
        if filename in selected:
            matches[filename] = granule
            print("MATCH:", filename)

missing = selected - set(matches)

if missing:
    raise RuntimeError(f"Selected granules not found: {sorted(missing)}")

print(f"\nEXACT MATCHES: {len(matches)}/6")

existing = {p.name for p in raw_dir.glob("*.HDF5")}
to_download = [
    matches[name]
    for name in sorted(selected)
    if name not in existing
]

print("ALREADY PRESENT:", len(selected) - len(to_download))
print("TO DOWNLOAD:", len(to_download))

if to_download:
    downloaded = earthaccess.download(
        to_download,
        local_path=str(raw_dir)
    )
    print("DOWNLOAD RESULTS:", len(downloaded))

print("\nFINAL FILE VERIFICATION:")
for name in sorted(selected):
    path = raw_dir / name
    if path.is_file() and path.stat().st_size > 0:
        print(f"FOUND | {path.stat().st_size:,} bytes | {name}")
    else:
        print(f"MISSING OR EMPTY | {name}")
