# EarthTrend 2.0 — Consolidated GPM IMERG Validation Review

**Review date:** 19 November 2026
**Experiments reviewed:** D01–D09
**Dataset:** NASA GPM IMERG Final Half-Hourly V07
**Collection:** GPM_3IMERGHH
**Purpose:** Assess completed regional retrieval and source-to-Harmony fidelity experiments, identify evidence gaps, and determine whether additional experiments are justified.

---

## 1. Executive Summary

EarthTrend 2.0 has completed nine documented validation experiments evaluating NASA Harmony regional retrieval of GPM IMERG data.

The experiments demonstrate successful regional retrieval and exact source-to-Harmony numerical fidelity for the tested cases, including:

- Three principal GPM IMERG variables.
- Valid zero precipitation observations.
- Nonzero precipitation observations.
- Missing-value preservation.
- Mixed valid and missing cells.
- Different geographic regions.
- Two consecutive half-hour observation intervals.
- Multiple variables across multiple regions and times.

The completed experiments provide strong evidence for the exact tested configurations.

They do not establish universal fidelity across all GPM IMERG granules, dates, geographic regions, or Harmony selection boundaries.

**Overall assessment: The tested regional retrieval and data-fidelity capabilities have passed their defined checks. Broader generalization remains unverified.**

## 2. Consolidated Experiment Matrix

| ID | Experiment | Main coverage | Outcome |
|---|---|---|---|
| D01 | Regional retrieval validation | Precipitation, Region A, Time 1 | PASS |
| D02 | Multi-variable regional retrieval | Three variables, Region A, Time 1 | PASS |
| D03 | Nonzero and missing-value fidelity | Nonzero and fully missing precipitation regions | PASS |
| D04 | Mixed valid/missing fidelity | Valid zeros and missing precipitation cells in one subset | PASS |
| D05 | Geographic fidelity | Nonpolar Region B, Time 1, nonzero precipitation | PASS |
| D06 | Temporal fidelity | Region B, Time 2, precipitation | PASS |
| D07 | Multi-variable temporal fidelity | Three variables, Region B, Time 2 | PASS |
| D08 | Multi-region multi-time validation | Regions A and B, two intervals, three variables | PASS |
| D09 | Multi-variable missing-value fidelity | Three variables, mixed valid/missing cells | PASS |

**Document status:** All nine Markdown reports are present and verified in `docs`.

## 3. Geographic and Temporal Coverage

### Region A

Approximate location: 68.35°E, 25.40°N.

- Time 1: 2020-01-01, 00:00–00:30 UTC.
- Time 2: 2020-01-01, 00:30–01:00 UTC.

Coverage:
- D01 and D02 tested the first interval.
- D08 added the second interval.

### Region B

Approximate location: 151.95°W, 50.15°N.

- Time 1: 2020-01-01, 00:00–00:30 UTC.
- Time 2: 2020-01-01, 00:30–01:00 UTC.

Coverage:
- D05 tested the first interval.
- D06 and D07 tested the second interval.
- D08 consolidated the two-region, two-time matrix.

### Polar missing-value test region

Approximate location: 179.85°W, 89.45°N.

- D09 used the first half-hour granule.
- All three variables were tested together.
- Harmony returned a 3 × 5 grid rather than the intended 3 × 3 latitude selection.
- Every returned cell was mapped to the original source grid and verified.

This additional region provides a useful test of missing-value behavior at high latitude, but it does not establish general polar-region performance.

## 4. Variable Coverage

| Variable | Tested experiments | Evidence |
|---|---|---|
| `Grid/precipitation` | D01–D09 | Zero, nonzero, missing, mixed masks, geographic and temporal fidelity |
| `Grid/precipitationQualityIndex` | D02, D07, D08, D09 | Multi-region, multi-time, valid-value and missing-value preservation |
| `Grid/randomError` | D02, D07, D08, D09 | Multi-region, multi-time, valid-value and missing-value preservation |

D07 used the precipitation output already validated in D06 while retrieving and validating the additional variables. D08 and D09 provide further consolidated multi-variable checks.

## 5. Key Scientific and Technical Evidence

### A. Numerical fidelity

The completed comparisons repeatedly demonstrated exact equality between valid source values and Harmony-returned values.

Reported maximum absolute numerical differences in the tested comparisons: **0.0**.

### B. Missing-value preservation

The experiments established that:

- Fill values were preserved.
- Missing masks matched the original source.
- Valid zero precipitation remained distinguishable from missing precipitation.
- Mixed valid/missing cells were preserved in the same regional subset.
- D09 verified missing-value behavior across all three variables together.

