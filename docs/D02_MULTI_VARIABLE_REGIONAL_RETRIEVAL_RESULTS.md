# D02 — Multi-Variable Regional Retrieval Validation

**Project:** EarthTrend 2.0
**Validation date:** 2026-11-18
**Status:** PASS — all three tested variables passed their individual acceptance checks.

## 1. Objective

Validate whether NASA Harmony can retrieve multiple scientific variables from the same GPM IMERG Final Half-Hourly V07 granule for an identical time interval and geographic subset.

Each returned variable was inspected and compared against the corresponding cells in the original global granule.

## 2. Locked experiment parameters

| Parameter | Value |
|---|---|
| Dataset | GPM IMERG Final Half-Hourly |
| Collection | GPM_3IMERGHH |
| Collection version | 07 |
| Product granule version | V07B |
| Date | 2020-01-01 |
| Time interval | 00:00–00:30 UTC |
| Granule | 3B-HHR.MS.MRG.3IMERG.20200101-S000000-E002959.0000.V07B.HDF5 |
| Requested west longitude | 68.30 |
| Requested east longitude | 68.40 |
| Requested south latitude | 25.35 |
| Requested north latitude | 25.45 |
| Output format | NetCDF4 |
| Reference | Original global HDF5 granule |

The same granule, time interval, and bounding box were retained across the tested variables.

## 3. Variables tested

1. `Grid/precipitation`
2. `Grid/precipitationQualityIndex`
3. `Grid/randomError`

The precipitation variable was validated in D01 and retained as the reference for this multi-variable experiment. The quality-index and random-error variables were additionally retrieved through the Harmony `parameter_vars` endpoint.

## 4. Retrieval results

| Variable | HTTP status | Content type | Output size |
|---|---:|---|---:|
| Grid/precipitation | 200 | application/x-netcdf4 | 45,254 bytes |
| Grid/precipitationQualityIndex | 200 | application/x-netcdf4 | 43,602 bytes |
| Grid/randomError | 200 | application/x-netcdf4 | 45,248 bytes |

All three outputs were verified as NetCDF4/HDF5 files.

Temporary output files were stored outside the project directory.

## 5. Coordinate and dimension validation

The two D02 variable outputs both contained:

- Variable shape: `(1, 3, 2)`
- Dimension order: `time,lon,lat`
- Latitude coordinate count: 2
- Longitude coordinate count: 3
- Time coordinate count: 1

Returned coordinates:

- Latitude: approximately `[25.35, 25.449999]`
- Longitude: `[68.25, 68.35, 68.45]`

The returned coordinate values were matched to their corresponding source-grid indices.

**Important spatial-selection observation:** Harmony returned grid cells intersecting the requested bounding box. Some returned cell centres therefore lie outside the numerical bbox boundaries. The comparison used the actual returned coordinates and corresponding original-grid cells, not an assumption that every returned centre must lie inside the bbox.

Coordinate comparisons passed.

## 6. Per-variable numerical validation

### 6.1 Precipitation

Reference validation: D01.

- Original and returned missing-value masks matched.
- Fill-value metadata matched.
- Coordinates matched.
- All six selected numerical cells matched exactly.
- Maximum absolute difference: `0.0`.
- All six selected precipitation values were `0.0 mm/hr`.

**Result: PASS**

### 6.2 Precipitation quality index

Variable: `Grid/precipitationQualityIndex`

- Original shape: `(1, 3600, 1800)`
- Returned shape: `(1, 3, 2)`
- Dimension order: `time,lon,lat`
- Fill value: `-9999.9`
- CodeMissingValue: `-9999.9`
- No units attribute in either original or returned variable.
- Scientific LongName preserved.
- Missing-value masks matched.
- All six numerical cells matched exactly.
- Maximum absolute difference: `0.0`.
- All six selected values: approximately `0.77300006`.

The original fill-value attribute was exposed as a scalar, while the returned attribute was exposed as a one-element array. Their normalized numerical values were equal.

**Result: PASS**

### 6.3 Random error

Variable: `Grid/randomError`

- Original shape: `(1, 3600, 1800)`
- Returned shape: `(1, 3, 2)`
- Dimension order: `time,lon,lat`
- Units: `mm/hr`
- Fill value: `-9999.9`
- CodeMissingValue: `-9999.9`
- Scientific LongName preserved.
- Missing-value masks matched.
- All six numerical cells matched exactly.
- Maximum absolute difference: `0.0`.
- All six selected values: `0.24 mm/hr`.

The original fill-value attribute was exposed as a scalar, while the returned attribute was exposed as a one-element array. Their normalized numerical values were equal.

**Result: PASS**

## 7. Acceptance matrix

| Acceptance criterion | Precipitation | Quality index | Random error |
|---|---|---|---|
| Successful retrieval | PASS | PASS | PASS |
| Correct dimensions and coordinates | PASS | PASS | PASS |
| Matching missing-value masks | PASS | PASS | PASS |
| Matching fill-value metadata | PASS | PASS | PASS |
| Exact numerical comparison | PASS | PASS | PASS |
| Relevant scientific metadata | PASS | PASS | PASS |

All three tested variables passed their individual acceptance checks.

## 8. Final conclusion

NASA Harmony successfully returned the tested GPM IMERG Final V07 regional subset for precipitation, precipitation quality index, and random error.

For the exact granule, date, time interval, and geographic subset tested:

- All three variables were available as NetCDF4/HDF5 outputs.
- Returned coordinates corresponded to the original source grid.
- Missing-value masks matched.
- Fill-value metadata matched after normalizing scalar and one-element-array representations.
- All six selected cells per variable matched the corresponding original-granule values exactly.
- Maximum absolute numerical difference was zero for each variable.
- Relevant scientific metadata, including random-error units, was preserved.

**D02 outcome: PASS for the exact tested case.**

## 9. Limitations and scientific safeguards

This experiment does not establish:

- General retrieval reliability across all GPM IMERG granules or dates.
- Performance across different geographic regions or bounding-box sizes.
- Fidelity for nonzero precipitation values across a broad range of conditions.
- Fidelity of actual missing cells in a test where selected cells contain missing values.
- Large-scale retrieval performance or production-level service reliability.
- Scientific validity of the variables beyond their verified agreement with the source granule.

The six-cell comparisons establish exact fidelity only for the selected cells in this specific test.

The returned grid-cell selection behaviour must be considered when designing downstream regional analysis.

No original project files, raw source granules, processed Zarr data, or completed ingestion code were modified during D02.

## 10. Reproducibility artifacts

Temporary diagnostic scripts and retrieved files were kept under the Windows temporary directory.

Key outputs:

- `earthtrend_d02_precipitationQualityIndex.nc4`
- `earthtrend_d02_randomError.nc4`
- `earthtrend_d02_inspect_quality.py`
- `earthtrend_d02_compare_quality.py`
- `earthtrend_d02_inspect_random_error.py`
- `earthtrend_d02_compare_random_error.py`

The original global granule remains the numerical reference.

---

**EarthTrend 2.0 — D02 validation completed.**
