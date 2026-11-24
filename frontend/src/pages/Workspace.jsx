
import { lazy, Suspense, useEffect, useState } from 'react'
import Overview from './Overview.jsx'
import './Workspace.css'

const GeospatialAnalysis = lazy(() => import('./GeospatialAnalysis.jsx'))
const TimeSeries = lazy(() => import('./TimeSeries.jsx'))
const Forecasting = lazy(() => import('./Forecasting.jsx'))
const AIInsights = lazy(() => import('./AIInsights.jsx'))

const navigation = [
  {
    section: 'MONITOR',
    items: [
      { id: 'overview', label: 'Overview', icon: '◈' },
      { id: 'geospatial', label: 'Geospatial Analysis', icon: '◎' },
    ],
  },
  {
    section: 'ANALYZE',
    items: [
      { id: 'timeseries', label: 'Time Series', icon: '⌁' },
      { id: 'forecasting', label: 'Forecasting', icon: '⌗' },
    ],
  },
  {
    section: 'INTELLIGENCE',
    items: [
      { id: 'insights', label: 'AI Insights', icon: '✧' },
    ],
  },
]

function getUtcTime() {
  return new Date().toISOString().slice(11, 19)
}

export default function Workspace({
  data,
  loading,
  error,
  variable,
  setVariable,
  timeIndex,
  setTimeIndex,
  historicalData,
  historicalLoading,
  historicalError,
  onExit,
}) {
  const [activePage, setActivePage] = useState('overview')
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [utcTime, setUtcTime] = useState(getUtcTime)
  const [headerPanel, setHeaderPanel] = useState(null)

  useEffect(() => {
    const clockInterval = setInterval(() => {
      setUtcTime(getUtcTime())
    }, 1000)

    return () => clearInterval(clockInterval)
  }, [])

  const activeItem = navigation
    .flatMap((group) => group.items)
    .find((item) => item.id === activePage)

  const hasObservations =
    Array.isArray(data?.coordinates?.latitude) &&
    Array.isArray(data?.coordinates?.longitude) &&
    Array.isArray(data?.values)

  const systemStatus = loading
    ? 'RETRIEVING DATA'
    : error
      ? 'SOURCE ERROR'
      : hasObservations
        ? 'DATA AVAILABLE'
        : 'AWAITING DATA'

  const systemStatusClass = loading
    ? 'status-loading'
    : error
      ? 'status-error'
      : hasObservations
        ? 'status-ready'
        : 'status-idle'

  const observationCount = hasObservations
    ? data.values.flat(Infinity).filter(
        (value) =>
          value !== null &&
          value !== undefined &&
          Number.isFinite(Number(value))
      ).length
    : 0

  function navigateTo(page) {
    setActivePage(page)
    setSidebarOpen(false)
    setHeaderPanel(null)
  }

  function renderPage() {
    switch (activePage) {
      case 'overview':
        return (
          <Overview
            data={data}
            loading={loading}
            error={error}
            onNavigate={navigateTo}
          />
        )

      case 'geospatial':
        return (
          <Suspense
            fallback={
              <div className="geospatial-map-message">
                Loading Geospatial Analysis...
              </div>
            }
          >
            <GeospatialAnalysis
              data={data}
              loading={loading}
              error={error}
              variable={variable}
              setVariable={setVariable}
              timeIndex={timeIndex}
              setTimeIndex={setTimeIndex}
            />
          </Suspense>
        )

      case 'timeseries':
        return (
          <Suspense
            fallback={
              <div className="geospatial-map-message">
                Loading Time Series Analysis...
              </div>
            }
          >
            <TimeSeries
              data={data}
              loading={loading}
              error={error}
              historicalData={historicalData}
              historicalLoading={historicalLoading}
              historicalError={historicalError}
            />
          </Suspense>
        )


      case 'forecasting':
        return (
          <Suspense
            fallback={
              <div className="geospatial-map-message">
                Loading Forecasting Analysis...
              </div>
            }
          >
            <Forecasting
              data={data}
              historicalData={historicalData}
              historicalLoading={historicalLoading}
              historicalError={historicalError}
          />
        </Suspense>
      )


      case 'insights':
        return (
          <Suspense
            fallback={
              <div className="geospatial-map-message">
                Loading AI Insights...
              </div>
            }
          >
            <AIInsights
              data={data}
              loading={loading}
              error={error}
              historicalData={historicalData}
              historicalLoading={historicalLoading}
              historicalError={historicalError}
            />
          </Suspense>
        )
      default:
        return null
    }
  }

  return (
    <div className="workspace-shell">
      {sidebarOpen && (
        <button
          className="workspace-sidebar-overlay"
          aria-label="Close navigation"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <aside
        className={`workspace-sidebar ${
          sidebarOpen ? 'sidebar-open' : ''
        }`}
      >
        <div className="workspace-brand">
          <div className="workspace-brand-mark">E</div>
          <div>
            <strong>
              EARTH<span>TREND</span>
            </strong>
            <small>EARTH INTELLIGENCE 2.0</small>
          </div>
        </div>

        <div className="workspace-sidebar-divider" />

        <div className="workspace-navigation">
          {navigation.map((group) => (
            <div className="workspace-nav-group" key={group.section}>
              <span className="workspace-nav-heading">
                {group.section}
              </span>

              {group.items.map((item) => (
                <button
                  key={item.id}
                  className={`workspace-nav-item ${
                    activePage === item.id ? 'active' : ''
                  }`}
                  onClick={() => navigateTo(item.id)}
                  aria-current={
                    activePage === item.id ? 'page' : undefined
                  }
                >
                  <span className="workspace-nav-icon">
                    {item.icon}
                  </span>
                  <span>{item.label}</span>

                  {activePage === item.id && (
                    <span className="workspace-nav-indicator" />
                  )}
                </button>
              ))}
            </div>
          ))}
        </div>

        <div className="workspace-sidebar-bottom">
          <div className="workspace-data-indicator">
            <span className="workspace-data-dot" />
            <div>
              <strong>DATA WORKSPACE</strong>
              <small>Regional observation system</small>
            </div>
          </div>

          <button
            className="workspace-exit-button"
            onClick={onExit}
          >
            <span>←</span>
            Return to Home
          </button>
        </div>
      </aside>

      <div className="workspace-main">
        <header className="workspace-topbar">
          <div className="workspace-breadcrumb">
            <button
              className="workspace-menu-button"
              onClick={() => setSidebarOpen(true)}
              aria-label="Open navigation"
            >
              ☰
            </button>

            <span>WORKSPACE</span>
            <span className="workspace-breadcrumb-separator">/</span>
            <strong>{activeItem?.label || 'Overview'}</strong>
          </div>

          <div className="workspace-topbar-right">
            <div className="workspace-clock">
              <span className="workspace-clock-label">UTC</span>
              <strong className="workspace-clock-value">
                {utcTime}
              </strong>
            </div>

            <span className="workspace-version">
              PLATFORM 2.0
            </span>

            <button
              type="button"
              className={`workspace-status ${systemStatusClass}`}
              style={{
                border: 'none',
                background: 'transparent',
                color: 'inherit',
                font: 'inherit',
                cursor: 'pointer',
              }}
              onClick={() =>
                setHeaderPanel(
                  headerPanel === 'status' ? null : 'status'
                )
              }
              aria-expanded={headerPanel === 'status'}
            >
              <span />
              {systemStatus}
            </button>

            <button
              type="button"
              className="workspace-science-mode"
              style={{
                background: 'transparent',
                color: 'inherit',
                font: 'inherit',
                cursor: 'pointer',
              }}
              onClick={() =>
                setHeaderPanel(
                  headerPanel === 'science' ? null : 'science'
                )
              }
              aria-expanded={headerPanel === 'science'}
            >
              SCIENTIFIC MODE
            </button>
          </div>

          {headerPanel && (
            <div
              className="workspace-header-panel"
              role="dialog"
              aria-label={
                headerPanel === 'status'
                  ? 'Data connection status'
                  : 'Scientific mode information'
              }
              style={{
                position: 'fixed',
                top: '76px',
                right: '24px',
                zIndex: 1000,
                width: 'min(340px, calc(100vw - 40px))',
                boxSizing: 'border-box',
                padding: '22px',
                background: '#131a26',
                border: '1px solid rgba(0, 229, 255, 0.3)',
                borderRadius: '8px',
                color: '#e8efff',
                boxShadow: '0 12px 35px rgba(0, 0, 0, 0.4)',
              }}
            >
              <button
                type="button"
                onClick={() => setHeaderPanel(null)}
                aria-label="Close information panel"
                style={{
                  position: 'absolute',
                  top: '8px',
                  right: '12px',
                  border: 'none',
                  background: 'transparent',
                  color: '#aab8cc',
                  fontSize: '22px',
                  cursor: 'pointer',
                }}
              >
                ×
              </button>

              {headerPanel === 'status' ? (
                <>
                  <strong
                    style={{
                      display: 'block',
                      color: '#00e5ff',
                      fontSize: '12px',
                      letterSpacing: '1px',
                      marginBottom: '16px',
                    }}
                  >
                    DATA CONNECTION STATUS
                  </strong>

                  <p>System: {systemStatus}</p>
                  <p>Source: NASA GPM IMERG V07</p>
                  <p>Observation cells: {observationCount}</p>
                  <p>Selected variable: {variable || 'Not specified'}</p>
                  <p>Time index: {timeIndex ?? 'Not specified'}</p>

                  {error && (
                    <p>
                      Source error:{' '}
                      {String(error?.message || error)}
                    </p>
                  )}

                  <p>
                    Historical data:{' '}
                    {historicalLoading
                      ? 'Loading'
                      : historicalError
                        ? 'Unavailable'
                        : historicalData
                          ? 'Available'
                          : 'Awaiting data'}
                  </p>
                </>
              ) : (
                <>
                  <strong
                    style={{
                      display: 'block',
                      color: '#00e5ff',
                      fontSize: '12px',
                      letterSpacing: '1px',
                      marginBottom: '16px',
                    }}
                  >
                    SCIENTIFIC MODE
                  </strong>

                  <p>Evidence-first Earth observation analysis.</p>
                  <p>
                    Results are based on retrieved NASA GPM IMERG V07
                    data.
                  </p>
                  <p>
                    Unsupported measurements and conclusions are not
                    presented as verified facts.
                  </p>
                  <p>
                    Scientific safeguards remain active throughout
                    the workspace.
                  </p>
                </>
              )}
            </div>
          )}
        </header>

        <main className="workspace-content" key={activePage}>
          {renderPage()}
        </main>

        <footer className="workspace-footer">
          <span>EARTH TREND 2.0</span>
          <span>
            NASA GPM IMERG V07 · REGIONAL DATA WORKSPACE
          </span>
        </footer>
      </div>
    </div>
  )
}
