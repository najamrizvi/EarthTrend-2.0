
import { useEffect, useMemo, useState } from 'react'
import './Forecasting.css'

const API_BASE_URL = '/api'

function formatTimestamp(timestamp) {
  if (!timestamp) return '—'

  return new Date(timestamp.endsWith('Z') ? timestamp : `${timestamp}Z`)
    .toLocaleString([], {
      day: '2-digit',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit',
      hour12: false,
    })
}

function formatMetric(value) {
  return Number.isFinite(value) ? value.toFixed(5) : '—'
}

function ForecastChart({ history, forecast, units }) {
  const chart = useMemo(() => {
    const combined = [...history, ...forecast]

    if (combined.length < 2) return null

    const values = combined.map((item) => item.value)
    const maxValue = Math.max(...values, 0.1)
    const width = 900
    const height = 280
    const padding = { top: 24, right: 25, bottom: 35, left: 65 }

    const plotWidth = width - padding.left - padding.right
    const plotHeight = height - padding.top - padding.bottom

    const x = (index) =>
      padding.left + (index / (combined.length - 1)) * plotWidth

    const y = (value) =>
      padding.top + plotHeight - (value / maxValue) * plotHeight

    const historyPoints = history.map(
      (item, index) => `${x(index)},${y(item.value)}`
    )

    const forecastPoints = [
      ...(history.length
        ? [`${x(history.length - 1)},${y(history[history.length - 1].value)}`]
        : []),
      ...forecast.map((item, index) =>
        `${x(history.length + index)},${y(item.value)}`
      ),
    ]

    const gridLines = [0, 0.25, 0.5, 0.75, 1].map((fraction) => ({
      y: padding.top + plotHeight * (1 - fraction),
      label: (maxValue * fraction).toFixed(3),
    }))

    return {
      width,
      height,
      historyPoints: historyPoints.join(' '),
      forecastPoints: forecastPoints.join(' '),
      gridLines,
      historyEndX: history.length
        ? x(history.length - 1)
        : padding.left,
    }
  }, [history, forecast])

  if (!chart) {
    return (
      <div className="forecasting-placeholder">
        <strong>Chart data unavailable</strong>
        <p>Historical observations and forecast values are required.</p>
      </div>
    )
  }

  return (
    <div style={{ width: '100%', overflowX: 'auto' }}>
      <svg
        viewBox={`0 0 ${chart.width} ${chart.height}`}
        role="img"
        aria-label="Historical precipitation and six-hour forecast chart"
        style={{ width: '100%', minWidth: '550px', display: 'block' }}
      >
        {chart.gridLines.map((line, index) => (
          <g key={index}>
            <line
              x1="65"
              y1={line.y}
              x2="875"
              y2={line.y}
              stroke="rgba(148, 163, 184, 0.17)"
              strokeDasharray="4 5"
            />
            <text
              x="55"
              y={line.y + 4}
              textAnchor="end"
              fill="#94a3b8"
              fontSize="11"
            >
              {line.label}
            </text>
          </g>
        ))}

        <line
          x1={chart.historyEndX}
          y1="24"
          x2={chart.historyEndX}
          y2="245"
          stroke="rgba(34, 211, 238, 0.55)"
          strokeDasharray="5 5"
        />

        <polyline
          points={chart.historyPoints}
          fill="none"
          stroke="#22d3ee"
          strokeWidth="2.5"
          strokeLinejoin="round"
          strokeLinecap="round"
        />

        <polyline
          points={chart.forecastPoints}
          fill="none"
          stroke="#a78bfa"
          strokeWidth="2.8"
          strokeLinejoin="round"
          strokeLinecap="round"
          strokeDasharray="7 4"
        />

        {history.length > 0 && (
          <circle
            cx={chart.historyEndX}
            cy={245 - (history[history.length - 1].value / Math.max(
              ...[...history, ...forecast].map((item) => item.value),
              0.1
            )) * 221}
            r="4"
            fill="#22d3ee"
          />
        )}

        <text
          x="65"
          y="270"
          fill="#94a3b8"
          fontSize="11"
        >
          Historical observations
        </text>

        <text
          x="875"
          y="270"
          fill="#94a3b8"
          fontSize="11"
          textAnchor="end"
        >
          Forecast → ({units})
        </text>
      </svg>

      <div
        style={{
          display: 'flex',
          gap: '22px',
          flexWrap: 'wrap',
          padding: '8px 4px',
          color: '#94a3b8',
          fontSize: '12px',
        }}
      >
        <span>
          <span style={{ color: '#22d3ee' }}>●</span> Historical
        </span>
        <span>
          <span style={{ color: '#a78bfa' }}>●</span> Forecast
        </span>
      </div>
    </div>
  )
}

