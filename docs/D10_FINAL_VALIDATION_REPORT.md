# D10 ? Multi-Date, Multi-Granule Harmony Fidelity Validation

**Final status: PASS**

## 1. Objective

Evaluate source-to-Harmony fidelity across multiple dates, consecutive GPM IMERG half-hourly granules, three spatial regions, and all three scientific variables. Each returned Harmony cell was mapped to its corresponding source HDF5 coordinate before comparison.

## 2. Dataset and scope

- Dataset: GPM IMERG Final Half-Hourly, collection `GPM_3IMERGHH`, V07.
- Variables: `Grid/precipitation`, `Grid/precipitationQualityIndex`, `Grid/randomError`.
- Dates tested: 20200201, 20200501, 20200801.
- Six source granules: two consecutive half-hourly granules per date, starting at 00:00 and 00:30 UTC.
- Three spatial validation regions: NONPOLAR, SOUTH_POLAR, NORTH_POLAR.
- Total: 13 region/granule cases and 39 variable comparisons.

## 3. Validation design

| Region | Source granules | Variables per granule | Comparisons |
|---|---:|---:|---:|
| NONPOLAR | 6 | 3 | 18 |
| SOUTH_POLAR | 6 | 3 | 18 |
| NORTH_POLAR | 1 | 3 | 3 |
| **Total** | **13 region/granule cases** | | **39** |

The first request was retrieved and validated as the pilot. The remaining 38 requests were processed sequentially from the locked manifest. Each successful response was validated before being saved. The batch stopped on a failed request; no failures occurred.

## 4. Acceptance checks

Each variable comparison was required to pass:

1. HTTP request success.
2. Expected NetCDF4 content type and valid HDF5 signature.
3. Returned data dimensions and shape consistency.
4. Unique mapping of returned longitude coordinates to source coordinates.
5. Unique mapping of returned latitude coordinates to source coordinates.
6. Matching source and returned timestamps.
7. Matching fill values.
8. Identical source and returned missing-value masks.
9. Matching valid values within absolute tolerance `1e-6`.
10. Matching Units attribute presence and value.
11. Matching LongName metadata.

The source variables use `(time, lon, lat)` array order. HDF5 dimension labels were blank in the inspected source files; array order was established from the source data and the pilot's returned dimension metadata. Returned coordinates were mapped to source indices rather than assuming the requested bounding box produced an identical extent.

## 5. Source metadata findings

| Variable | Units attribute | Fill value | LongName |
|---|---|---:|---|
| precipitation | `mm/hr` | `-9999.9` | Present |
| precipitationQualityIndex | Absent | `-9999.9` | Present |
| randomError | `mm/hr` | `-9999.9` | Present |

The quality-index variable's absent Units attribute was treated as an expected source property and checked for preservation.

## 6. Consolidated results

| Measure | Result |
|---|---:|
| Manifest requests | 39 |
| Pilot comparisons passed | 1 |
| Batch comparisons passed | 38 |
| Total comparisons passed | 39 / 39 |
| Failed comparisons | 0 |
| Expected output files present | 39 / 39 |
| Missing output files | 0 |
| Recorded batch validation checks passed | All |
| Maximum absolute difference | 0.0 |

Every recorded valid-value comparison had a maximum absolute difference of `0.0` in the reported precision. Missing masks, mapped coordinates, timestamps, fill values and checked metadata passed.

## 7. Per-comparison evidence

