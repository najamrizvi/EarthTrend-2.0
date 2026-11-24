
import './Overview.css'
import { lazy, Suspense } from 'react'

const EarthGlobe = lazy(() => import('../components/EarthGlobe.jsx'))

const platformMetrics = [
  {
    label: 'DATA SOURCE',
    value: 'NASA GPM',
    detail: 'IMERG · Version 07',
    icon: '◈',
  },
  {
    label: 'TIME RESOLUTION',
    value: '30 MIN',
    detail: 'Half-hourly observations',
    icon: '◷',
  },
  {
    label: 'SPATIAL RESOLUTION',
    value: '0.1°',
    detail: 'Native product grid',
    icon: '▦',
  },
  {
    label: 'WORKSPACE',
    value: 'READY',
    detail: 'Scientific environment',
    icon: '⌁',
  },
]

const analysisPages = [
  {
    id: 'geospatial',
    name: 'Geospatial Analysis',
    description: 'Explore regional observations',
    icon: '◎',
  },
  {
    id: 'timeseries',
    name: 'Time Series',
    description: 'Examine temporal patterns',
    icon: '⌁',
  },
  {
    id: 'forecasting',
    name: 'Forecasting',
    description: 'Explore prediction experiments',
    icon: '⌗',
  },
  {
    id: 'insights',
    name: 'AI Insights',
    description: 'Review evidence-based findings',
    icon: '✧',
  },
]

function isValidNumber(value) {
  if (
    value === null ||
    value === undefined ||
    typeof value === 'string' && value.trim() === ''
  ) {
    return false
  }

  return Number.isFinite(Number(value))
}

function getObservationCells(values) {
  if (!Array.isArray(values)) {
    return []
  }

  return values
    .flat(Infinity)
    .filter(isValidNumber)
    .map(Number)
}

function formatObservationTime(timestamp) {
  if (!timestamp) {
    return null
  }

  const value = String(timestamp)

  const match = value.match(
    /^(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2})/
  )

  if (!match) {
    return value
  }

  return `${match[1]} ${match[2]} UTC`
}

