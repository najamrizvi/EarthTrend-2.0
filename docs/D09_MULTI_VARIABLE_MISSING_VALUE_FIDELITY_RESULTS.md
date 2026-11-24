# D09 — Multi-Variable Missing-Value Fidelity Validation Results

**Project:** EarthTrend 2.0
**Experiment:** D09 — Multi-Variable Missing-Value Fidelity
**Date:** 19 November 2026
**Dataset:** GPM IMERG Final Half-Hourly V07
**Collection:** GPM_3IMERGHH
**Granule:** `3B-HHR.MS.MRG.3IMERG.20200101-S000000-E002959.0000.V07B.HDF5`

## 1. Objective

Determine whether NASA Harmony preserves valid observations and missing-value information independently across all three principal GPM IMERG variables within the same regional subset:

1. `Grid/precipitation`
2. `Grid/precipitationQualityIndex`
3. `Grid/randomError`

The experiment specifically tests whether valid zero precipitation values remain distinguishable from missing observations, while also verifying the quality-index and random-error values.

## 2. Test Configuration

| Parameter | Value |
|---|---|
| Dataset | GPM IMERG Final Half-Hourly |
| Collection | GPM_3IMERGHH |
| Collection version | 07 |
| Granule | First 2020-01-01 half-hour granule |
| Date | 2020-01-01 |
| Observation interval | 00:00–00:30 UTC |
| Target longitude centre | -179.85° |
| Target latitude centre | 89.45° |
| Intended longitude centres | -179.95°, -179.85°, -179.75° |
| Intended latitude centres | 89.35°, 89.45°, 89.549995° |
| Output format | NetCDF4 |
| Reference | Original global HDF5 granule |

The original granule was retained unchanged and used as the source of truth.

## 3. Source Data Inspection

The selected source region contained the following three-variable pattern.

### Precipitation

- 6 valid cells, all with precipitation equal to 0.0 mm/hr.
- 3 missing cells.
- Fill value: `-9999.900390625`.

### Precipitation quality index

- 6 valid cells, each with value approximately `0.193`.
- 3 missing cells.
- No units attribute in the source dataset.
- Fill value: `-9999.900390625`.

### Random error

- 6 valid cells, each with value approximately `0.24 mm/hr`.
- 3 missing cells.
- Units: `mm/hr`.
- Fill value: `-9999.900390625`.

All three variables shared the same source missing-value pattern.

## 4. Harmony Retrieval

The three variables were retrieved independently using the NASA Harmony regional coverage endpoint and an authenticated Earthaccess session.

| Variable | HTTP status | Content type | Output size | Retrieval |
|---|---:|---|---:|---|
| precipitation | 200 | application/x-netcdf4 | 45,349 bytes | PASS |
| precipitationQualityIndex | 200 | application/x-netcdf4 | 43,645 bytes | PASS |
| randomError | 200 | application/x-netcdf4 | 45,291 bytes | PASS |

All three outputs passed the HDF5 signature check.

## 5. Returned Coordinate and Shape Inspection

Harmony returned the following coordinates for all three variables:

**Longitude:**
-179.95°, -179.85°, -179.75°

**Latitude:**
89.25°, 89.35°, 89.45°, 89.549995°, 89.65°

**Time:** `[1261872000]`

**Returned data shape:** `(1, 3, 5)` for each variable.

The returned latitude selection contained five rows rather than the three intended latitude centres. This boundary-selection behaviour was recorded rather than silently cropping the additional rows.

## 6. Full Returned-Grid Source Comparison

Every returned longitude and latitude coordinate was mapped to its corresponding source-grid index in the original HDF5 granule.

The complete returned 3 × 5 arrays were then compared against the corresponding original source cells.

### Precipitation

- Source missing cells: 6
- Harmony missing cells: 6
- Source valid cells: 9
- Harmony valid cells: 9
- Missing masks: identical
- Valid values: exact match
- Maximum absolute difference: 0.0
- Units: `mm/hr` preserved
- Long name: preserved

**Result: PASS**

### Precipitation quality index

- Source missing cells: 6
- Harmony missing cells: 6
- Source valid cells: 9
- Harmony valid cells: 9
- Missing masks: identical
- Valid values: exact match
- Maximum absolute difference: 0.0
- Units: no units attribute in either source or output
- Long name: preserved

**Result: PASS**

### Random error

- Source missing cells: 6
- Harmony missing cells: 6
- Source valid cells: 9
- Harmony valid cells: 9
- Missing masks: identical
- Valid values: exact match
- Maximum absolute difference: 0.0
- Units: `mm/hr` preserved
- Long name: preserved

**Result: PASS**

## 7. Consolidated Validation

| Validation | Precipitation | Quality index | Random error |
|---|---|---|---|
| Shape | PASS | PASS | PASS |
| Longitude coordinates | PASS | PASS | PASS |
| Latitude coordinates | PASS | PASS | PASS |
| Timestamp | PASS | PASS | PASS |
| Fill value | PASS | PASS | PASS |
| Missing-value mask | PASS | PASS | PASS |
| Valid numerical values | PASS | PASS | PASS |
| Units | PASS | PASS | PASS |
| Long name | PASS | PASS | PASS |

**Variables passed:** 3 / 3
**Total returned cells compared:** 45
**Valid cell comparisons:** 27
**Missing cells preserved:** 18
**Maximum absolute numerical difference:** 0.0

## 8. Interpretation

The experiment demonstrates that, for this tested granule and regional subset, Harmony preserved the source values and missing-value masks independently across precipitation, precipitation quality index, and random error.

Importantly, valid zero precipitation values remained valid observations and were not converted into missing values.

The quality index and random-error variables also retained their valid numerical values and their source missing-value locations.

Harmony returned two additional latitude rows beyond the three intended target rows. All returned rows were independently mapped to the original granule and verified successfully. This is recorded as a selection-extent observation, not a fidelity failure.

## 9. Limitations

This validation is restricted to:

- One GPM IMERG granule.
- One observation interval on 2020-01-01.
- One small regional subset near 89.45°N.
- Three variables.
- The specific returned 3 × 5 grid.

The valid precipitation observations in this test were all zero. Therefore, D09 does not establish nonzero precipitation fidelity. Nonzero precipitation fidelity was separately demonstrated in D03 and D05.

The experiment does not establish universal fidelity across all dates, regions, granules, or geographic boundaries. Additional testing would be required before making such claims.

## 10. Final Decision

**D09 RESULT: PASS**

All three variables passed the complete source-to-Harmony comparison across every returned cell.

The experiment confirms exact preservation of the tested valid values, missing-value masks, coordinates, timestamps, fill values, units, and long names.

The observed latitude-selection expansion is documented as a limitation of the tested regional selection behaviour.

**Conclusion:** D09 provides additional evidence that NASA Harmony can preserve multi-variable GPM IMERG data fidelity, including the distinction between valid zero precipitation and missing observations, for the exact tested case.
