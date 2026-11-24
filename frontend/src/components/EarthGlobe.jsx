
import { useEffect, useMemo, useRef, useState } from 'react'
import Globe from 'react-globe.gl'

export default function EarthGlobe({ data }) {
  const containerRef = useRef(null)
  const globeRef = useRef(null)

  const [dimensions, setDimensions] = useState({
    width: 720,
    height: 500,
  })

  const [globeReady, setGlobeReady] = useState(false)

  // Keep the globe responsive to its available panel size.
  useEffect(() => {
    const container = containerRef.current

    if (!container) return

    const observer = new ResizeObserver(([entry]) => {
      const width = Math.max(280, Math.floor(entry.contentRect.width))

      setDimensions({
        width,
        height: Math.max(360, Math.min(540, Math.floor(width * 0.72))),
      })
    })

    observer.observe(container)

    return () => observer.disconnect()
  }, [])

  // Display only valid observations returned by the backend.
  const observationPoints = useMemo(() => {
    const latitudes = data?.coordinates?.latitude ?? []
    const longitudes = data?.coordinates?.longitude ?? []
    const values = data?.values ?? []

    if (
      !Array.isArray(latitudes) ||
      !Array.isArray(longitudes) ||
      !Array.isArray(values)
    ) {
      return []
    }

    const points = []

    latitudes.forEach((latitude, rowIndex) => {
      longitudes.forEach((longitude, columnIndex) => {
        const rawValue = values[rowIndex]?.[columnIndex]

        if (
          rawValue === null ||
          rawValue === undefined ||
          !Number.isFinite(Number(rawValue)) ||
          !Number.isFinite(Number(latitude)) ||
          !Number.isFinite(Number(longitude))
        ) {
          return
        }

        points.push({
          lat: Number(latitude),
          lng: Number(longitude),
          value: Number(rawValue),
          label: `${Number(rawValue).toFixed(3)} ${data?.units || ''}`,
        })
      })
    })

    return points
  }, [data])

  // Focus the camera on the retrieved observation region.
  useEffect(() => {
    if (!globeReady || !globeRef.current || observationPoints.length === 0) {
      return
    }

    const centerLatitude =
      observationPoints.reduce((sum, point) => sum + point.lat, 0) /
      observationPoints.length

    const centerLongitude =
      observationPoints.reduce((sum, point) => sum + point.lng, 0) /
      observationPoints.length

    globeRef.current.pointOfView(
      {
        lat: centerLatitude,
        lng: centerLongitude,
        altitude: 1.65,
      },
      1400
    )
  }, [globeReady, observationPoints])

  return (
    <div className="earth-globe-shell" ref={containerRef}>
      <Globe
        ref={globeRef}
        width={dimensions.width}
        height={dimensions.height}

        // Earth appearance
        backgroundColor="rgba(0,0,0,0)"
        globeImageUrl="//unpkg.com/three-globe/example/img/earth-blue-marble.jpg"
        bumpImageUrl="//unpkg.com/three-globe/example/img/earth-topology.png"
        showAtmosphere
        atmosphereColor="#00bfff"
        atmosphereAltitude={0.16}
        showGraticules
        animateIn
        enablePointerInteraction

        // Actual regional observation markers
        pointsData={observationPoints}
        pointLat="lat"
        pointLng="lng"
        pointAltitude={0.025}
        pointRadius={0.14}
        pointResolution={12}
        pointColor={() => '#00e5ff'}
        pointLabel="label"

        // Restrained animated observation highlights
        ringsData={observationPoints}
        ringLat="lat"
        ringLng="lng"
        ringColor={() => '#00e5ff'}
        ringMaxRadius={1.4}
        ringPropagationSpeed={0.8}
        ringRepeatPeriod={1800}

        onGlobeReady={() => setGlobeReady(true)}
      />
    </div>
  )
}