### C. Metadata and coordinates

The relevant tests checked:

- Longitude coordinates.
- Latitude coordinates.
- Observation timestamps.
- Fill values.
- Units.
- Long names.
- Dataset shape.

### D. Regional retrieval

The experiments demonstrate that Harmony can return small NetCDF4 regional subsets from the tested original global GPM IMERG granules.

D01's original comparison involved a six-cell subset against a global grid of 6,480,000 cells.

This is evidence of successful regional subsetting, not a comprehensive performance benchmark.

## 6. Important Limitations

The following limitations must remain visible in the project documentation.

1. **Limited dates:** The current matrix uses one date, 2020-01-01.
2. **Limited granules:** Two consecutive half-hour granules were tested.
3. **Limited temporal coverage:** Two adjacent observation intervals do not establish long-term temporal reliability.
4. **Limited geographic sampling:** Only a small number of regional subsets were examined.
5. **Boundary behavior:** D09 returned five latitude rows rather than the three intended rows. All returned cells matched the source, but selection extent requires further investigation.
6. **Missing-value generalization:** The tested missing-value patterns do not establish behavior for every missing-data configuration.
7. **Nonzero precipitation coverage:** Nonzero precipitation fidelity was demonstrated in separate tests, but D09's valid precipitation cells were all zero.
8. **Performance:** No systematic latency, throughput, concurrency, or large-scale retrieval benchmark has been completed.

These are evidence gaps, not failures of the completed experiments.

## 7. Remaining Evidence Gaps and Priorities

| Priority | Evidence gap | Why it matters |
|---|---|---|
| High | More dates and granules | Establish whether results generalize beyond one date and two granules |
| High | Different missing-value patterns across variables | Test whether each variable's independent mask is preserved when masks differ |
| High | Regional selection boundaries | Understand the extra latitude rows observed in D09 |
| Medium | More geographic regions | Increase confidence across different latitudes and longitudes |
| Medium | Longer temporal separation | Test granules beyond consecutive half-hour intervals |
| Medium | Systematic retrieval performance | Establish realistic data-transfer and processing costs |

## 8. Recommended Next Experiment

D10 should not be started merely because D09 is complete.

The strongest next candidate is a **multi-granule, multi-date fidelity validation**.

Suggested objective:

Validate the same three variables against original source granules from additional dates, using controlled regional subsets and consistent source-to-Harmony comparison checks.

The test should:

- Use additional original granules.
- Preserve source files unchanged.
- Include more than one observation date.
- Include valid, missing, and nonzero values where available.
- Compare each returned coordinate to the exact source-grid cell.
- Check missing masks independently for each variable.
- Record boundary-selection behavior.
- Avoid treating multiple cells from one granule as independent temporal observations.

The specific granules, regions, and dates should be selected only after inspecting the available source data.

This experiment is recommended for future work, not authorized or executed as part of D01–D09.

## 9. Current Decision

**D01–D09: COMPLETE AND DOCUMENTED.**

The tested GPM IMERG regional retrieval and fidelity checks passed.

No evidence currently justifies changing the completed ingestion pipeline.

The next development stage should build on the validated ingestion and retrieval foundations while preserving the distinction between demonstrated behavior and untested generalization.

## 10. Final Assessment

EarthTrend 2.0 has progressed beyond simply demonstrating that NASA Harmony can return regional data.

The completed work now includes source-to-output verification of numerical values, coordinates, timestamps, missing-value masks, and relevant metadata across three GPM IMERG variables.

The next phase should strengthen generalization across dates and granules, investigate boundary selection, and eventually establish reproducible retrieval-performance measurements.

**Final review status: D01–D09 consolidated review complete.**

**No additional experiment executed during this review.**


---

# D01?D10 Consolidated Review Addendum

## 11. D10 ? Multi-Date, Multi-Granule Validation

**Status: COMPLETE ? PASS**

D10 extended the earlier validation work across three observation dates and six original GPM IMERG V07B granules.

### 11.1 Dataset and temporal coverage

| Observation date | Granules |
|---|---:|
| 2020-02-01 | 2 consecutive half-hourly granules |
| 2020-05-01 | 2 consecutive half-hourly granules |
| 2020-08-01 | 2 consecutive half-hourly granules |
| **Total** | **6 granules** |

The three tested variables were:

- `Grid/precipitation`
- `Grid/precipitationQualityIndex`
- `Grid/randomError`

