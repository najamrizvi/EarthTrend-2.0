# D10 — Multi-Date, Multi-Granule Source-to-Harmony Fidelity Validation

**Status:** EXPERIMENT DESIGN LOCKED — NOT YET EXECUTED
**Dataset:** GPM IMERG Final Half-Hourly, GPM_3IMERGHH V07
**Variables:**
- `Grid/precipitation`
- `Grid/precipitationQualityIndex`
- `Grid/randomError`

## 1. Objective

Validate whether NASA Harmony regional subset retrieval preserves source-level values, missing-value masks, spatial coordinates, timestamps, fill values, and variable metadata across multiple dates, granules, and geographic regions.

This experiment extends D01–D09 using six granules from three dates in 2020.

## 2. Locked source granules

1. `3B-HHR.MS.MRG.3IMERG.20200201-S000000-E002959.0000.V07B.HDF5`
2. `3B-HHR.MS.MRG.3IMERG.20200201-S003000-E005959.0030.V07B.HDF5`
3. `3B-HHR.MS.MRG.3IMERG.20200501-S000000-E002959.0000.V07B.HDF5`
4. `3B-HHR.MS.MRG.3IMERG.20200501-S003000-E005959.0030.V07B.HDF5`
5. `3B-HHR.MS.MRG.3IMERG.20200801-S000000-E002959.0000.V07B.HDF5`
6. `3B-HHR.MS.MRG.3IMERG.20200801-S003000-E005959.0030.V07B.HDF5`

All six source granules have been downloaded and inspected.

## 3. Locked regional test cases

### Case A — Common non-polar region

Source grid indices:
- Longitude index: 3471
- Latitude index: 393

Longitude centres:
- 167.15°
- 167.25°
- 167.34999°

Latitude centres:
- −50.649998°
- −50.55°
- −50.45°

Coverage:
- All six granules.
- All three variables.
- 3 × 3 cells per variable.
- All 9 precipitation cells are valid and nonzero in each granule.

Purpose: test preservation of valid nonzero measurements across three dates and six granules.

### Case B — Common southern-polar mixed-value region

Source grid indices:
- Longitude index: 1124
- Latitude index: 3

Longitude centres:
- −67.549995°
- −67.45°
- −67.35°

Latitude centres:
- −89.65°
- −89.549995°
- −89.45°

Coverage:
- All six granules.
- All three variables.
- 3 × 3 cells per variable.
- Mixed valid and missing cells in every granule.
- Valid precipitation cells contain zero precipitation.

Purpose: test preservation of missing-value masks, valid zeros, and variable-specific valid measurements across dates.

### Case C — August northern-polar three-state precipitation region

Source granule:
`3B-HHR.MS.MRG.3IMERG.20200801-S000000-E002959.0000.V07B.HDF5`

Source grid indices:
- Longitude index: 195
- Latitude index: 1795

Longitude centres:
- −160.45°
- −160.34999°
- −160.25°

Latitude centres:
- 89.549995°
- 89.65°
- 89.75°

Coverage:
- One granule.
- All three variables.
- 3 × 3 cells per variable.
- Precipitation contains missing cells, valid zeros, and valid nonzero values.

Purpose: test preservation of all three precipitation states in one regional subset.

## 4. Test matrix

| Case | Granules | Variables | Comparisons |
|---|---:|---:|---:|
| A — Non-polar | 6 | 3 | 18 |
| B — Southern polar | 6 | 3 | 18 |
| C — Northern polar | 1 | 3 | 3 |
| **Total** | **13 regional/time cases** | | **39 variable comparisons** |

## 5. Required comparison checks

For every retrieved variable:

1. HTTP response succeeds.
2. Returned content is a valid NetCDF4/HDF5 dataset.
3. Expected spatial dimensions and array shape are verified.
4. Longitude coordinates match the corresponding source cells.
5. Latitude coordinates match the corresponding source cells.
6. Timestamp matches the source granule.
7. Fill-value metadata is checked.
8. Missing-value masks match exactly.
9. All valid source and returned values match within the defined numerical tolerance.
10. Units match the source metadata, including the absence of a units attribute where applicable.
11. LongName metadata matches the source metadata.

Source windows must be extracted using the original HDF5 grid's native longitude-by-latitude ordering. Returned coordinates must be mapped to their corresponding source indices before comparison. Do not assume Harmony always returns precisely the requested centre coordinates or the same spatial extent.

## 6. Acceptance criteria

A variable comparison passes only when:
- Its returned data are readable.
- Spatial and temporal coordinates match the mapped source cells.
- Missing-value masks are identical.
- All valid numerical values match within the predeclared floating-point tolerance.
- Fill-value and available variable metadata match.

A regional/time case passes only when all three variable comparisons pass.

D10 passes only when all 39 variable comparisons pass.

Any unexpected coordinate expansion, dimension change, metadata difference, or numerical discrepancy must be investigated and documented. Do not silently adjust the source window or acceptance criteria to obtain a pass.

## 7. Experimental safeguards

- Do not modify the completed GPM ingestion module.
- Do not modify the original EarthTrend project.
- Do not overwrite source granules or previous experiment outputs.
- Use authenticated Earthdata sessions for Harmony requests.
- Preserve the exact six source granules.
- Record request parameters, response status, content type, output size, and output file for every retrieval.
- Compare returned data against the original HDF5 source, not against previously processed output.
- Preserve unexpected results as evidence.
- Do not generalize findings beyond the tested granules, dates, regions, and variables.

## 8. Current status

Source downloads: COMPLETE
Source inspection: COMPLETE
Regional candidate selection: COMPLETE
Three-variable source inspection: COMPLETE
Experimental design: LOCKED
Harmony retrievals for D10: NOT STARTED
Source-to-Harmony comparisons for D10: NOT STARTED

**D10 is a controlled validation experiment, not a universal validation of all GPM IMERG data or all Harmony requests.**
