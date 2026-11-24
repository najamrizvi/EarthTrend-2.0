# D07 — Multi-Variable Temporal Fidelity Validation Results

**Project:** EarthTrend 2.0
**Experiment:** D07 — Multi-Variable Temporal Fidelity Validation
**Date:** 19 November 2026
**Dataset:** GPM IMERG Final Half-Hourly V07
**Collection:** `GPM_3IMERGHH`
**Collection version:** 07

## 1. Objective

Determine whether NASA Harmony preserves the original source values, coordinates, time information, missing-value representation, and variable metadata when retrieving multiple GPM IMERG variables from a second consecutive half-hourly granule.

D07 extends the temporal validation performed in D06. It evaluates precipitation, precipitation quality index, and random error for the same geographic region and observation interval.

## 2. Locked Validation Configuration

| Parameter | Value |
|---|---|
| Dataset | GPM IMERG Final Half-Hourly |
| Collection | GPM_3IMERGHH |
| Version | 07 |
| Source granule | `3B-HHR.MS.MRG.3IMERG.20200101-S003000-E005959.0030.V07B.HDF5` |
| Observation date | 2020-01-01 |
| Observation interval | 00:30–01:00 UTC |
| Western longitude | -152.099 |
| Eastern longitude | -151.801 |
| Southern latitude | 50.001 |
| Northern latitude | 50.299 |
| Output format | NetCDF4 |
| Reference | Original global HDF5 granule |

The geographic region was intentionally kept identical to D05 and D06 so that the temporal interval and source granule could be changed without changing the selected region.

## 3. Variables Evaluated

Three variables were included:

1. `Grid/precipitation`
2. `Grid/precipitationQualityIndex`
3. `Grid/randomError`

Precipitation was retrieved and independently validated in D06. It was included again in the D07 consolidated verification against the same original second granule. The quality index and random error were retrieved specifically for D07.

## 4. Original Source Inspection

The original second granule was inspected using HDF5.

The selected source coordinates were:

- Longitude centres: -152.05, -151.95, -151.84999
- Latitude centres: 50.05, 50.149998, 50.25

All three source variables had dimensions `(1, 3600, 1800)`, float32 data, and a fill value of approximately `-9999.9`.

### 4.1 Precipitation

Source values:

```text
[[0.39999998 0.11       0.11      ]
 [0.39999998 0.19999999 0.14999999]
 [0.16       0.19       0.24      ]]
```

- Valid cells: 9
- Missing cells: 0
- Units: mm/hr

### 4.2 Precipitation quality index

Source values:

```text
[[0.767 0.767 0.767]
 [0.767 0.767 0.767]
 [0.767 0.767 0.767]]
```

- Valid cells: 9
- Missing cells: 0
- Units attribute: Not present in the source
- LongName: Preserved

No units were inferred or assigned.

### 4.3 Random error

Source values:

```text
[[2.8799999 1.25      1.25     ]
 [2.8799999 1.8299999 1.52     ]
 [1.5899999 1.77       2.01     ]]
```

- Valid cells: 9
- Missing cells: 0
- Units: mm/hr
- LongName: Preserved

## 5. NASA Harmony Retrieval

The two additional variables were requested through the authenticated NASA Harmony regional coverage retrieval endpoint.

The retrieval used:

- The exact second source granule
- The locked D06 geographic bounding box
- The 00:30–01:00 UTC observation interval
- NetCDF4 output
- The corresponding variable selection

Both requests returned HTTP 200 and valid NetCDF4/HDF5 output.

| Variable | Output file | Size | Retrieval |
|---|---|---:|---|
| Precipitation quality index | `earthtrend_d07_precipitationQualityIndex.nc4` | 43,606 bytes | Successful |
| Random error | `earthtrend_d07_randomError.nc4` | 45,278 bytes | Successful |

The previously validated precipitation output was retained as:

`earthtrend_d06_regional.nc4`

No original source granule was modified.

## 6. Source-to-Harmony Fidelity Comparison

Each returned variable was compared against the corresponding cells in the original global HDF5 source.

The comparison evaluated:

1. Array shape
2. Longitude and latitude coordinates
3. Time coordinate
4. Fill value
5. Missing-value mask
6. Exact valid numerical values
7. Units metadata
8. LongName metadata

### 6.1 Precipitation

