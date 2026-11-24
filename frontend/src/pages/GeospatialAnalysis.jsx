
import RegionalMap from '../components/RegionalMap.jsx'
import './GeospatialAnalysis.css'

const variables = [
  { value: 'precipitation', label: 'Precipitation' },
  {
    value: 'precipitation_quality_index',
    label: 'Precipitation Quality Index',
  },
  { value: 'random_error', label: 'Random Error' },
]

export default function GeospatialAnalysis({
  data,
  loading,
  error,
  variable,
  setVariable,
  timeIndex,
  setTimeIndex,
}) {
  const latitude = data?.coordinates?.latitude ?? []
  const longitude = data?.coordinates?.longitude ?? []
  const values = data?.values ?? []

  const gridCount =
    data?.shape?.total_cells ?? latitude.length * longitude.length

  const flatValues = values.flat()

  const validValues = flatValues.filter(
    (value) =>
      value !== null &&
      value !== undefined &&
      Number.isFinite(Number(value))
  )

  const validCount = validValues.length
  const missingCount = Math.max(0, gridCount - validCount)

  const numericValues = validValues.map(Number)

  const minimum = numericValues.length
    ? Math.min(...numericValues)
    : null

  const maximum = numericValues.length
    ? Math.max(...numericValues)
    : null

  const timestamp = data?.timestamp
    ? data.timestamp.replace('T', ' ').replace('Z', '')
    : 'Awaiting observation'

  const selectedVariable =
    variables.find((item) => item.value === variable)?.label ??
    variable

  const dataStatus = loading
    ? 'RETRIEVING'
    : error
      ? 'SOURCE ERROR'
      : data
        ? 'DATA AVAILABLE'
        : 'AWAITING DATA'

  return (
    <main className="geospatial-page">
      <header className="geospatial-header">
        <div>
          <span className="geospatial-eyebrow">
            EARTH SCIENCE INTELLIGENCE / GEOSPATIAL
          </span>

          <h1>Geospatial Analysis</h1>

          <p>
            Explore satellite-derived precipitation observations across
            geographic regions using the NASA GPM IMERG dataset.
          </p>
        </div>

        <div className="geospatial-source">
          <span className="source-status-dot" />
          NASA GPM · IMERG V07
        </div>
      </header>

      <section className="geospatial-controls">
        <div className="geospatial-control">
          <label htmlFor="geo-variable">
            OBSERVATION VARIABLE
          </label>

          <select
            id="geo-variable"
            value={variable}
            onChange={(event) => setVariable(event.target.value)}
          >
            {variables.map((item) => (
              <option key={item.value} value={item.value}>
                {item.label}
              </option>
            ))}
          </select>
        </div>

        <div className="geospatial-control time-control">
          <label htmlFor="geo-time-index">
            TIME INDEX
          </label>

          <select
            id="geo-time-index"
            value={timeIndex}
            onChange={(event) => setTimeIndex(event.target.value)}
          >
            <option value="0">Observation 0</option>
            <option value="1">Observation 1</option>
          </select>
        </div>

        <div className="geospatial-control-info">
          <span>OBSERVATION INTERVAL</span>
          <strong>30 minutes</strong>
        </div>

        <div className="geospatial-control-info">
          <span>GRID RESOLUTION</span>
          <strong>0.1°</strong>
        </div>
      </section>

      <section className="geospatial-summary">
        <article>
          <span>TOTAL GRID CELLS</span>
          <strong>{data ? gridCount : '—'}</strong>
        </article>

        <article>
          <span>VALID OBSERVATIONS</span>
          <strong>{data ? validCount : '—'}</strong>
        </article>

        <article>
          <span>MISSING OBSERVATIONS</span>
          <strong>{data ? missingCount : '—'}</strong>
        </article>

        <article>
          <span>DATA UNITS</span>
          <strong>{data?.units || '—'}</strong>
        </article>
      </section>

      <section className="geospatial-map-panel">
        <div className="geospatial-map-heading">
          <div>
            <span className="map-panel-eyebrow">
              SPATIAL DATA VIEWER
            </span>

            <h2>Regional observation map</h2>

            <p>
              Geographic distribution of retrieved satellite grid-cell values.
            </p>
          </div>

          <span
            className={`map-live-label ${
              error ? 'map-status-error' : ''
            }`}
          >
            {dataStatus}
          </span>
        </div>

        <div className="geospatial-map-container">
          {loading ? (
            <div className="geospatial-map-message">
              Retrieving regional observations...
            </div>
          ) : error ? (
            <div className="geospatial-map-message geospatial-error">
              {String(error)}
            </div>
          ) : data ? (
            <RegionalMap data={data} />
          ) : (
            <div className="geospatial-map-message">
              No regional observations are currently available.
            </div>
          )}
        </div>

        <div className="geospatial-map-footer">
          <span>
            SOURCE: {data?.dataset || 'NASA GPM IMERG FINAL HALF-HOURLY V07'}
          </span>

          <span>
            {data?.timestamp || 'Observation timestamp unavailable'}
          </span>
        </div>
      </section>

      <section className="geospatial-information">
        <div>
          <span className="map-panel-eyebrow">
            OBSERVATION INTELLIGENCE
          </span>

          <h2>Selected observation metadata</h2>

          <div className="geospatial-metadata-grid">
            <div>
              <span>VARIABLE</span>
              <strong>{selectedVariable}</strong>
            </div>

            <div>
              <span>TIME INDEX</span>
              <strong>{timeIndex}</strong>
            </div>

            <div>
              <span>OBSERVATION TIME</span>
              <strong>{timestamp}</strong>
            </div>

            <div>
              <span>TIME STANDARD</span>
              <strong>{data?.time_standard || 'UTC'}</strong>
            </div>
          </div>
        </div>

        <div className="geospatial-information-note">
          <strong>Data integrity</strong>

          <p>
            {data
              ? `${validCount} valid measurements and ${missingCount} missing measurements across ${gridCount} retrieved grid cells. Missing values are excluded from numerical statistics.`
              : 'Observation quality statistics will appear when regional data becomes available.'}
          </p>

          <div className="geospatial-range">
            <span>OBSERVED MINIMUM</span>
            <strong>
              {minimum === null ? '—' : minimum.toFixed(4)}
            </strong>
          </div>

          <div className="geospatial-range">
            <span>OBSERVED MAXIMUM</span>
            <strong>
              {maximum === null ? '—' : maximum.toFixed(4)}
            </strong>
          </div>
        </div>
      </section>
    </main>
  )
}
