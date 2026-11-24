# D03 — Nonzero Precipitation and Missing-Value Fidelity Validation

**Status: PASSED for both tested cases**

## 1. Objective

Validate whether NASA Harmony regional retrieval preserves:
1. Actual nonzero GPM IMERG precipitation values.
2. Genuine missing precipitation cells and their missing-value mask.

This experiment extends D01 and D02, whose original test region contained only zero precipitation and no missing cells.

## 2. Locked test configuration

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

Two independent regional retrievals were performed.

### 2.1 Nonzero precipitation region

| Parameter | Value |
|---|---:|
| West | -170.099 |
| East | -169.801 |
| South | -68.999 |
| North | -68.701 |

Harmony output: `earthtrend_d03_nonzero.nc4`

- HTTP status: 200
- Content type: application/x-netcdf4
- Output size: 45,339 bytes
- HDF5 signature: valid

### 2.2 Missing-value region

| Parameter | Value |
|---|---:|
| West | 68.201 |
| East | 68.499 |
| South | -89.899 |
| North | -89.601 |

Harmony output: `earthtrend_d03_missing.nc4`

- HTTP status: 200
- Content type: application/x-netcdf4
- Output size: 45,323 bytes
- HDF5 signature: valid

## 3. Nonzero precipitation fidelity results

The original HDF5 source and Harmony output both contained 3 × 3 cells.

Returned longitude centres:
- -170.05
- -169.95
- -169.84999

Returned latitude centres:
- -68.95
- -68.85
- -68.75

All nine source cells contained valid, nonzero precipitation values.

| Validation | Result |
|---|---|
| Source and returned shapes | Both (3, 3) |
| Coordinates match | PASS |
| Source missing cells | 0 |
| Returned missing cells | 0 |
| Missing masks identical | PASS |
| Valid cells | 9 |
| Valid values exactly equal | PASS |
| Maximum absolute difference | 0.0 |

The source and returned precipitation arrays were exactly equal:

```text
[[0.41       0.47       0.35      ]
 [0.29999998 0.47       0.29999998]
 [0.35999998 0.41       0.41      ]]
```

**Result: PASS**

## 4. Missing-value preservation results

The original HDF5 source and Harmony output both contained 3 × 3 cells.

Returned longitude centres:
- 68.25
- 68.35
- 68.45

Returned latitude centres:
- -89.85
- -89.75
- -89.65

All nine source cells contained the genuine precipitation fill value.

| Validation | Result |
|---|---|
| Source and returned shapes | Both (3, 3) |
| Coordinates match | PASS |
| Source missing cells | 9 |
| Returned missing cells | 9 |
| Missing masks identical | PASS |
| Valid cells | 0 |
| Fill value preserved | PASS |

Source and returned fill value:

`-9999.9`

Both arrays contained nine missing cells, and their missing masks were identical.

A numerical difference for valid cells was not applicable because this test contained no valid cells.

**Result: PASS**

## 5. Acceptance summary

| Acceptance criterion | Result |
|---|---|
| Both regional requests successful | PASS |
| Valid NetCDF4/HDF5 outputs | PASS |
| Nonzero precipitation values preserved exactly | PASS |
| Nonzero-region coordinates preserved | PASS |
| Nonzero-region missing mask preserved | PASS |
| Genuine missing cells preserved | PASS |
| Missing-region coordinates preserved | PASS |
| Fill value preserved | PASS |

**Overall D03 result: PASS for both defined test cases.**

## 6. Limitations and scientific safeguards

- Both tests used one original granule, one date, one half-hour interval, and one precipitation variable.
- The nonzero test region contained nine valid nonzero cells; it did not contain missing cells.
- The missing-value test region contained nine missing cells; it did not contain valid cells.
- A mixed valid/missing neighborhood has not yet been tested.
- No conclusions are made about all dates, geographic regions, variables, or Harmony retrieval performance.
- Successful retrieval and exact fidelity in these tested cases do not establish universal retrieval correctness.
- Missing values are distinguished from valid zero precipitation values.
- The original source granule and existing processed ingestion output were not modified.

## 7. Reproducibility artifacts

Original source:

`data/raw/gpm_imerg/3B-HHR.MS.MRG.3IMERG.20200101-S000000-E002959.0000.V07B.HDF5`

Temporary Harmony outputs:
- `%TEMP%/earthtrend_d03_nonzero.nc4`
- `%TEMP%/earthtrend_d03_missing.nc4`

Diagnostic scripts:
- `%TEMP%/earthtrend_d03_retrieve.py`
- `%TEMP%/earthtrend_d03_compare.py`

The comparison used exact source-grid coordinate matching, corresponding source-array indexing, fill-value normalization, missing-mask equality, and exact equality of valid precipitation values.

## 8. Conclusion

D03 successfully demonstrated that NASA Harmony preserved actual nonzero precipitation values and genuine missing precipitation cells for the two tested regional subsets.

Both tests matched the corresponding original HDF5 source cells exactly, with zero numerical difference for valid cells and identical missing-value masks.

The result strengthens the evidence established by D01 and D02 while retaining the stated scope and limitations.