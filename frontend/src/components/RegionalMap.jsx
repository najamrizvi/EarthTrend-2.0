
import { useEffect, useMemo, useState } from 'react'
import {
  MapContainer,
  TileLayer,
  Rectangle,
  Tooltip,
  useMap,
} from 'react-leaflet'

function MapViewport({ bounds, viewMode }) {
  const map = useMap()

  useEffect(() => {
    const timer = window.setTimeout(() => {
      map.invalidateSize()

      if (viewMode === 'global') {
        map.setView([20, 0], 2)
      } else {
        map.fitBounds(bounds, {
          padding: [45, 45],
          maxZoom: 12,
        })
      }
    }, 150)

    return () => window.clearTimeout(timer)
  }, [map, bounds, viewMode])

  return null
}

function getCellColor(value, min, max) {
  if (
    value === null ||
    value === undefined ||
    !Number.isFinite(Number(value))
  ) {
    return '#64748b'
  }

  const ratio = max === min
    ? 0.5
    : (Number(value) - min) / (max - min)

  const red = Math.round(30 + ratio * 190)
  const green = Math.round(110 + (1 - ratio) * 95)
  const blue = Math.round(175 - ratio * 120)

  return `rgb(${red}, ${green}, ${blue})`
}

export default function RegionalMap({ data }) {
  const [viewMode, setViewMode] = useState('global')

  const latitude = data?.coordinates?.latitude ?? []
  const longitude = data?.coordinates?.longitude ?? []
  const values = data?.values ?? []

  const resolution =
    Number(data?.spatial_resolution?.split(' ')[0]) || 0.1

  const halfCell = resolution / 2

  const cells = useMemo(
    () =>
      latitude.flatMap((lat, rowIndex) =>
        longitude.map((lon, columnIndex) => ({
          id: `${rowIndex}-${columnIndex}`,
          lat,
          lon,
          value: values[rowIndex]?.[columnIndex] ?? null,
        }))
      ),
    [latitude, longitude, values]
  )

  const numericValues = cells
    .filter(
      (cell) =>
        cell.value !== null &&
        cell.value !== undefined &&
        Number.isFinite(Number(cell.value))
    )
    .map((cell) => Number(cell.value))

  const min = numericValues.length
    ? Math.min(...numericValues)
    : null

  const max = numericValues.length
    ? Math.max(...numericValues)
    : null

  if (!latitude.length || !longitude.length) {
    return (
      <div className="regional-map">
        <div className="data-message">
          No geographic coordinates available.
        </div>
      </div>
    )
  }

  const bounds = [
    [
      Math.min(...latitude) - halfCell,
      Math.min(...longitude) - halfCell,
    ],
    [
      Math.max(...latitude) + halfCell,
      Math.max(...longitude) + halfCell,
    ],
  ]

  return (
    <div className="regional-map">
      <div className="regional-map-toolbar">
        <span className="regional-map-mode">
          {viewMode === 'global'
            ? 'GLOBAL EARTH VIEW'
            : 'REGIONAL OBSERVATION VIEW'}
        </span>

        <div className="regional-map-actions">
          <button
            type="button"
            className={viewMode === 'global' ? 'active' : ''}
            onClick={() => setViewMode('global')}
          >
            Global Earth
          </button>

          <button
            type="button"
            className={viewMode === 'regional' ? 'active' : ''}
            onClick={() => setViewMode('regional')}
          >
            Observation Grid
          </button>
        </div>
      </div>

      <MapContainer
        center={[20, 0]}
        zoom={2}
        minZoom={2}
        maxZoom={18}
        scrollWheelZoom
        style={{ height: '100%', width: '100%' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        <MapViewport
          bounds={bounds}
          viewMode={viewMode}
        />

        {cells.map((cell) => (
          <Rectangle
            key={cell.id}
            bounds={[
              [cell.lat - halfCell, cell.lon - halfCell],
              [cell.lat + halfCell, cell.lon + halfCell],
            ]}
            pathOptions={{
              color: '#e2e8f0',
              weight: 1,
              fillColor: getCellColor(cell.value, min ?? 0, max ?? 1),
              fillOpacity: 0.75,
            }}
          >
            <Tooltip>
              <strong>
                {(data.variable || 'Observation').replaceAll('_', ' ')}
              </strong>
              <br />
              Latitude: {cell.lat.toFixed(3)}°
              <br />
              Longitude: {cell.lon.toFixed(3)}°
              <br />
              Value: {
                cell.value === null
                  ? 'No data'
                  : Number(cell.value).toFixed(3)
              }
              <br />
              Units: {data.units || 'Not specified'}
            </Tooltip>
          </Rectangle>
        ))}
      </MapContainer>

      <div className="regional-map-legend">
        <div className="regional-map-legend-heading">
          <span>OBSERVATION INTENSITY</span>
          <span>{data.units || 'Units unavailable'}</span>
        </div>

        <div
          className="regional-map-gradient"
          role="img"
          aria-label="Relative observation color scale from minimum to maximum"
        />

        <div className="regional-map-legend-values">
          <span>
            MIN: {min === null ? '—' : min.toFixed(4)}
          </span>

          <span>
            MAX: {max === null ? '—' : max.toFixed(4)}
          </span>
        </div>

        <div className="regional-map-missing">
          <span />
          Missing observation
        </div>
      </div>
    </div>
  )
}