| # | Region | Granule | Variable | Returned shape | Valid cells | Missing cells | Max abs diff | Result |
|---:|---|---|---|---|---:|---:|---:|---|
| 1 | NONPOLAR | `20200201-S000000-E002959.0000.V07B.HDF5` | `precipitation` | `(1, 5, 3)` | 15 | 0 | 0.0 | PASS |
| 2 | NONPOLAR | `20200201-S000000-E002959.0000.V07B.HDF5` | `precipitationQualityIndex` | `(1, 5, 3)` | 15 | 0 | 0.0 | PASS |
| 3 | NONPOLAR | `20200201-S000000-E002959.0000.V07B.HDF5` | `randomError` | `(1, 5, 3)` | 15 | 0 | 0.0 | PASS |
| 4 | NONPOLAR | `20200201-S003000-E005959.0030.V07B.HDF5` | `precipitation` | `(1, 5, 3)` | 15 | 0 | 0.0 | PASS |
| 5 | NONPOLAR | `20200201-S003000-E005959.0030.V07B.HDF5` | `precipitationQualityIndex` | `(1, 5, 3)` | 15 | 0 | 0.0 | PASS |
| 6 | NONPOLAR | `20200201-S003000-E005959.0030.V07B.HDF5` | `randomError` | `(1, 5, 3)` | 15 | 0 | 0.0 | PASS |
| 7 | NONPOLAR | `20200501-S000000-E002959.0000.V07B.HDF5` | `precipitation` | `(1, 5, 3)` | 15 | 0 | 0.0 | PASS |
| 8 | NONPOLAR | `20200501-S000000-E002959.0000.V07B.HDF5` | `precipitationQualityIndex` | `(1, 5, 3)` | 15 | 0 | 0.0 | PASS |
| 9 | NONPOLAR | `20200501-S000000-E002959.0000.V07B.HDF5` | `randomError` | `(1, 5, 3)` | 15 | 0 | 0.0 | PASS |
| 10 | NONPOLAR | `20200501-S003000-E005959.0030.V07B.HDF5` | `precipitation` | `(1, 5, 3)` | 15 | 0 | 0.0 | PASS |
| 11 | NONPOLAR | `20200501-S003000-E005959.0030.V07B.HDF5` | `precipitationQualityIndex` | `(1, 5, 3)` | 15 | 0 | 0.0 | PASS |
| 12 | NONPOLAR | `20200501-S003000-E005959.0030.V07B.HDF5` | `randomError` | `(1, 5, 3)` | 15 | 0 | 0.0 | PASS |
| 13 | NONPOLAR | `20200801-S000000-E002959.0000.V07B.HDF5` | `precipitation` | `(1, 5, 3)` | 15 | 0 | 0.0 | PASS |
| 14 | NONPOLAR | `20200801-S000000-E002959.0000.V07B.HDF5` | `precipitationQualityIndex` | `(1, 5, 3)` | 15 | 0 | 0.0 | PASS |
| 15 | NONPOLAR | `20200801-S000000-E002959.0000.V07B.HDF5` | `randomError` | `(1, 5, 3)` | 15 | 0 | 0.0 | PASS |
| 16 | NONPOLAR | `20200801-S003000-E005959.0030.V07B.HDF5` | `precipitation` | `(1, 5, 3)` | 15 | 0 | 0.0 | PASS |
| 17 | NONPOLAR | `20200801-S003000-E005959.0030.V07B.HDF5` | `precipitationQualityIndex` | `(1, 5, 3)` | 15 | 0 | 0.0 | PASS |
| 18 | NONPOLAR | `20200801-S003000-E005959.0030.V07B.HDF5` | `randomError` | `(1, 5, 3)` | 15 | 0 | 0.0 | PASS |
| 19 | SOUTH_POLAR | `20200201-S000000-E002959.0000.V07B.HDF5` | `precipitation` | `(1, 5, 5)` | 15 | 10 | 0.0 | PASS |
| 20 | SOUTH_POLAR | `20200201-S000000-E002959.0000.V07B.HDF5` | `precipitationQualityIndex` | `(1, 5, 5)` | 15 | 10 | 0.0 | PASS |
| 21 | SOUTH_POLAR | `20200201-S000000-E002959.0000.V07B.HDF5` | `randomError` | `(1, 5, 5)` | 15 | 10 | 0.0 | PASS |
| 22 | SOUTH_POLAR | `20200201-S003000-E005959.0030.V07B.HDF5` | `precipitation` | `(1, 5, 5)` | 15 | 10 | 0.0 | PASS |
| 23 | SOUTH_POLAR | `20200201-S003000-E005959.0030.V07B.HDF5` | `precipitationQualityIndex` | `(1, 5, 5)` | 15 | 10 | 0.0 | PASS |
| 24 | SOUTH_POLAR | `20200201-S003000-E005959.0030.V07B.HDF5` | `randomError` | `(1, 5, 5)` | 15 | 10 | 0.0 | PASS |
| 25 | SOUTH_POLAR | `20200501-S000000-E002959.0000.V07B.HDF5` | `precipitation` | `(1, 5, 5)` | 15 | 10 | 0.0 | PASS |
| 26 | SOUTH_POLAR | `20200501-S000000-E002959.0000.V07B.HDF5` | `precipitationQualityIndex` | `(1, 5, 5)` | 15 | 10 | 0.0 | PASS |
| 27 | SOUTH_POLAR | `20200501-S000000-E002959.0000.V07B.HDF5` | `randomError` | `(1, 5, 5)` | 15 | 10 | 0.0 | PASS |
| 28 | SOUTH_POLAR | `20200501-S003000-E005959.0030.V07B.HDF5` | `precipitation` | `(1, 5, 5)` | 10 | 15 | 0.0 | PASS |
| 29 | SOUTH_POLAR | `20200501-S003000-E005959.0030.V07B.HDF5` | `precipitationQualityIndex` | `(1, 5, 5)` | 10 | 15 | 0.0 | PASS |
| 30 | SOUTH_POLAR | `20200501-S003000-E005959.0030.V07B.HDF5` | `randomError` | `(1, 5, 5)` | 10 | 15 | 0.0 | PASS |
| 31 | SOUTH_POLAR | `20200801-S000000-E002959.0000.V07B.HDF5` | `precipitation` | `(1, 5, 5)` | 10 | 15 | 0.0 | PASS |
| 32 | SOUTH_POLAR | `20200801-S000000-E002959.0000.V07B.HDF5` | `precipitationQualityIndex` | `(1, 5, 5)` | 10 | 15 | 0.0 | PASS |
| 33 | SOUTH_POLAR | `20200801-S000000-E002959.0000.V07B.HDF5` | `randomError` | `(1, 5, 5)` | 10 | 15 | 0.0 | PASS |
| 34 | SOUTH_POLAR | `20200801-S003000-E005959.0030.V07B.HDF5` | `precipitation` | `(1, 5, 5)` | 15 | 10 | 0.0 | PASS |
| 35 | SOUTH_POLAR | `20200801-S003000-E005959.0030.V07B.HDF5` | `precipitationQualityIndex` | `(1, 5, 5)` | 15 | 10 | 0.0 | PASS |
| 36 | SOUTH_POLAR | `20200801-S003000-E005959.0030.V07B.HDF5` | `randomError` | `(1, 5, 5)` | 15 | 10 | 0.0 | PASS |
| 37 | NORTH_POLAR | `20200801-S000000-E002959.0000.V07B.HDF5` | `precipitation` | `(1, 3, 5)` | 9 | 6 | 0.0 | PASS |
| 38 | NORTH_POLAR | `20200801-S000000-E002959.0000.V07B.HDF5` | `precipitationQualityIndex` | `(1, 3, 5)` | 9 | 6 | 0.0 | PASS |
| 39 | NORTH_POLAR | `20200801-S000000-E002959.0000.V07B.HDF5` | `randomError` | `(1, 3, 5)` | 9 | 6 | 0.0 | PASS |

