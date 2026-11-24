# D05 — Geographic Fidelity Validation

**Status: PASSED**

## 1. Objective

Evaluate whether NASA Harmony preserves GPM IMERG precipitation coordinates and values in a geographically different, non-polar region.

D05 extends the earlier regional retrieval experiments by testing a new geographic location with both valid zero and nonzero precipitation measurements.

## 2. Test configuration

| Parameter | Value |
|---|---|
| Dataset | GPM IMERG Final Half-Hourly |
| Collection | GPM_3IMERGHH |
| Collection version | 07 |
| Granule | 3B-HHR.MS.MRG.3IMERG.20200101-S000000-E002959.0000.V07B.HDF5 |
| Date | 2020-01-01 |
| Time interval | 00:00–00:30 UTC |
| Variable | Grid/precipitation |
| Output format | NetCDF4 |
| Reference | Original global HDF5 granule |

### Geographic test region

| Parameter | Value |
|---|---:|
| West | -152.099 |
| East | -151.801 |
| South | 50.001 |
| North | 50.299 |
| Centre longitude | -151.95 |
| Centre latitude | 50.149998 |

The candidate was selected through a source-grid scan, excluding the earlier D01 region and polar latitudes.

The selected 3 × 3 source window contained nine valid cells, including eight nonzero measurements and one valid zero.

## 3. Harmony retrieval

- HTTP status: 200
- Content type: application/x-netcdf4
- Response size: 45,337 bytes
- HDF5 signature: valid
- Temporary output: `%TEMP%/earthtrend_d05_regional.nc4`

## 4. Source-to-Harmony comparison

Both source and returned arrays had shape `(3, 3)`.

Returned longitude centres:

- -152.05
- -151.95
- -151.84999

Returned latitude centres:

- 50.05
- 50.149998
- 50.25

Coordinate comparison: PASS.

### Source precipitation array

```text
[[0.26999998 0.09999999 0.11      ]
 [0.09999999 0.         0.08      ]
 [0.16       0.09999999 0.19999999]]
```

### Harmony returned precipitation array

```text
[[0.26999998 0.09999999 0.11      ]
 [0.09999999 0.         0.08      ]
 [0.16       0.09999999 0.19999999]]
```

## 5. Validation results

| Validation criterion | Result |
|---|---|
| Source shape | (3, 3) |
| Returned shape | (3, 3) |
| Coordinates match | PASS |
| Source fill value | -9999.900390625 |
| Returned fill value | -9999.900390625 |
| Fill values match | PASS |
| Source missing cells | 0 |
| Returned missing cells | 0 |
| Missing masks identical | PASS |
| Valid cells | 9 |
| Valid zero cells | 1 |
| Valid nonzero cells | 8 |
| Valid values exactly match | PASS |
| Maximum absolute difference | 0.0 |

**D05 result: PASS**

## 6. Acceptance summary

- Regional Harmony retrieval succeeded.
- The returned grid matched the corresponding source-grid dimensions.
- Longitude and latitude coordinates matched.
- Fill-value metadata matched.
- All nine valid precipitation measurements were exactly equal.
- The valid zero measurement remained distinguishable from nonzero measurements.
- Maximum numerical difference was zero.

## 7. Limitations and scientific safeguards

- One granule, one date, one half-hour interval, one variable, and one geographic region were tested.
- The selected region contained no missing cells.
- Missing-value behavior was tested separately in D03 and D04.
- This experiment does not establish universal geographic fidelity across all GPM IMERG regions, dates, or granules.
- No claims are made about global retrieval performance or scientific accuracy of the underlying precipitation estimates.
- The original granule and processed ingestion pipeline were not modified.

## 8. Reproducibility artifacts

Original source:

`data/raw/gpm_imerg/3B-HHR.MS.MRG.3IMERG.20200101-S000000-E002959.0000.V07B.HDF5`

Temporary Harmony output:

`%TEMP%/earthtrend_d05_regional.nc4`

Diagnostic scripts:

- `%TEMP%/earthtrend_d05_scan.py`
- `%TEMP%/earthtrend_d05_median_scan.py`
- `%TEMP%/earthtrend_d05_candidate_inspect.py`
- `%TEMP%/earthtrend_d05_retrieve.py`
- `%TEMP%/earthtrend_d05_compare.py`

The comparison matched returned coordinates to the original grid, selected corresponding source cells, compared fill values and missing masks, and checked exact equality of all valid precipitation values.

## 9. Conclusion

D05 demonstrated exact source-to-Harmony precipitation fidelity for a geographically different, non-polar regional subset.

All nine valid cells matched the original source values exactly, including eight nonzero measurements and one valid zero.

The result extends the evidence from D01–D04 to a second geographically distinct test area.

**Overall D05 status: PASS.**