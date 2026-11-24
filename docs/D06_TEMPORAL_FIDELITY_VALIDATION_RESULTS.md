# D06 — Temporal Fidelity Validation Results

**Project:** EarthTrend 2.0
**Experiment:** D06 — Temporal Generalization
**Status:** PASS
**Date performed:** 19 November 2026

## 1. Objective

Evaluate whether NASA Harmony can retrieve a regional GPM IMERG precipitation subset from a second consecutive half-hourly granule while preserving the original source-grid coordinates, missing-value representation, and valid precipitation measurements.

D06 extends the previous retrieval experiments by holding the geographic region constant and changing the observation interval.

## 2. Dataset and experimental configuration

| Parameter | Value |
|---|---|
| Dataset | GPM IMERG Final Half-Hourly |
| Collection | GPM_3IMERGHH |
| Collection version | 07 |
| Granule product version | V07B |
| Date | 2020-01-01 |
| Observation interval | 00:30–01:00 UTC |
| Variable | Grid/precipitation |
| Output format | NetCDF4 |
| Retrieval service | NASA Harmony |

**Source granule:**

`3B-HHR.MS.MRG.3IMERG.20200101-S003000-E005959.0030.V07B.HDF5`

**Regional bounding box:**

- West: -152.099°
- East: -151.801°
- South: 50.001°
- North: 50.299°

This is the same geographic region used in D05.

## 3. Source-grid inspection

The second original granule was inspected before retrieval.

| Source property | Result |
|---|---:|
| Global grid shape | 3600 × 1800 |
| Total grid cells | 6,480,000 |
| Missing cells | 28,829 |
| Valid cells | 6,451,171 |
| Nonzero valid cells | 626,378 |

The selected regional 3 × 3 source window contained:

- 9 valid cells
- 0 missing cells
- 9 nonzero precipitation cells

**Source precipitation array:**

```text
[[0.39999998 0.11       0.11      ]
 [0.39999998 0.19999999 0.14999999]
 [0.16       0.19       0.24      ]]
```

## 4. NASA Harmony retrieval

The regional subset was successfully retrieved using the authenticated Earthaccess HTTPS session.

| Retrieval check | Result |
|---|---|
| HTTP status | 200 |
| Content type | application/x-netcdf4 |
| Response size | 45,340 bytes |
| Output file | earthtrend_d06_regional.nc4 |
| File existence | Confirmed |
| HDF5 signature | Valid |

The returned NetCDF4 structure contained the expected precipitation dataset:

`Grid/precipitation`

Returned precipitation shape: `(1, 3, 3)`.

## 5. Source-to-Harmony fidelity comparison

The returned regional subset was compared directly against the corresponding cells in the original second granule.

| Validation | Source | Harmony | Result |
|---|---:|---:|---|
| Array shape | (3, 3) | (3, 3) | PASS |
| Longitude coordinates | Same | Same | PASS |
| Latitude coordinates | Same | Same | PASS |
| Fill value | -9999.900390625 | -9999.900390625 | PASS |
| Missing cells | 0 | 0 | PASS |
| Valid cells | 9 | 9 | PASS |
| Nonzero valid cells | 9 | 9 | PASS |
| Valid precipitation values | Identical | Identical | PASS |

**Maximum absolute difference:** 0.0

**Missing-value masks:** Identical.

**Coordinate comparison:** Exact match within the numerical comparison tolerance of 1e-5 degrees.

**Returned precipitation array:**

```text
[[0.39999998 0.11       0.11      ]
 [0.39999998 0.19999999 0.14999999]
 [0.16       0.19       0.24      ]]
```

The returned array matched the original source array exactly.

## 6. D05–D06 temporal comparison

D05 and D06 used the same geographic region, dataset collection, date, and precipitation variable.

| Parameter | D05 | D06 |
|---|---|---|
| Granule | First granule | Second granule |
| Observation interval | 00:00–00:30 UTC | 00:30–01:00 UTC |
| Geographic region | Same | Same |
| Regional grid | 3 × 3 | 3 × 3 |
| Valid cells | 9 | 9 |
| Nonzero cells | 8 | 9 |
| Source-to-Harmony comparison | PASS | PASS |

This provides a controlled two-interval temporal retrieval comparison at one fixed geographic location.

## 7. Final result

**D06 RESULT: PASS**

All five implemented comparison gates passed:

1. Source and returned array shapes match.
2. Geographic coordinates match.
3. Fill values match.
4. Missing-value masks match.
5. Valid precipitation values match exactly.

NASA Harmony successfully retrieved the second consecutive half-hourly GPM IMERG granule for the tested region without introducing numerical differences in the nine returned precipitation cells.

## 8. Limitations

- Only one additional granule and one observation interval were tested.
- Only one geographic region was used.
- Only the precipitation variable was evaluated in D06.
- All nine selected cells contained valid, nonzero precipitation.
- D06 does not independently test missing-value preservation in the second granule.
- These results do not establish universal temporal fidelity across all dates, regions, variables, or GPM IMERG granules.
- Broader validation is required before making general performance or reliability claims.

## 9. Reproducibility artifacts

Original source granule:

`data/raw/gpm_imerg/3B-HHR.MS.MRG.3IMERG.20200101-S003000-E005959.0030.V07B.HDF5`

Harmony output:

`%TEMP%/earthtrend_d06_regional.nc4`

Diagnostic scripts:

- `earthtrend_d06_scan.py`
- `earthtrend_d06_same_region.py`
- `earthtrend_d06_retrieval.py`
- `earthtrend_d06_inspect.py`
- `earthtrend_d06_compare.py`

All diagnostic scripts and retrieval output were kept in the temporary directory. The original granules and completed ingestion pipeline were not modified.

---

**Experiment status: D06 PASSED — Temporal Regional Fidelity Validated for the Tested Second Granule.**