## 8. Interpretation and limitations

D10 demonstrates exact source-to-Harmony value fidelity for all returned cells in the 39 tested variable comparisons across the selected dates, granules and spatial windows. It also demonstrates that the validation method can map returned coordinates to source coordinates when Harmony returns a spatial extent wider than the intended three-cell window.

This is evidence for the tested cases, not proof of universal fidelity for every GPM IMERG granule, date, region, variable, request geometry or Harmony processing condition. The experiment uses three selected dates, six source granules and three selected spatial windows. The NORTH_POLAR case covers one granule only. Broader temporal, geographic and boundary coverage would require separate experiments.

## 9. Reproducibility and artifacts

- Locked specification: `D10_MULTI_DATE_MULTI_GRANULE_VALIDATION_SPEC.md`
- Request manifest: `D10_HARMONY_REQUEST_MANIFEST.json`
- Batch validation results: `D10_HARMONY_BATCH_RESULTS.json`
- Batch script: `d10_harmony_batch.py`
- Pilot script: `d10_harmony_pilot.py`
- Pilot fidelity comparison: `d10_pilot_fidelity_comparison.py`
- Output directory: `data/processed/gpm_imerg/d10_harmony/`

The manifest contains 39 requests. The batch results contain the 38 remaining successful comparisons; the first pilot comparison is documented separately above and in its existing pilot evidence.

## 10. Final decision

**D10: PASS for all predefined tested cases.**

All 39 variable comparisons passed, all 39 expected NetCDF4 output files exist, and no batch failures were recorded. The D10 experiment is complete and its results are locked. No additional retrieval or re-comparison is required for this experiment.
