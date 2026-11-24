# D04 — Mixed Valid/Missing-Value Fidelity Validation

**Status: PASSED**

## 1. Objective

Validate whether NASA Harmony preserves genuine missing precipitation cells and valid zero-precipitation cells together within the same regional subset.

This experiment extends D03, which tested nonzero and missing-value preservation in separate regional subsets.

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

### Regional bounding box

| Parameter | Value |
|---|---:|
| West | 68.201 |
| East | 68.499 |
| South | -89.699 |
| North | -89.401 |

Harmony output: `earthtrend_d04_mixed.nc4`

- HTTP status: 200
- Content type: application/x-netcdf4
- Output size: 45,328 bytes
- HDF5 signature: valid

## 3. Source-to-Harmony comparison

Both the original HDF5 source and Harmony output contained a 3 × 3 grid.

Returned longitude centres:
- 68.25
- 68.35
- 68.45

Returned latitude centres:
- -89.65
- -89.549995
- -89.45

### Source array

```text
[[-9999.9 -9999.9     0. ]
 [-9999.9 -9999.9     0. ]
 [-9999.9 -9999.9     0. ]]
```

### Harmony returned array

```text
[[-9999.9 -9999.9     0. ]
 [-9999.9 -9999.9     0. ]
 [-9999.9 -9999.9     0. ]]
```

## 4. Validation results

| Validation criterion | Result |
|---|---|
| Source and returned shapes | Both (3, 3) |
| Coordinates match | PASS |
| Source missing cells | 6 |
| Returned missing cells | 6 |
| Missing masks identical | PASS |
| Valid cells | 3 |
| Valid zero cells | 3 |
| Valid nonzero cells | 0 |
| Valid values exactly equal | PASS |
| Fill value preserved | PASS |
| Maximum absolute difference | 0.0 |

Source and returned fill value:

`-9999.9`

All six missing cells were preserved, and all three valid zero values were reproduced exactly.

**D04 result: PASS**

## 5. Acceptance summary

- Regional retrieval completed successfully.
- Returned coordinates matched the corresponding original source-grid coordinates.
- Genuine missing values were preserved.
- Valid zero precipitation values were preserved.
- Missing-value masks were identical.
- Fill value was preserved.
- All valid values matched exactly.

## 6. Limitations and scientific safeguards

- The experiment used one original granule, one date, one half-hour interval, and one variable.
- The returned subset contained six missing cells and three valid zero cells.
- It did not contain valid nonzero precipitation values; nonzero fidelity was tested separately in D03.
- No conclusions are made about all dates, geographic regions, variables, or Harmony retrieval performance.
- Missing values are not treated as equivalent to zero precipitation.
- The original source granule and processed ingestion output were not modified.

## 7. Reproducibility artifacts

Original source:

`data/raw/gpm_imerg/3B-HHR.MS.MRG.3IMERG.20200101-S000000-E002959.0000.V07B.HDF5`

Temporary Harmony output:

`%TEMP%/earthtrend_d04_mixed.nc4`

Diagnostic scripts:
- `%TEMP%/earthtrend_d04_retrieve.py`
- `%TEMP%/earthtrend_d04_compare.py`

The comparison used source-grid coordinate matching, corresponding source-array indexing, fill-value normalization, missing-mask equality, and exact equality of valid precipitation values.

## 8. Conclusion

D04 demonstrated that NASA Harmony preserved the distinction between genuine missing precipitation cells and valid zero-precipitation cells within the same regional subset.

All nine returned cells matched their corresponding original HDF5 source cells exactly.

The experiment strengthens the evidence established by D01, D02, and D03 for the tested retrieval configuration.

**Overall D04 status: PASS.**