export default function Overview({
  data,
  loading,
  error,
  onNavigate,
}) {
  const latitudeCount =
    Array.isArray(data?.coordinates?.latitude)
      ? data.coordinates.latitude.length
      : 0

  const longitudeCount =
    Array.isArray(data?.coordinates?.longitude)
      ? data.coordinates.longitude.length
      : 0

  const validValues = getObservationCells(data?.values)

  const hasCoordinates =
    latitudeCount > 0 && longitudeCount > 0

  const hasData =
    hasCoordinates && validValues.length > 0

  const average =
    validValues.length > 0
      ? (
          validValues.reduce(
            (sum, value) => sum + value,
            0
          ) / validValues.length
        ).toFixed(3)
      : '—'

  const observationTime =
    formatObservationTime(data?.timestamp)

  const status = loading
    ? 'RETRIEVING OBSERVATIONS'
    : error
      ? 'DATA CONNECTION ISSUE'
      : hasData
        ? 'OBSERVATIONS AVAILABLE'
        : 'AWAITING DATA'

  return (
    <main className="overview-page">
      <header className="overview-header">
        <div className="overview-heading">
          <div className="overview-eyebrow">
            EARTH SCIENCE INTELLIGENCE / 02
          </div>

          <h1>Earth Intelligence Center</h1>

          <p>
            Scientific observation, geospatial exploration
            and evidence-driven analysis of Earth's systems.
          </p>
        </div>

        <div className={`overview-status ${error ? 'status-error' : ''}`}>
          <span className="status-indicator" />
          <span>{status}</span>
        </div>
      </header>

      <section className="overview-metrics">
        {platformMetrics.map((metric) => (
          <article className="overview-metric" key={metric.label}>
            <div className="metric-top">
              <span>{metric.label}</span>
              <span className="metric-icon">{metric.icon}</span>
            </div>

            <strong>{metric.value}</strong>
            <p>{metric.detail}</p>
          </article>
        ))}
      </section>

      <section className="mission-layout">
        <article className="mission-globe-panel">
          <div className="mission-panel-header">
            <div>
              <span className="panel-eyebrow">
                PLANETARY OBSERVATION / GLOBAL CONTEXT
              </span>

              <h2>Earth observation viewport</h2>
            </div>

            <span className="panel-live-label">
              <span />
              3D EARTH
            </span>
          </div>

          <div className="globe-viewport">
            <Suspense
              fallback={
                <div className="geospatial-map-message">
                  Initializing Earth visualization...
                </div>
              }
            >
              <EarthGlobe data={data} />
            </Suspense>
          </div>

          <div className="globe-caption">
            <div>
              <span className="caption-marker" />
              <span>Regional grid observations</span>
            </div>

            <span>
              {validValues.length} VALID CELLS
            </span>
          </div>

          <div className="globe-disclaimer">
            Globe provides geographic context. Highlighted points represent
            retrieved regional grid cells, not global data coverage.
          </div>
        </article>

        <aside className="mission-intelligence-panel">
          <div className="mission-panel-header">
            <div>
              <span className="panel-eyebrow">
                DATA INTELLIGENCE
              </span>

              <h2>Regional snapshot</h2>
            </div>

            <span className="panel-symbol">◈</span>
          </div>

          {loading ? (
            <div className="overview-message">
              Retrieving regional observations...
            </div>
          ) : error ? (
            <div className="overview-message error-message">
              Regional data could not be retrieved.
            </div>
          ) : hasData ? (
            <>
              <div className="intelligence-value-label">
                MEAN GRID-CELL VALUE · SELECTED TIMESTEP
              </div>

              <div className="observation-value">
                {average}
                <span>{data.units || 'units'}</span>
              </div>

              <p className="observation-description">
                Mean precipitation rate across the available regional
                grid cells at the selected UTC observation time.
              </p>

              {observationTime && (
                <p className="observation-description">
                  Observation time: {observationTime}
                </p>
              )}

              <div className="intelligence-divider" />

              <div className="intelligence-facts">
                <div>
                  <span>GRID DIMENSIONS</span>
                  <strong>
                    {latitudeCount} × {longitudeCount}
                  </strong>
                </div>

                <div>
                  <span>VALID CELLS</span>
                  <strong>{validValues.length}</strong>
                </div>

                <div>
                  <span>VARIABLE</span>
                  <strong>
                    {(data.variable || 'Not specified').replaceAll('_', ' ')}
                  </strong>
                </div>

                <div>
                  <span>GRID RESOLUTION</span>
                  <strong>
                    {data.spatial_resolution || 'Not specified'}
                  </strong>
                </div>
              </div>
            </>
          ) : (
            <div className="overview-message">
              Waiting for valid regional observations.
            </div>
          )}

          <button
            className="overview-action"
            onClick={() => onNavigate?.('geospatial')}
          >
            Open geospatial analysis
            <span>↗</span>
          </button>
        </aside>
      </section>

      <section className="science-foundation">
        <div className="science-foundation-heading">
          <div>
            <span className="panel-eyebrow">
              SCIENTIFIC FOUNDATION
            </span>

            <h2>Observation infrastructure</h2>
          </div>

          <span className="science-version">PRODUCT V07</span>
        </div>

        <div className="science-foundation-content">
          <div className="science-source">
            <div className="source-mark">NASA</div>

            <div>
              <strong>Global Precipitation Measurement</strong>
              <span>IMERG Final · Version 07</span>
            </div>
          </div>

          <div className="science-fact">
            <span>DATA PRODUCT</span>
            <strong>GPM_3IMERGHH</strong>
          </div>

          <div className="science-fact">
            <span>TIME INTERVAL</span>
            <strong>Half-hourly</strong>
          </div>

          <div className="science-fact">
            <span>OBSERVATION GRID</span>
            <strong>0.1°</strong>
          </div>
        </div>
      </section>

      <section className="analysis-access">
        <div className="analysis-access-heading">
          <div>
            <span className="panel-eyebrow">
              ANALYTICAL ENVIRONMENT
            </span>

            <h2>Explore scientific capabilities</h2>
          </div>

          <span className="analysis-access-caption">
            FOUR ANALYSIS MODULES
          </span>
        </div>

        <div className="overview-navigation">
          {analysisPages.map((page) => (
            <button
              key={page.id}
              onClick={() => onNavigate?.(page.id)}
            >
              <span className="analysis-icon">{page.icon}</span>

              <span className="analysis-navigation-text">
                <strong>{page.name}</strong>
                <small>{page.description}</small>
              </span>

              <span className="navigation-arrow">↗</span>
            </button>
          ))}
        </div>
      </section>
    </main>
  )
}
