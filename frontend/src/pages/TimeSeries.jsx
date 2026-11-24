
import './TimeSeries.css'

function isValidNumber(value) {
  return (
    value !== null &&
    value !== undefined &&
    value !== '' &&
    Number.isFinite(Number(value))
  )
}

function getObservationCells(data) {
  const latitudes = data?.coordinates?.latitude ?? []
  const longitudes = data?.coordinates?.longitude ?? []
  const rawValues = data?.values ?? []

  const cells = []

  if (!Array.isArray(latitudes) || !Array.isArray(longitudes)) {
    return cells
  }

  latitudes.forEach((latitude, latIndex) => {
    longitudes.forEach((longitude, lonIndex) => {
      const value = Array.isArray(rawValues[latIndex])
        ? rawValues[latIndex][lonIndex]
        : null

      cells.push({
        id: `${latIndex}-${lonIndex}`,
        latitude,
        longitude,
        value: isValidNumber(value) ? Number(value) : null,
      })
    })
  })

  return cells
}

function getHistoricalObservations(data) {
  const timestamps = data?.coordinates?.time ?? []
  const rawValues = data?.values ?? []

  if (!Array.isArray(timestamps) || !Array.isArray(rawValues)) {
    return []
  }

  return timestamps.map((timestamp, index) => {
    const values = Array.isArray(rawValues[index])
      ? rawValues[index].flat(Infinity)
      : []

    const validValues = values
      .filter(isValidNumber)
      .map(Number)

    const mean = validValues.length
      ? validValues.reduce((sum, value) => sum + value, 0) /
        validValues.length
      : null

    return {
      index,
      timestamp,
      mean,
      validCells: validValues.length,
      missingCells: values.length - validValues.length,
    }
  })
}

function formatValue(value, digits = 3) {
  return value === null || !isValidNumber(value)
    ? '—'
    : Number(value).toFixed(digits)
}

function formatTimestamp(timestamp) {
  if (!timestamp) return 'Unknown time'

  return String(timestamp)
    .replace('T', ' ')
    .replace('Z', ' UTC')
    .replace('.000', '')
}

function formatClock(timestamp) {
  if (!timestamp) return ''

  return String(timestamp).slice(11, 16)
}

function HistoricalChart({ observations, units }) {
  const valid = observations.filter(
    (item) => item.mean !== null
  )

  if (valid.length < 2) {
    return (
      <div className="timeseries-empty">
        At least two valid historical observations are required
        to draw a trend.
      </div>
    )
  }

  const width = 1000
  const height = 320
  const left = 65
  const right = 25
  const top = 25
  const bottom = 55

  const values = valid.map((item) => item.mean)
  const minimum = Math.min(...values)
  const maximum = Math.max(...values)
  const range = maximum - minimum || 1

  const x = (index) =>
    left +
    (index / Math.max(observations.length - 1, 1)) *
      (width - left - right)

  const y = (value) =>
    top +
    ((maximum - value) / range) *
      (height - top - bottom)

  const points = valid
    .map((item) => `${x(item.index)},${y(item.mean)}`)
    .join(' ')

  const yTicks = Array.from(
    { length: 5 },
    (_, index) => maximum - (range * index) / 4
  )

  const xTicks = [
    0,
    Math.floor((observations.length - 1) / 4),
    Math.floor((observations.length - 1) / 2),
    Math.floor(((observations.length - 1) * 3) / 4),
    observations.length - 1,
  ]

  return (
    <div style={{ width: '100%', overflowX: 'auto' }}>
      <svg
        viewBox={`0 0 ${width} ${height}`}
        role="img"
        aria-label="Historical precipitation spatial mean over time"
        style={{
          display: 'block',
          width: '100%',
          minWidth: '520px',
          height: 'auto',
        }}
      >
        {yTicks.map((tick, index) => (
          <g key={index}>
            <line
              x1={left}
              x2={width - right}
              y1={y(tick)}
              y2={y(tick)}
              stroke="rgba(150,170,200,0.18)"
              strokeDasharray="4 5"
            />
            <text
              x={left - 12}
              y={y(tick) + 4}
              textAnchor="end"
              fill="#91a3bb"
              fontSize="12"
            >
              {tick.toFixed(3)}
            </text>
          </g>
        ))}

        <line
          x1={left}
          x2={width - right}
          y1={height - bottom}
          y2={height - bottom}
          stroke="rgba(150,170,200,0.4)"
        />

        {xTicks.map((index) => (
          <g key={index}>
            <line
              x1={x(index)}
              x2={x(index)}
              y1={height - bottom}
              y2={height - bottom + 5}
              stroke="#91a3bb"
            />
            <text
              x={x(index)}
              y={height - bottom + 24}
              textAnchor="middle"
              fill="#91a3bb"
              fontSize="12"
            >
              {formatClock(observations[index]?.timestamp)}
            </text>
          </g>
        ))}

        <polyline
          points={points}
          fill="none"
          stroke="#00e5ff"
          strokeWidth="3"
          strokeLinejoin="round"
          strokeLinecap="round"
        />

        {valid.map((item) => (
          <circle
            key={item.index}
            cx={x(item.index)}
            cy={y(item.mean)}
            r="3"
            fill="#00e5ff"
            stroke="#07111f"
            strokeWidth="1"
          >
            <title>
              {formatTimestamp(item.timestamp)}: {formatValue(item.mean)} {units}
            </title>
          </circle>
        ))}

        <text
          x={left}
          y="13"
          fill="#91a3bb"
          fontSize="11"
        >
          {units}
        </text>
      </svg>

      <p
        style={{
          textAlign: 'center',
          color: '#91a3bb',
          fontSize: '11px',
          margin: '0 0 8px',
        }}
      >
        OBSERVATION TIME (UTC)
      </p>
    </div>
  )
}

