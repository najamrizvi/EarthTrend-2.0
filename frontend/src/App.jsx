
import { useEffect, useState } from 'react'

import HomePage from './pages/HomePage.jsx'
import Workspace from './pages/Workspace.jsx'

const API_REGION = {
  min_latitude: -0.06,
  max_latitude: 0.06,
  min_longitude: -0.06,
  max_longitude: 0.06,
}

function App() {
  const [view, setView] = useState('home')

  const [variable, setVariable] = useState('precipitation')
  const [timeIndex, setTimeIndex] = useState('0')

  const [regionalData, setRegionalData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [apiError, setApiError] = useState('')

  const [historicalData, setHistoricalData] = useState(null)
  const [historicalLoading, setHistoricalLoading] = useState(false)
  const [historicalError, setHistoricalError] = useState('')

  useEffect(() => {
    if (view !== 'workspace') return

    const controller = new AbortController()

    async function loadRegionalData() {
      setLoading(true)
      setApiError('')

      const params = new URLSearchParams({
        variable,
        ...Object.fromEntries(
          Object.entries(API_REGION).map(([key, value]) => [
            key,
            String(value),
          ])
        ),
        time_index: timeIndex,
      })

      try {
        const response = await fetch(
          `/api/gpm/regional?${params}`,
          { signal: controller.signal }
        )

        const result = await response.json()

        if (!response.ok) {
          throw new Error(
            typeof result.detail === 'string'
              ? result.detail
              : 'The regional data request failed.'
          )
        }

        setRegionalData(result)
      } catch (error) {
        if (error.name !== 'AbortError') {
          setRegionalData(null)
          setApiError(error.message || 'Unable to connect to the API.')
        }
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false)
        }
      }
    }

    loadRegionalData()

    return () => controller.abort()
  }, [view, variable, timeIndex])

  useEffect(() => {
    if (view !== 'workspace') return

    const controller = new AbortController()

    async function loadHistoricalData() {
      setHistoricalLoading(true)
      setHistoricalError('')

      try {
        const response = await fetch(
          '/api/gpm/historical-expanded',
          { signal: controller.signal }
        )

        const result = await response.json()

        if (!response.ok) {
          throw new Error(
            typeof result.detail === 'string'
              ? result.detail
              : 'The historical data request failed.'
          )
        }

        setHistoricalData(result)
      } catch (error) {
        if (error.name !== 'AbortError') {
          setHistoricalData(null)
          setHistoricalError(
            error.message || 'Unable to load historical data.'
          )
        }
      } finally {
        if (!controller.signal.aborted) {
          setHistoricalLoading(false)
        }
      }
    }

    loadHistoricalData()

    return () => controller.abort()
  }, [view])

  if (view === 'home') {
    return (
      <HomePage
        onLaunch={() => setView('workspace')}
      />
    )
  }

  return (
    <Workspace
      data={regionalData}
      loading={loading}
      error={apiError}
      variable={variable}
      setVariable={setVariable}
      timeIndex={timeIndex}
      setTimeIndex={setTimeIndex}
      historicalData={historicalData}
      historicalLoading={historicalLoading}
      historicalError={historicalError}
      onExit={() => setView('home')}
    />
  )
}

export default App