- Shape: PASS
- Coordinates: PASS
- Time: PASS
- Fill value: PASS
- Missing-value mask: PASS
- Valid values: PASS
- Units: PASS
- LongName: PASS
- Valid cells compared: 9
- Maximum absolute difference: 0.0

**Result: PASS**

### 6.2 Precipitation quality index

- Shape: PASS
- Coordinates: PASS
- Time: PASS
- Fill value: PASS
- Missing-value mask: PASS
- Valid values: PASS
- Units: PASS
- LongName: PASS
- Valid cells compared: 9
- Maximum absolute difference: 0.0

**Result: PASS**

### 6.3 Random error

- Shape: PASS
- Coordinates: PASS
- Time: PASS
- Fill value: PASS
- Missing-value mask: PASS
- Valid values: PASS
- Units: PASS
- LongName: PASS
- Valid cells compared: 9
- Maximum absolute difference: 0.0

**Result: PASS**

## 7. Consolidated Verification

A final consolidated comparison evaluated all three variables against the original second granule.

| Variable | Checks passed | Valid cells | Maximum absolute difference | Result |
|---|---:|---:|---:|---|
| Precipitation | 8/8 | 9 | 0.0 | PASS |
| Precipitation quality index | 8/8 | 9 | 0.0 | PASS |
| Random error | 8/8 | 9 | 0.0 | PASS |
| **Total** | **24/24** | **27** | **0.0** | **PASS** |

**Final consolidated output:**

```text
VARIABLES PASSED: 3 / 3
TOTAL VALID CELL COMPARISONS: 27
D07 FINAL RESULT: PASS
```

All 27 valid cell comparisons matched the corresponding original source values exactly.

## 8. D05–D07 Experimental Continuity

The experiments provide complementary evidence:

- **D05:** Geographic fidelity was evaluated in a nonpolar region using the first granule.
- **D06:** Temporal fidelity was evaluated in the same region using the second consecutive granule, with precipitation.
- **D07:** Multi-variable temporal fidelity was evaluated using the same second granule and region, covering precipitation, precipitation quality index, and random error.

This controlled progression changes the observation interval while maintaining the selected geography, then expands the variable coverage for the second interval.

## 9. Limitations

The PASS result applies to the exact tested granule, observation interval, geographic bounding box, and variables.

The D07 region contained nine valid cells per variable and no missing cells. Therefore:

- D07 does not independently establish missing-value fidelity for these three variables in this region.
- Mixed valid/missing and nonzero-value fidelity were investigated separately in D03 and D04.
- Only one second granule and one geographic region were evaluated.
- These results do not establish universal fidelity across every date, granule, region, or variable.
- The experiment does not establish broader retrieval performance or scientific accuracy of the underlying precipitation estimates.

## 10. Reproducibility Artifacts

**Original source granule:**

`data/raw/gpm_imerg/3B-HHR.MS.MRG.3IMERG.20200101-S003000-E005959.0030.V07B.HDF5`

**Retrieved outputs:**

- `%TEMP%/earthtrend_d07_precipitationQualityIndex.nc4`
- `%TEMP%/earthtrend_d07_randomError.nc4`
- `%TEMP%/earthtrend_d06_regional.nc4` (previously validated precipitation output)

**Diagnostic scripts:**

- `%TEMP%/earthtrend_d07_source_audit.py`
- `%TEMP%/earthtrend_d07_retrieval.py`
- `%TEMP%/earthtrend_d07_inspect.py`
- `%TEMP%/earthtrend_d07_compare.py`
- `%TEMP%/earthtrend_d07_final.py`

The original source granule remains unchanged.

## 11. Final Conclusion

**D07 RESULT: PASS**

NASA Harmony successfully retrieved the precipitation quality index and random error for the second consecutive GPM IMERG V07 granule. Their returned values, coordinates, time information, fill values, missing-value masks, and available variable metadata matched the original source.

The previously validated precipitation output also passed the consolidated comparison.

All three variables passed all eight comparison checks, with 27 valid regional cell comparisons and a maximum absolute numerical difference of zero.

D07 therefore provides additional, controlled evidence that NASA Harmony can preserve multiple GPM IMERG variables across the tested consecutive half-hourly observation intervals.

This conclusion remains limited to the exact experimental conditions documented above.
