# D01 — GPM IMERG Regional Retrieval Validation

**Project:** EarthTrend 2.0
**Experiment:** D01
**Status:** PASSED — Limited to the tested case
**Validation date:** 2026-11-18

## 1. Objective

Determine whether NASA Harmony can retrieve a geographically and temporally constrained subset of GPM IMERG Final V07 precipitation data without downloading an entire global half-hourly granule.

The retrieved subset was compared against the corresponding cells in the original global granule.

## 2. Locked Experiment Configuration

| Parameter | Value |
|---|---|
| Dataset | GPM IMERG Final Half-Hourly |
| Collection | GPM_3IMERGHH |
| Collection version | 07 |
| Granule product version | V07B |
| Date | 2020-01-01 |
| Time interval | 00:00–00:30 UTC |
| West | 68.30 |
| East | 68.40 |
| South | 25.35 |
| North | 25.45 |
| Variable | Grid/precipitation |
| Output format | NetCDF4 |

**Original granule:**

`3B-HHR.MS.MRG.3IMERG.20200101-S000000-E002959.0000.V07B.HDF5`

**DOI:** `10.5067/GPM/IMERG/3B-HH/07`

## 3. Retrieval Results

NASA Harmony successfully returned HTTP 200.

The retrieved output was a NetCDF4/HDF5-compatible file.

| Measurement | Result |
|---|---:|
| Original global granule | 7,553,086 bytes |
| Regional subset | 45,254 bytes |
| Original grid cells | 6,480,000 |
| Returned grid cells | 6 |
| Returned longitude coordinates | 3 |
| Returned latitude coordinates | 2 |
| Returned time coordinates | 1 |

**Temporary subset location:**

`%TEMP%\earthtrend_d01_regional_subset.nc4`

The subset was approximately 99.4% smaller than the original granule by file size.

## 4. Coordinate and Spatial Validation

**Returned latitude centres:**
- 25.350000
- 25.449999

**Returned longitude centres:**
- 68.25
- 68.35
- 68.45

The returned coordinate centres matched the corresponding original-grid coordinates exactly.

**Spatial selection observation:** Harmony returned grid cells intersecting the requested bounding box. Consequently, some returned cell centres lie outside the exact requested bounds.

This behaviour must be considered when implementing regional selection and must not be described as centre-only filtering.

## 5. Data-Fidelity Validation

The original global precipitation array uses longitude × latitude dimension ordering.

The initial comparison incorrectly transposed the expected regional array. This produced an apparent missing-mask mismatch.

Inspection of both files established:

- Original `_FillValue`: -9999.9
- Subset `_FillValue`: -9999.9
- Original `CodeMissingValue`: -9999.9
- Subset `CodeMissingValue`: -9999.9

The comparison was corrected to preserve the native longitude × latitude ordering.

**Corrected comparison:**

```python
expected = original[np.ix_(lon_idx, lat_idx)]
```

**Final results:**

| Validation | Result |
|---|---|
| Expected shape | (3, 2) |
| Returned shape | (3, 2) |
| Missing masks identical | True |
| All precipitation values identical | True |
| Maximum absolute difference | 0.0 |
| Fill-value metadata | Matching |

All six tested precipitation values were 0.0 mm/hr.

The corrected comparison demonstrated exact numerical agreement for all six cells.

## 6. Final Assessment

**D01 PASSED for the exact tested case.**

NASA Harmony successfully retrieved a spatially and temporally constrained GPM IMERG Final V07 regional subset in NetCDF4 format.

The returned precipitation values, missing-value masks, and coordinates matched the corresponding cells in the original global granule exactly.

**Maximum absolute numerical difference: 0.0.**

## 7. Scientific Limitations

This result must not be generalized beyond the tested configuration.

1. Only one granule and one 30-minute interval were tested.
2. Only one precipitation variable was validated.
3. All six returned precipitation cells contained zero values.
4. Nonzero precipitation fidelity has not yet been demonstrated.
5. Missing-cell preservation has not yet been demonstrated using an actual missing observation.
6. Only one small geographic bounding box was tested.
7. The experiment does not establish global retrieval performance or scientific validity of regional trends.

Further validation is necessary before treating Harmony regional retrieval as a broadly validated production capability.

## 8. Reproducibility and Provenance

The original global granule was retained.

The comparison used the exact corresponding original-grid cells, matching latitude and longitude coordinates.

The completed metadata-v4 ingestion pipeline was not modified.

The original EarthTrend project was not modified.

The temporary Harmony subset and diagnostic scripts were retained outside the project directory.

NASA credentials and authentication tokens are not included in this report.

## 9. Decision

D01 is closed as a successful proof of regional retrieval and exact data fidelity for the specified granule, time interval, bounding box, and precipitation variable.

No additional experiments or permanent implementation changes are authorized by this result alone.

The next experiment must be discussed and agreed upon separately.
