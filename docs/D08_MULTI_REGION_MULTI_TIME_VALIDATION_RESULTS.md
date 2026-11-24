# D08 — Multi-Region and Multi-Time Retrieval Validation Results

## 1. Objective

Evaluate GPM IMERG Final V07 regional retrieval fidelity across two geographically distinct regions and two consecutive half-hour observation intervals.

The experiment consolidates previous validated results and adds the previously untested Region A / second-granule combination.

## 2. Dataset and source

- Dataset: GPM IMERG Final Half-Hourly
- Collection: GPM_3IMERGHH
- Collection version: 07
- Product version: V07B
- Date: 2020-01-01
- Reference: Original global HDF5 granules

## 3. Controlled validation design

### Geographic regions

**Region A**
- Longitude: 68.30–68.40
- Latitude: 25.35–25.45
- Retrieved grid centres: 68.25, 68.35, 68.45 longitude; 25.35, approximately 25.45 latitude.

**Region B**
- Longitude: -152.099 to -151.801
- Latitude: 50.001–50.299
- Retrieved grid centres: -152.05, -151.95, -151.84999 longitude; 50.05, 50.149998, 50.25 latitude.

### Temporal intervals

- Time 1: 00:00–00:30 UTC
- Time 2: 00:30–01:00 UTC

### Validation matrix

| Region | Time 1 | Time 2 |
|---|---|---|
| Region A | D01/D02 | D08 |
| Region B | D05 | D06/D07 |

## 4. D08 new retrieval

Granule:

`3B-HHR.MS.MRG.3IMERG.20200101-S003000-E005959.0030.V07B.HDF5`

Variables retrieved:
1. Grid/precipitation
2. Grid/precipitationQualityIndex
3. Grid/randomError

All three Harmony requests returned HTTP 200 with NetCDF4 content and valid HDF5 signatures.

Output files:
- `earthtrend_d08_precipitation.nc4` — 45,254 bytes
- `earthtrend_d08_precipitationQualityIndex.nc4` — 43,602 bytes
- `earthtrend_d08_randomError.nc4` — 45,248 bytes

## 5. D08 source audit

The original second granule was inspected at Region A.

All three variables contained six valid cells and zero missing cells.

- Precipitation: six valid zeros, units mm/hr.
- Quality index: six values of 0.68600005; no units attribute.
- Random error: six values of 0.24 mm/hr.

The source and requested grid coordinates matched.

## 6. Source-to-Harmony fidelity results

| Check | Precipitation | Quality index | Random error |
|---|---|---|---|
| Shape | PASS | PASS | PASS |
| Coordinates | PASS | PASS | PASS |
| Time | PASS | PASS | PASS |
| Fill value | PASS | PASS | PASS |
| Missing mask | PASS | PASS | PASS |
| Valid values | PASS | PASS | PASS |
| Units | PASS | PASS | PASS |
| LongName | PASS | PASS | PASS |

Each variable contained six valid cells.

Maximum absolute numerical difference for each variable: 0.0.

All returned arrays exactly matched their corresponding source arrays.

## 7. Consolidated multi-region and multi-time evidence

The completed validation matrix combines:

- Region A / Time 1: D01 and D02.
- Region A / Time 2: D08.
- Region B / Time 1: D05.
- Region B / Time 2: D06 and D07.

The experiments collectively cover precipitation, precipitation quality index, and random error, with the specific variable coverage and cell counts recorded in their individual reports.

D08's new contribution is the successful source-to-Harmony comparison for all three variables in Region A during the second half-hour interval.

## 8. Final result

**D08 RESULT: PASS**

All three newly retrieved variables passed source-to-Harmony fidelity validation.

The 2 × 2 regional and temporal evidence matrix is complete for the tested regions and intervals.

## 9. Scientific limitations

- Only two geographic regions were tested.
- Only two consecutive half-hour intervals on 2020-01-01 were included.
- D08 Region A contained valid zero precipitation values, not nonzero precipitation.
- D08 did not independently test missing cells in its Region A subset.
- Missing-value and mixed valid/missing fidelity were separately examined in D03 and D04.
- The matrix consolidates previous experiments; it does not represent four independent new retrieval campaigns.
- These results do not establish universal fidelity across all GPM granules, dates, geographic regions, or precipitation conditions.

## 10. Reproducibility and provenance

Original granules remain unchanged.

Harmony outputs and comparison scripts were stored in the system temporary directory.

The following experiment reports provide supporting evidence:

- D01 — Regional Retrieval Validation
- D02 — Multi-Variable Regional Retrieval
- D03 — Nonzero and Missing-Value Fidelity
- D04 — Mixed Valid/Missing Fidelity
- D05 — Geographic Fidelity Validation
- D06 — Temporal Fidelity Validation
- D07 — Multi-Variable Temporal Fidelity

The completed ingestion pipeline was not modified during D08.

---

**Conclusion:** D08 successfully completes the planned two-region, two-interval validation matrix for the tested GPM IMERG Final V07 observations, supported by exact comparisons against the original global source granules.