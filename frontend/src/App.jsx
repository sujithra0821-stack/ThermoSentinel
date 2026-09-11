import { useEffect, useState } from 'react'
import {
  MapContainer,
  TileLayer,
  CircleMarker,
  Popup,
} from 'react-leaflet'

import 'leaflet/dist/leaflet.css'
import './App.css'

function App() {
  const [hotspots, setHotspots] = useState([])
  const [facilities, setFacilities] = useState([])
  const [filter, setFilter] = useState('ALL')

const thermalActivity = Array.from({ length: 24 }, (_, hour) => {
  return hotspots.filter((hotspot) => {
    if (hotspot.acq_time === undefined) {
      return false
    }

    const time = String(hotspot.acq_time).padStart(4, '0')
    const hotspotHour = parseInt(time.slice(0, 2), 10)

    return hotspotHour === hour
  }).length
})

  const highRisk = hotspots.filter(
  (hotspot) => hotspot.risk_level === 'HIGH'
).length

const mediumRisk = hotspots.filter(
  (hotspot) => hotspot.risk_level === 'MEDIUM'
).length

const lowRisk = hotspots.filter(
  (hotspot) => hotspot.risk_level === 'LOW'
).length

const filteredHotspots =
  filter === 'ALL'
    ? hotspots
    : hotspots.filter(
        (hotspot) => hotspot.classification === filter
      )
  useEffect(() => {
    fetch('http://127.0.0.1:8000/analyzed-hotspots')
      .then((response) => response.json())
      .then((data) => setHotspots(data.hotspots))
      .catch((error) => console.error('Hotspot error:', error))

    fetch('http://127.0.0.1:8000/facilities')
      .then((response) => response.json())
      .then((data) => setFacilities(data.facilities))
      .catch((error) => console.error('Facility error:', error))
  }, [])

  return (
    <div className="app">

      <header>
        <h1>ThermoSentinel</h1>
        <p>
          AI-Powered Industrial Fire & Persistent Thermal Source Intelligence
        </p>
      </header>
      <div className="filter-bar">

<button
  className={filter === 'ALL' ? 'active-filter' : ''}
  onClick={() => setFilter('ALL')}
>
  All Hotspots
</button>

<button
  className={filter === 'Possible Industrial Fire' ? 'active-filter' : ''}
  onClick={() => setFilter('Possible Industrial Fire')}
>
  Industrial Facility
</button>
  <button onClick={() => setFilter('Other Thermal Anomaly')}>
    Other Anomalies
  </button>

</div>

      <div className="dashboard">

        <div className="card">
          <h2>🔥 Thermal Hotspots</h2>
          <p>{hotspots.length}</p>
        </div>

        <div className="card">
          <h2>🏭 Industrial Facilities</h2>
          <p>{facilities.length}</p>
        </div>

        <div className="card">
          <h2>🤖 AI Classification</h2>
          <p>Active</p>
        </div>

      </div>
      <div className="risk-dashboard">

  <div className="risk-card">
    <h3>HIGH RISK</h3>
    <p>{highRisk}</p>
  </div>

  <div className="risk-card">
    <h3>MEDIUM RISK</h3>
    <p>{mediumRisk}</p>
  </div>

  <div className="risk-card">
    <h3>LOW RISK</h3>
    <p>{lowRisk}</p>
  </div>
  

</div>

  <div className="thermal-chart">
    <h2>📈 Thermal Activity — Last 24 Hours</h2>

    <div className="line-chart">
      <svg
        viewBox="0 0 960 300"
        width="100%"
        height="300"
        preserveAspectRatio="none"
      >
        {[50, 100, 150, 200, 250].map((y) => (
          <line
            key={y}
            x1="40"
            y1={y}
            x2="940"
            y2={y}
            stroke="#26344d"
            strokeWidth="1"
          />
        ))}

        <polyline
          fill="none"
          stroke="#f97316"
          strokeWidth="4"
          strokeLinejoin="round"
          strokeLinecap="round"
          points={thermalActivity
            .map((count, hour) => {
              const maxCount = Math.max(...thermalActivity, 1)
              const x = 40 + (hour / 23) * 900
              const y = 250 - (count / maxCount) * 200
              return `${x},${y}`
            })
            .join(' ')}
        />

        {thermalActivity.map((count, hour) => {
          const maxCount = Math.max(...thermalActivity, 1)
          const x = 40 + (hour / 23) * 900
          const y = 250 - (count / maxCount) * 200

          return (
            <circle
              key={hour}
              cx={x}
              cy={y}
              r="5"
              fill="#f97316"
            >
              <title>
                {count} detections at {hour}:00
              </title>
            </circle>
          )
        })}

        {thermalActivity.map((_, hour) => {
          const x = 40 + (hour / 23) * 900

          return (
            <text
              key={hour}
              x={x}
              y="280"
              textAnchor="middle"
              fill="#9ca3af"
              fontSize="12"
            >
              {hour}
            </text>
          )
        })}
      </svg>
    </div>
  </div>


      <div className="map-container">

        <MapContainer
          center={[20, 78]}
          zoom={5}
          style={{ height: '600px', width: '100%' }}
        >

          <TileLayer
            attribution='&copy; OpenStreetMap contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          {filteredHotspots.map((hotspot, index) => (

            <CircleMarker
              key={index}
              center={[hotspot.latitude, hotspot.longitude]}
              radius={7}
              pathOptions={{
                color:
                  hotspot.classification === 'Possible Industrial Fire'
                    ? 'red'
                    : 'orange',
              }}
            >

              <Popup>
                <strong>🔥 Thermal Hotspot</strong>

                <br />
                Latitude: {hotspot.latitude}

                <br />
                Longitude: {hotspot.longitude}

                <br />
                FRP: {hotspot.frp}

                <br />
                Confidence: {hotspot.confidence}

                <br />
                Classification:
                <strong> {hotspot.classification}</strong>

                <br />
                Risk Level:
                <strong> {hotspot.risk_level}</strong>

                <br />
                Persistence:
                <strong> {hotspot.persistence_status}</strong>

                <br />
                <br />
                <strong>Detection Intelligence</strong>

                <br />
                ✓ NASA FIRMS thermal anomaly detected
                
                <br />
                ✓ Industrial facility proximity analyzed
                
                <br />
                ✓ FRP evaluated
                
                <br />
                ✓ Risk level calculated
                
                <br />
                ✓ Persistence indicator evaluated

                <br />
                Nearest Facility:
                <br />
                {hotspot.nearest_facility}

                <br />
                Distance:
                {hotspot.distance_km} km
              </Popup>

            </CircleMarker>

          ))}

          {facilities.map((facility, index) => (

            <CircleMarker
              key={`facility-${index}`}
              center={[facility.latitude, facility.longitude]}
              radius={9}
              pathOptions={{
                color: 'blue',
                fillColor: 'blue',
                fillOpacity: 0.8,
              }}
            >

              <Popup>
                <strong>🏭 Industrial Facility</strong>

                <br />
                Name: {facility.name}

                <br />
                Type: {facility.type}
              </Popup>

            </CircleMarker>

          ))}

        </MapContainer>
        <div className="legend">
  <strong>Map Legend</strong>
  <div>🔴 Possible Industrial Fire</div>
  <div>🟠 Other Thermal Anomaly</div>
  <div>🔵 Industrial Facility</div>
</div>

      </div>

    </div>
  )
}

export default App