### 11.2 Regional and comparison coverage

| Region | Granule-variable comparisons |
|---|---:|
| Nonpolar region | 18 |
| Southern polar region | 18 |
| Northern polar region | 3 |
| **Total** | **39** |

The nonpolar and southern polar regions were evaluated across all six granules and all three variables. The northern polar case was evaluated for all three variables in the first August granule.

### 11.3 Validation results

The first Harmony retrieval was independently validated as the pilot. The remaining 38 requests were executed sequentially using the locked manifest.

All 39 comparisons passed the recorded checks:

- Successful HTTP response and expected NetCDF4 content type.
- Valid NetCDF4/HDF5 output.
- Returned dimensions and shape.
- Longitude and latitude mapping to original source-grid coordinates.
- Timestamp equality.
- Fill-value metadata.
- Missing-mask equality.
- Numerical equality of valid source and returned values.
- Units attribute presence and value, including the absent Units attribute for the quality index.
- LongName metadata equality.

**Maximum absolute difference across every comparison: 0.0.**

### 11.4 Output integrity

The final integrity check confirmed:

| Integrity measure | Result |
|---|---:|
| Manifest requests | 39 |
| Expected output files found | 39 |
| Missing output files | 0 |
| Batch completed records | 38 |
| Batch failed records | 0 |
| Pilot output | Present |
| Batch status | ALL_38_PASSED |
| Final integrity result | PASS |

The pilot was counted separately from the 38 batch requests.

### 11.5 Harmony selection behavior

The pilot demonstrated that Harmony may return a spatial selection larger than the initially intended three-cell longitude window. The returned coordinates were mapped to their exact source-grid indices, and every returned cell matched the original source.

This is an important methodological safeguard: validation must compare the actual returned coordinates against the source grid rather than assume that the requested bounding box produces an identical array extent.

The D10 cases passed their coordinate and value comparisons. These observations do not establish universal boundary-selection behavior for all requests.

## 12. Updated Scientific Assessment

D10 adds evidence beyond the original D01?D09 test scope:

- Multiple observation dates were tested.
- Six source granules were used.
- Three geographic test regions were included.
- All three GPM IMERG variables were compared.
- Valid values and missing masks were checked against original source data.
- Every recorded comparison passed with zero maximum absolute numerical difference.

The combined D01?D10 evidence supports successful regional retrieval and source-to-Harmony fidelity for the specific tested cases.

It does not establish universal fidelity across all dates, granules, regions, variables, or possible missing-data patterns.

## 13. Remaining Evidence Gaps

D10 reduces the earlier evidence gaps but does not eliminate them.

| Priority | Remaining gap | Reason |
|---|---|---|
| High | Broader date and granule coverage | Six granules across three dates are still a limited sample |
| High | Independent missing-mask patterns | Tested variables shared missing masks in the inspected source granules |
| High | Boundary-selection characterization | Additional tests are needed to characterize Harmony selection expansion |
| Medium | Broader geographic coverage | More regions and grid configurations are needed |
| Medium | Longer temporal continuity | Longer sequences and nonconsecutive granules remain untested |
| Medium | Retrieval performance | No systematic latency, throughput, concurrency, or scaling benchmark has been completed |
| Medium | Operational robustness | Retry behavior, service interruptions, and larger workloads need separate evaluation |

These are future evidence gaps, not failures of D01?D10.

## 14. Updated Development Decision

**D01?D10: COMPLETE AND DOCUMENTED.**

The multi-date, multi-granule validation recommended in the original D01?D09 review has now been executed successfully as D10.

The original recommendation to conduct D10 is therefore superseded by this completed evidence.

The next phase should shift from repeated fidelity experiments toward controlled development of the EarthTrend 2.0 application, building on the existing ingestion and retrieval foundations.

Development should preserve the following safeguards:

1. Do not modify the completed ingestion pipeline without a demonstrated requirement.
2. Keep original NASA source granules unchanged.
3. Preserve reproducibility and source-to-output traceability.
4. Distinguish validated behavior from assumptions and untested capabilities.
5. Add application features incrementally with independent tests.

### Final assessment

EarthTrend 2.0 has completed ten documented validation stages covering regional retrieval, multi-variable handling, numerical fidelity, missing-value preservation, geographic and temporal fidelity, and multi-date, multi-granule testing.

The next project milestone is application development and integration, followed by dedicated operational and performance testing.

**Final consolidated review status: D01?D10 COMPLETE.**

**D10 result: 39/39 comparisons passed; final integrity check passed.**