export default function TimeSeries({
  data,
  loading,
  error,
  historicalData,
  historicalLoading,
  historicalError,
}) {
  const cells = getObservationCells(data)

  const validValues = cells
    .filter((cell) => cell.value !== null)
    .map((cell) => cell.value)

  const currentAverage = validValues.length
    ? validValues.reduce((sum, value) => sum + value, 0) /
      validValues.length
    : null

  const observations = getHistoricalObservations(historicalData)

  const historicalValid = observations.filter(
    (item) => item.mean !== null
  )

  const historicalMeans = historicalValid.map(
    (item) => item.mean
  )

  const historicalAverage = historicalMeans.length
    ? historicalMeans.reduce((sum, value) => sum + value, 0) /
      historicalMeans.length
    : null

  const historicalMinimum = historicalMeans.length
    ? Math.min(...historicalMeans)
    : null

  const historicalMaximum = historicalMeans.length
    ? Math.max(...historicalMeans)
    : null

  const totalMissing = observations.reduce(
    (sum, item) => sum + item.missingCells,
    0
  )

  const historicalUnits =
    historicalData?.units || 'mm/hr'

  const historicalStart =
    observations[0]?.timestamp

  const historicalEnd =
    observations[observations.length - 1]?.timestamp

  const historicalAvailable =
    observations.length > 0 && historicalValid.length > 0

  const currentTimestamp = data?.timestamp
    ? formatTimestamp(data.timestamp)
    : 'Timestamp not supplied'

  return (
    <main className="timeseries-page">
      <header className="timeseries-header">
        <div>
          <span className="timeseries-eyebrow">
            EARTH SCIENCE INTELLIGENCE / TEMPORAL ANALYSIS
          </span>

          <h1>Time Series Analysis</h1>

          <p>
            Explore historical satellite observations, inspect
            temporal precipitation patterns, and examine individual
            regional grid-cell measurements.
          </p>
        </div>

        <span className="timeseries-source">
          NASA GPM · IMERG V07
        </span>
      </header>

      <section className="timeseries-panel">
        <div className="timeseries-panel-heading">
          <div>
            <span className="timeseries-panel-eyebrow">
              HISTORICAL DATASET
            </span>
            <h2>24-hour precipitation history</h2>
          </div>

          <span className="timeseries-tag">
            {historicalAvailable
              ? `${historicalValid.length} OBSERVATIONS`
              : historicalLoading
                ? 'LOADING'
                : 'AWAITING DATA'}
          </span>
        </div>

        {historicalLoading ? (
          <section className="timeseries-notice">
            <span className="notice-symbol">◷</span>
            <div>
              <strong>Retrieving historical observations</strong>
              <p>
                Loading the historical NASA GPM IMERG dataset.
              </p>
            </div>
          </section>
        ) : historicalError ? (
          <section className="timeseries-notice timeseries-error">
            <span className="notice-symbol">!</span>
            <div>
              <strong>Historical data retrieval failed</strong>
              <p>{String(historicalError)}</p>
            </div>
          </section>
        ) : historicalAvailable ? (
          <>
            <section className="timeseries-metrics">
              <article>
                <span>TIME OBSERVATIONS</span>
                <strong>{observations.length}</strong>
                <small>Half-hourly timestamps</small>
              </article>

              <article>
                <span>HISTORICAL MEAN</span>
                <strong>
                  {formatValue(historicalAverage)}
                </strong>
                <small>{historicalUnits}</small>
              </article>

              <article>
                <span>MINIMUM SPATIAL MEAN</span>
                <strong>
                  {formatValue(historicalMinimum)}
                </strong>
                <small>{historicalUnits}</small>
              </article>

              <article>
                <span>MAXIMUM SPATIAL MEAN</span>
                <strong>
                  {formatValue(historicalMaximum)}
                </strong>
                <small>{historicalUnits}</small>
              </article>
            </section>

            <div className="timeseries-profile">
              <div className="profile-stat">
                <span>DATASET</span>
                <strong>
                  {historicalData?.dataset?.name ||
                    'NASA GPM IMERG Historical Pilot'}
                </strong>
              </div>

              <div className="profile-stat">
                <span>START TIME (UTC)</span>
                <strong>{formatTimestamp(historicalStart)}</strong>
              </div>

              <div className="profile-stat">
                <span>END TIME (UTC)</span>
                <strong>{formatTimestamp(historicalEnd)}</strong>
              </div>

              <div className="profile-stat">
                <span>VALID GRID MEASUREMENTS</span>
                <strong>
                  {historicalData?.summary?.valid_observations ??
                    historicalValid.reduce(
                      (sum, item) => sum + item.validCells,
                      0
                    )}
                </strong>
              </div>

              <div className="profile-stat">
                <span>MISSING GRID MEASUREMENTS</span>
                <strong>{totalMissing}</strong>
              </div>

              <div className="profile-stat">
                <span>TIME INTERVAL</span>
                <strong>30 MINUTES</strong>
              </div>
            </div>

            <div style={{ marginTop: '28px' }}>
              <HistoricalChart
                observations={observations}
                units={historicalUnits}
              />
            </div>

            <div className="timeseries-panel-heading" style={{ marginTop: '28px' }}>
              <div>
                <span className="timeseries-panel-eyebrow">
                  TEMPORAL MEASUREMENTS
                </span>
                <h2>Historical observation records</h2>
              </div>

              <span className="timeseries-tag">
                UTC
              </span>
            </div>

            <div style={{ overflowX: 'auto' }}>
              <table
                style={{
                  width: '100%',
                  borderCollapse: 'collapse',
                  textAlign: 'left',
                  fontSize: '13px',
                }}
              >
                <thead>
                  <tr>
                    {[
                      'TIME (UTC)',
                      `SPATIAL MEAN (${historicalUnits})`,
                      'VALID CELLS',
                      'MISSING CELLS',
                    ].map((heading) => (
                      <th
                        key={heading}
                        style={cellHeadingStyle}
                      >
                        {heading}
                      </th>
                    ))}
                  </tr>
                </thead>

                <tbody>
                  {observations.map((item) => (
                    <tr key={item.index}>
                      <td style={cellStyle}>
                        {formatTimestamp(item.timestamp)}
                      </td>

                      <td style={cellStyle}>
                        {formatValue(item.mean)}
                      </td>

                      <td style={cellStyle}>
                        {item.validCells}
                      </td>

                      <td style={cellStyle}>
                        {item.missingCells}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        ) : (
          <div className="timeseries-empty">
            No valid historical observations are currently available.
          </div>
        )}
      </section>

      <section className="timeseries-panel">
        <div className="timeseries-panel-heading">
          <div>
            <span className="timeseries-panel-eyebrow">
              REGIONAL OBSERVATION
            </span>
            <h2>Current grid-cell measurements</h2>
          </div>

          <span className="timeseries-tag">
            REGIONAL SNAPSHOT
          </span>
        </div>

        {loading ? (
          <div className="timeseries-empty">
            Retrieving the selected regional observation...
          </div>
        ) : error ? (
          <div className="timeseries-empty timeseries-error">
            {String(error?.message || error)}
          </div>
        ) : cells.length > 0 ? (
          <>
            <div className="timeseries-profile">
              <div className="profile-stat">
                <span>VARIABLE</span>
                <strong>
                  {(data?.variable || 'Not specified').replaceAll('_', ' ')}
                </strong>
              </div>

              <div className="profile-stat">
                <span>OBSERVATION TIME</span>
                <strong>{currentTimestamp}</strong>
              </div>

              <div className="profile-stat">
                <span>REGIONAL MEAN</span>
                <strong>{formatValue(currentAverage)}</strong>
              </div>

              <div className="profile-stat">
                <span>VALID CELLS</span>
                <strong>{validValues.length}</strong>
              </div>

              <div className="profile-stat">
                <span>MISSING CELLS</span>
                <strong>{cells.length - validValues.length}</strong>
              </div>
            </div>

            <div style={{ overflowX: 'auto', marginTop: '20px' }}>
              <table
                style={{
                  width: '100%',
                  borderCollapse: 'collapse',
                  textAlign: 'left',
                  fontSize: '13px',
                }}
              >
                <thead>
                  <tr>
                    {[
                      'GRID CELL',
                      'LATITUDE',
                      'LONGITUDE',
                      `OBSERVATION (${data?.units || 'units'})`,
                      'QUALITY',
                    ].map((heading) => (
                      <th key={heading} style={cellHeadingStyle}>
                        {heading}
                      </th>
                    ))}
                  </tr>
                </thead>

                <tbody>
                  {cells.map((cell, index) => (
                    <tr key={cell.id}>
                      <td style={cellStyle}>
                        {`CELL ${String(index + 1).padStart(2, '0')}`}
                      </td>

                      <td style={cellStyle}>
                        {Number(cell.latitude).toFixed(3)}°
                      </td>

                      <td style={cellStyle}>
                        {Number(cell.longitude).toFixed(3)}°
                      </td>

                      <td style={cellStyle}>
                        {formatValue(cell.value, 4)}
                      </td>

                      <td
                        style={{
                          ...cellStyle,
                          color: cell.value === null
                            ? '#ffb300'
                            : '#00e5a0',
                        }}
                      >
                        {cell.value === null ? 'MISSING' : 'VALID'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        ) : (
          <div className="timeseries-empty">
            No regional grid-cell measurements are available.
          </div>
        )}
      </section>

      <section className="timeseries-panel methodology-panel">
        <span className="timeseries-panel-eyebrow">
          SCIENTIFIC INTERPRETATION
        </span>

        <h2>How the historical trend is calculated</h2>

        <div className="timeseries-roadmap">
          <article>
            <span className="roadmap-number">01</span>
            <div>
              <strong>Spatial aggregation</strong>
              <p>
                The four grid-cell measurements at each timestamp
                are averaged to produce one regional mean.
              </p>
            </div>
          </article>

          <article>
            <span className="roadmap-number">02</span>
            <div>
              <strong>Temporal sequence</strong>
              <p>
                The regional means are plotted in their original
                half-hourly UTC order.
              </p>
            </div>
          </article>

          <article>
            <span className="roadmap-number">03</span>
            <div>
              <strong>Missing-data safeguards</strong>
              <p>
                Missing measurements are excluded from each
                timestamp's mean. Valid zero precipitation values
                remain included as real observations.
              </p>
            </div>
          </article>
        </div>

      </section>
    </main>
  )
}

const cellHeadingStyle = {
  padding: '13px 12px',
  color: '#00e5ff',
  borderBottom: '1px solid rgba(0,229,255,0.2)',
  whiteSpace: 'nowrap',
  fontSize: '11px',
}

const cellStyle = {
  padding: '14px 12px',
  color: '#c7d4e8',
  borderBottom: '1px solid rgba(150,170,200,0.12)',
  whiteSpace: 'nowrap',
}