export default function Forecasting({ data }) {
  const [forecastData, setForecastData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const controller = new AbortController()

    async function loadForecast() {
      try {
        setLoading(true)
        setError('')

        const response = await fetch(
          `${API_BASE_URL}/gpm/forecast`,
          { signal: controller.signal }
        )

        if (!response.ok) {
          const errorBody = await response.json().catch(() => null)
          throw new Error(
            errorBody?.detail || `Forecast API returned HTTP ${response.status}`
          )
        }

        const result = await response.json()

        if (
          result.status !== 'success' ||
          !Array.isArray(result.forecast?.values) ||
          !Array.isArray(result.forecast?.timestamps)
        ) {
          throw new Error('The forecast API returned an unexpected response.')
        }

        setForecastData(result)
      } catch (err) {
        if (err.name !== 'AbortError') {
          setError(err.message || 'Unable to load forecasting results.')
        }
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false)
        }
      }
    }

    loadForecast()

    return () => controller.abort()
  }, [])

  const history = useMemo(() => {
    const timestamps = forecastData?.recent_history?.timestamps || []
    const values = forecastData?.recent_history?.values || []

    return timestamps.map((timestamp, index) => ({
      timestamp,
      value: Number(values[index]),
    })).filter((item) => Number.isFinite(item.value))
  }, [forecastData])

  const forecast = useMemo(() => {
    const timestamps = forecastData?.forecast?.timestamps || []
    const values = forecastData?.forecast?.values || []

    return timestamps.map((timestamp, index) => ({
      timestamp,
      value: Number(values[index]),
    })).filter((item) => Number.isFinite(item.value))
  }, [forecastData])

  const evaluation = forecastData?.evaluation
  const selectedMetrics = evaluation?.selected_metrics
  const selectedBaseline = evaluation?.selected_baseline

  const hasObservation = Boolean(data?.values?.length || history.length)

  return (
    <main className="forecasting-page">
      <header className="forecasting-header">
        <div>
          <span className="forecasting-eyebrow">
            EARTH SCIENCE INTELLIGENCE / PREDICTIVE ANALYTICS
          </span>
          <h1>Forecasting Laboratory</h1>
          <p>
            Six-hour precipitation forecasting using validated NASA GPM
            historical observations and transparent statistical baselines.
          </p>
        </div>

        <span className="forecasting-status">
          {loading ? 'LOADING FORECAST' : error ? 'API ERROR' : 'LIVE API CONNECTED'}
        </span>
      </header>

      {loading && (
        <section className="forecasting-intro">
          <div className="forecasting-intro-icon">⌁</div>
          <div>
            <strong>Loading forecasting results</strong>
            <p>Retrieving historical observations and evaluation results.</p>
          </div>
        </section>
      )}

      {error && (
        <section
          className="forecasting-intro"
          style={{ borderColor: 'rgba(248, 113, 113, 0.45)' }}
        >
          <div className="forecasting-intro-icon">!</div>
          <div>
            <strong>Forecast API unavailable</strong>
            <p>{error}</p>
            <button
              type="button"
              onClick={() => window.location.reload()}
              style={{
                marginTop: '12px',
                padding: '9px 15px',
                borderRadius: '7px',
                border: '1px solid rgba(34, 211, 238, 0.4)',
                background: 'transparent',
                color: '#22d3ee',
                cursor: 'pointer',
              }}
            >
              Retry
            </button>
          </div>
        </section>
      )}

      {!loading && !error && forecastData && (
        <>
          <section className="forecasting-intro">
            <div className="forecasting-intro-icon">⌁</div>
            <div>
              <strong>Evidence before prediction</strong>
              <p>
                The selected method is evaluated on the final seven days
                using chronological six-hour forecast windows. The displayed
                forecast uses the best-performing baseline by holdout MAE.
                It is a statistical reference method, not an AI model.
              </p>
            </div>
          </section>

          <section className="forecasting-overview">
            <article>
              <span>DATA AVAILABILITY</span>
              <strong>{hasObservation ? 'AVAILABLE' : 'UNAVAILABLE'}</strong>
              <small>
                {forecastData.historical_observations} half-hourly observations
              </small>
            </article>

            <article>
              <span>SELECTED BASELINE</span>
              <strong>
                {selectedBaseline === 'previous_day'
                  ? 'PREVIOUS DAY'
                  : 'PERSISTENCE'}
              </strong>
              <small>Selected using holdout MAE</small>
            </article>

            <article>
              <span>EVALUATION STATUS</span>
              <strong>COMPLETED</strong>
              <small>
                {selectedMetrics?.observations || 0} holdout predictions
              </small>
            </article>

            <article>
              <span>UNCERTAINTY</span>
              <strong>NOT ESTIMATED</strong>
              <small>Calibrated intervals not available</small>
            </article>
          </section>

          <section className="forecasting-panel" style={{ marginBottom: '22px' }}>
            <div className="forecasting-panel-heading">
              <div>
                <span className="forecasting-panel-eyebrow">
                  SHORT-TERM PRECIPITATION
                </span>
                <h2>Six-hour forecast</h2>
              </div>
              <span className="forecasting-panel-icon">◈</span>
            </div>

            <div style={{ display: 'flex', gap: '24px', flexWrap: 'wrap', marginBottom: '18px' }}>
              <div>
                <span className="forecasting-panel-eyebrow">LAST OBSERVATION</span>
                <strong style={{ display: 'block', color: '#e2e8f0', marginTop: '5px' }}>
                  {formatTimestamp(forecastData.last_observation_time)}
                </strong>
              </div>
              <div>
                <span className="forecasting-panel-eyebrow">FORECAST START</span>
                <strong style={{ display: 'block', color: '#e2e8f0', marginTop: '5px' }}>
                  {formatTimestamp(forecast[0]?.timestamp)}
                </strong>
              </div>
              <div>
                <span className="forecasting-panel-eyebrow">FORECAST POINTS</span>
                <strong style={{ display: 'block', color: '#e2e8f0', marginTop: '5px' }}>
                  {forecast.length}
                </strong>
              </div>
            </div>

            <ForecastChart
              history={history}
              forecast={forecast}
              units={forecastData.units}
            />

            <div style={{ marginTop: '18px', overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
                <thead>
                  <tr style={{ color: '#94a3b8', textAlign: 'left' }}>
                    <th style={{ padding: '10px' }}>Forecast time</th>
                    <th style={{ padding: '10px' }}>Precipitation ({forecastData.units})</th>
                  </tr>
                </thead>
                <tbody>
                  {forecast.map((item) => (
                    <tr key={item.timestamp} style={{ borderTop: '1px solid rgba(148, 163, 184, 0.14)' }}>
                      <td style={{ padding: '10px', color: '#cbd5e1' }}>
                        {formatTimestamp(item.timestamp)}
                      </td>
                      <td style={{ padding: '10px', color: '#e2e8f0' }}>
                        {item.value.toFixed(4)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          <section className="forecasting-main-grid">
            <article className="forecasting-panel model-panel">
              <div className="forecasting-panel-heading">
                <div>
                  <span className="forecasting-panel-eyebrow">
                    SELECTED METHOD
                  </span>
                  <h2>Baseline evaluation</h2>
                </div>
                <span className="forecasting-panel-icon">◈</span>
              </div>

              <div className="forecasting-evidence-list">
                <div>
                  <span>01</span>
                  <div>
                    <strong>Persistence baseline</strong>
                    <p>
                      MAE: {formatMetric(evaluation.persistence.mae)} ·
                      RMSE: {formatMetric(evaluation.persistence.rmse)}
                    </p>
                    <p>Bias: {formatMetric(evaluation.persistence.bias)}</p>
                  </div>
                </div>

                <div>
                  <span>02</span>
                  <div>
                    <strong>Previous-day baseline</strong>
                    <p>
                      MAE: {formatMetric(evaluation.previous_day.mae)} ·
                      RMSE: {formatMetric(evaluation.previous_day.rmse)}
                    </p>
                    <p>Bias: {formatMetric(evaluation.previous_day.bias)}</p>
                  </div>
                </div>
              </div>

              <div style={{ marginTop: '22px', padding: '15px', borderRadius: '9px', background: 'rgba(34, 211, 238, 0.07)' }}>
                <span className="forecasting-panel-eyebrow">SELECTED BY HOLDOUT MAE</span>
                <h2 style={{ margin: '8px 0', color: '#22d3ee' }}>
                  {selectedBaseline === 'previous_day' ? 'Previous-day baseline' : 'Persistence baseline'}
                </h2>
                <p style={{ color: '#94a3b8', fontSize: '13px' }}>
                  The selected baseline has the lower mean absolute error
                  across the chronological evaluation predictions.
                </p>
              </div>
            </article>

            <article className="forecasting-panel evidence-panel">
              <div className="forecasting-panel-heading">
                <div>
                  <span className="forecasting-panel-eyebrow">
                    SELECTED MODEL PERFORMANCE
                  </span>
                  <h2>Holdout metrics</h2>
                </div>
                <span className="forecasting-panel-icon">◎</span>
              </div>

              <div className="forecasting-evidence-list">
                <div>
                  <span>01</span>
                  <div>
                    <strong>Mean absolute error</strong>
                    <p>{formatMetric(selectedMetrics?.mae)} {forecastData.units}</p>
                  </div>
                </div>
                <div>
                  <span>02</span>
                  <div>
                    <strong>Root mean squared error</strong>
                    <p>{formatMetric(selectedMetrics?.rmse)} {forecastData.units}</p>
                  </div>
                </div>
                <div>
                  <span>03</span>
                  <div>
                    <strong>Prediction bias</strong>
                    <p>{formatMetric(selectedMetrics?.bias)} {forecastData.units}</p>
                  </div>
                </div>
                <div>
                  <span>04</span>
                  <div>
                    <strong>Evaluation observations</strong>
                    <p>{selectedMetrics?.observations ?? '—'} predictions</p>
                  </div>
                </div>
              </div>
            </article>
          </section>

          <section className="forecasting-methodology">
            <span className="forecasting-panel-eyebrow">
              DATA & SCIENTIFIC SAFEGUARDS
            </span>
            <h2>Forecast context and limitations</h2>

            <div className="forecasting-principles">
              <article>
                <strong>Data source</strong>
                <p>
                  {forecastData.source}. The forecast represents the
                  spatial mean of {forecastData.grid_cells} grid cells.
                </p>
              </article>

              <article>
                <strong>Chronological evaluation</strong>
                <p>
                  Final {evaluation.evaluation_period.days} days held out
                  for rolling-origin six-hour evaluation. No random split.
                </p>
              </article>

              <article>
                <strong>Uncertainty disclosure</strong>
                <p>
                  {forecastData.uncertainty.message}
                  Forecast values are baseline estimates, not guaranteed outcomes.
                </p>
              </article>
            </div>

            <div style={{ marginTop: '18px', color: '#94a3b8', fontSize: '12px', lineHeight: 1.7 }}>
              <strong>Spatial coverage:</strong>{' '}
              Latitude {forecastData.spatial_coverage.latitude.join('° to ')}°;
              longitude {forecastData.spatial_coverage.longitude.join('° to ')}°.
              {' '}This is a small four-cell regional sample, not a global
              precipitation forecast.
            </div>
          </section>
        </>
      )}
    </main>
  )
}
