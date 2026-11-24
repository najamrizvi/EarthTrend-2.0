
import { useMemo } from 'react'
import './AIInsights.css'

const format = (value, digits = 4) =>
  Number.isFinite(value) ? value.toFixed(digits) : '—'

const getTimestamp = (item) => {
  if (item === null || item === undefined) return null

  const value = String(item)

  // Treat timezone-naive API timestamps as UTC.
  const hasTimezone = /(?:Z|[+-]\d{2}:\d{2})$/i.test(value)
  const date = new Date(hasTimezone ? value : `${value}Z`)

  return Number.isNaN(date.getTime()) ? null : date
}

export default function AIInsights({
  historicalData,
  historicalLoading,
  historicalError,
}) {
  const analysis = useMemo(() => {
    const timestamps = historicalData?.coordinates?.time
    const values = historicalData?.values

    if (!Array.isArray(values) || !Array.isArray(timestamps)) {
      return null
    }

    const records = []

    values.forEach((grid, timeIndex) => {
      if (!Array.isArray(grid)) return

      const cells = grid
        .flat(Infinity)
        .filter(
          (value) =>
            value !== null &&
            value !== undefined &&
            value !== '' &&
            Number.isFinite(Number(value))
        )
        .map(Number)

      if (!cells.length) return

      records.push({
        timestamp: getTimestamp(timestamps[timeIndex]),
        cells,
        mean:
          cells.reduce((sum, value) => sum + value, 0) /
          cells.length,
      })
    })

    if (!records.length) return null

    const observations = records.map((record) => record.mean)
    const sorted = [...observations].sort((a, b) => a - b)

    const mean =
      observations.reduce((sum, value) => sum + value, 0) /
      observations.length

    const sumSquares = observations.reduce(
      (sum, value) => sum + (value - mean) ** 2,
      0
    )

    const percentile = (array, p) => {
      const position = (array.length - 1) * p
      const lower = Math.floor(position)
      const upper = Math.ceil(position)
      const fraction = position - lower

      return (
        array[lower] * (1 - fraction) +
        array[upper] * fraction
      )
    }

    const wet = observations.filter((value) => value > 0)
    const wetThreshold = percentile(sorted, 0.95)

    const highObservations = records.filter(
      (record) =>
        record.mean > wetThreshold && record.mean > 0
    )

    const dailyTotals = new Map()

    records.forEach((record) => {
      if (!record.timestamp) return

      const day = record.timestamp.toISOString().slice(0, 10)

      dailyTotals.set(
        day,
        (dailyTotals.get(day) ?? 0) + record.mean * 0.5
      )
    })

    const daily = [...dailyTotals.entries()]
      .map(([date, total]) => ({ date, total }))
      .sort((a, b) => a.date.localeCompare(b.date))

    const cellsByIndex = new Map()

    records.forEach((record) => {
      record.cells.forEach((value, index) => {
        if (!cellsByIndex.has(index)) {
          cellsByIndex.set(index, [])
        }

        cellsByIndex.get(index).push(value)
      })
    })

    const spatial = [...cellsByIndex.entries()].map(
      ([index, cellValues]) => ({
        index,
        mean:
          cellValues.reduce((sum, value) => sum + value, 0) /
          cellValues.length,
        observations: cellValues.length,
      })
    )

    return {
      records,
      mean,
      minimum: sorted[0],
      maximum: sorted[sorted.length - 1],
      standardDeviation: Math.sqrt(
        sumSquares / observations.length
      ),
      wetCount: wet.length,
      dryCount: observations.length - wet.length,
      wetPercentage: (wet.length / observations.length) * 100,
      wetThreshold,
      highObservations,
      daily,
      spatial,
      units: historicalData?.units || 'mm/hr',
    }
  }, [historicalData])

  const formatValue = (value) => format(value, 4)

  return (
    <main className="ai-insights-page">
      <header className="ai-insights-header">
        <div>
          <span className="ai-insights-eyebrow">
            INTELLIGENCE & INTERPRETATION
          </span>

          <h1>AI Insights</h1>

          <p>
            Evidence-first analysis of historical precipitation
            observations, spatial variation and forecast evaluation.
          </p>
        </div>

        <div className="ai-insights-status">
          <span className="ai-insights-status-dot" />
          HISTORICAL EVIDENCE
        </div>
      </header>

      <section className="ai-insights-notice">
        <div className="ai-insights-notice-icon">✦</div>

        <div>
          <strong>
            Measured evidence, transparent interpretation
          </strong>

          <p>
            The statistics below are calculated from historical
            observations. High-value intervals use the dataset's
            95th percentile as a descriptive threshold, not a
            validated meteorological anomaly classification.
            No external AI interpretation engine is currently
            connected.
          </p>
        </div>
      </section>

      <section className="ai-insights-summary">
        <div className="ai-insights-section-heading">
          <div>
            <span>01 / HISTORICAL OVERVIEW</span>
            <h2>Thirty-day precipitation evidence</h2>
          </div>

          <span className="ai-insights-source-tag">
            JANUARY 2020 DATASET
          </span>
        </div>

        {historicalLoading ? (
          <div className="ai-insights-message">
            Loading validated historical observations...
          </div>
        ) : historicalError ? (
          <div className="ai-insights-message ai-insights-error">
            Historical data could not be retrieved. No historical
            conclusions are presented.
          </div>
        ) : !analysis ? (
          <div className="ai-insights-message">
            No compatible historical observations are available.
            The historical API response must include timestamps
            and gridded values.
          </div>
        ) : (
          <>
            <div className="ai-insights-metrics">
              <article>
                <span>VALID TIME STEPS</span>
                <strong>
                  {analysis.records.length.toLocaleString()}
                </strong>
                <small>
                  Time intervals with valid grid observations
                </small>
              </article>

              <article>
                <span>REGIONAL MEAN</span>
                <strong>{formatValue(analysis.mean)}</strong>
                <small>{analysis.units}</small>
              </article>

              <article>
                <span>MAXIMUM INTERVAL</span>
                <strong>{formatValue(analysis.maximum)}</strong>
                <small>Highest regional spatial mean</small>
              </article>

              <article>
                <span>STANDARD DEVIATION</span>
                <strong>
                  {formatValue(analysis.standardDeviation)}
                </strong>
                <small>
                  Temporal variability · {analysis.units}
                </small>
              </article>
            </div>

            <div
              className="ai-insights-evidence-grid"
              style={{ marginTop: 14 }}
            >
              <article>
                <span className="evidence-label">
                  WET INTERVALS
                </span>

                <strong>
                  {analysis.wetCount.toLocaleString()}
                </strong>

                <p>
                  {format(analysis.wetPercentage, 2)}% of valid
                  intervals had a regional mean greater than zero.
                </p>
              </article>

              <article>
                <span className="evidence-label">
                  ZERO-MEAN INTERVALS
                </span>

                <strong>
                  {analysis.dryCount.toLocaleString()}
                </strong>

                <p>
                  Intervals where the spatial mean was zero.
                  This does not necessarily mean every grid cell
                  was zero.
                </p>
              </article>
            </div>
          </>
        )}
      </section>

      {analysis && (
        <>
          <section className="ai-insights-analysis">
            <div className="ai-insights-section-heading">
              <div>
                <span>02 / TEMPORAL DISTRIBUTION</span>
                <h2>Daily precipitation accumulation</h2>
              </div>
            </div>

            <div className="ai-insights-safeguards">
              {analysis.daily.map((day) => (
                <article key={day.date}>
                  <span>{day.date}</span>

                  <div style={{ flex: 1 }}>
                    <strong>{format(day.total, 3)} mm</strong>

                    <p>
                      Sum of regional mean rates multiplied by
                      the 30-minute interval duration.
                    </p>
                  </div>
                </article>
              ))}
            </div>
          </section>

          <section className="ai-insights-analysis">
            <div className="ai-insights-section-heading">
              <div>
                <span>03 / HIGH-VALUE INTERVALS</span>
                <h2>Upper-tail observations</h2>
              </div>

              <span className="ai-insights-source-tag">
                95TH PERCENTILE
              </span>
            </div>

            <div className="ai-insights-message">
              <strong>
                Descriptive threshold:{' '}
                {formatValue(analysis.wetThreshold)} {analysis.units}
              </strong>

              <p>
                {analysis.highObservations.length.toLocaleString()}{' '}
                intervals exceeded this threshold and had a
                positive regional mean. These are statistical
                upper-tail observations, not independently
                confirmed extreme weather events.
              </p>
            </div>

            <div
              className="ai-insights-safeguards"
              style={{ marginTop: 12 }}
            >
              {analysis.highObservations
                .slice(0, 10)
                .map((record, index) => (
                  <article
                    key={`${record.timestamp?.toISOString() ?? index}`}
                  >
                    <span>{index + 1}</span>

                    <div>
                      <strong>
                        {record.timestamp
                          ? record.timestamp
                              .toISOString()
                              .replace('T', ' ')
                              .slice(0, 16) + ' UTC'
                          : 'Timestamp unavailable'}
                      </strong>

                      <p>
                        Regional mean: {formatValue(record.mean)}{' '}
                        {analysis.units}
                      </p>
                    </div>
                  </article>
                ))}
            </div>
          </section>

          <section className="ai-insights-analysis">
            <div className="ai-insights-section-heading">
              <div>
                <span>04 / SPATIAL COMPARISON</span>
                <h2>Grid-cell mean comparison</h2>
              </div>
            </div>

            <div className="ai-insights-evidence-grid">
              {analysis.spatial.map((cell) => (
                <article key={cell.index}>
                  <span className="evidence-label">
                    GRID CELL {cell.index + 1}
                  </span>

                  <strong>
                    {formatValue(cell.mean)} {analysis.units}
                  </strong>

                  <p>
                    {cell.observations.toLocaleString()} valid
                    measurements included in its mean.
                  </p>
                </article>
              ))}
            </div>
          </section>
        </>
      )}

      <section className="ai-insights-limitations">
        <div className="ai-insights-section-heading">
          <div>
            <span>05 / INTERPRETATION SAFEGUARDS</span>
            <h2>Scientific limitations</h2>
          </div>
        </div>

        <div className="ai-insights-safeguards">
          <article>
            <span>01</span>

            <div>
              <strong>Limited spatial coverage</strong>

              <p>
                This analysis represents a small four-cell
                equatorial region, not global precipitation
                conditions.
              </p>
            </div>
          </article>

          <article>
            <span>02</span>

            <div>
              <strong>Descriptive statistical thresholds</strong>

              <p>
                The upper-tail threshold does not establish a
                meteorological extreme or a causal explanation.
              </p>
            </div>
          </article>

          <article>
            <span>03</span>

            <div>
              <strong>Forecasts remain separate from observations</strong>

              <p>
                Forecast performance must be interpreted using its
                documented holdout evaluation, not historical
                descriptive statistics.
              </p>
            </div>
          </article>
        </div>
      </section>

      <footer className="ai-insights-footer">
        <span>EARTH TREND 2.0</span>

        <p>
          Evidence-led environmental intelligence · Scientific
          transparency
        </p>
      </footer>
    </main>
  )
}
