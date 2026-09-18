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
  const [incidents, setIncidents] = useState([])

  const industrialHotspots = hotspots.filter(
  (hotspot) => hotspot.classification === 'Possible Industrial Fire'
).length

const persistentSources = hotspots.filter(
  (hotspot) => hotspot.persistence_status === 'Persistent Thermal Source'
).length

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
  const loadDashboardData = async () => {
    try {
      // 1. Load NASA FIRMS analyzed hotspots
      const hotspotResponse = await fetch(
        'http://127.0.0.1:8001/analyzed-hotspots'
      )

      if (!hotspotResponse.ok) {
        throw new Error('Failed to load hotspot data')
      }

      const hotspotData = await hotspotResponse.json()

      setHotspots(hotspotData.hotspots)

      // 2. Load industrial facilities
      const facilityResponse = await fetch(
        'http://127.0.0.1:8001/facilities'
      )

      if (!facilityResponse.ok) {
        throw new Error('Failed to load facility data')
      }

      const facilityData = await facilityResponse.json()

      setFacilities(facilityData.facilities)

      // 3. Load thermal incidents
      const incidentResponse = await fetch(
        'http://127.0.0.1:8001/incidents'
      )

      if (!incidentResponse.ok) {
        throw new Error('Failed to load incident data')
      }

      const incidentData = await incidentResponse.json()

      setIncidents(incidentData.incidents)

    } catch (error) {
      console.error('Dashboard data error:', error)
    }
  }

  loadDashboardData()
}, [])

  return (
    <div className="app">

    <header className="main-header">
  <div className="brand-section">
    <div className="brand-icon">🔥</div>

    <div>
      <h1>ThermoSentinel</h1>
      <p>
        AI-Powered Industrial Fire & Persistent Thermal Source Intelligence
      </p>
    </div>
  </div>

  <nav className="main-navigation">
    <a href="#command-center">Command Center</a>
    <a href="#incidents">Incidents</a>
    <a href="#analytics">Analytics</a>
    <a href="#map">Live Map</a>
    <a href="#facilities">Facilities</a>
  </nav>

  <div className="header-status">
    <span className="status-dot"></span>
    <span>SYSTEM LIVE</span>
  </div>
</header>

      <div className="system-status">
  <div className="status-item">
    <span className="status-dot"></span>
    <strong>SYSTEM LIVE</strong>
  </div>

  <div className="status-item">
    <span>🛰️</span>
    NASA FIRMS
  </div>

  <div className="status-item">
    <span>📡</span>
    VIIRS SNPP NRT
  </div>

  <div className="status-item">
    <span>🔥</span>
    {hotspots.length} observations
  </div>

  <div className="status-item">
    <span>🕐</span>
    Near Real-Time
  </div>
</div>
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

      <div className="dashboard" id="command-center">

        <div className="card">
  <h2>🔥 Total Hotspots</h2>
  <p>{hotspots.length}</p>
  <span>NASA FIRMS detections</span>
</div>

<div className="card">
  <h2>🏭 Industrial Links</h2>
  <p>{industrialHotspots}</p>
  <span>Potential industrial association</span>
</div>

<div className="card">
  <h2>🚨 High Risk</h2>
  <p>{highRisk}</p>
  <span>Priority monitoring</span>
</div>

<div className="card">
  <h2>♨️ Persistent Sources</h2>
  <p>{persistentSources}</p>
  <span>Elevated thermal activity</span>
</div>
      </div>
      <div className="risk-dashboard">

  <div className="risk-card high">
  <div className="risk-icon">🚨</div>
  <h3>HIGH RISK</h3>
  <p>{highRisk}</p>
  <span>Immediate attention</span>
</div>

<div className="risk-card medium">
  <div className="risk-icon">⚠️</div>
  <h3>MEDIUM RISK</h3>
  <p>{mediumRisk}</p>
  <span>Requires monitoring</span>
</div>

<div className="risk-card low">
  <div className="risk-icon">🟢</div>
  <h3>LOW RISK</h3>
  <p>{lowRisk}</p>
  <span>Normal monitoring</span>
</div>


</div>

<div className="analytics-panel" id="analytics">

  <div className="analytics-header">
    <div>
      <h2>📊 Thermal Intelligence</h2>
      <p>Real-time analysis of detected thermal activity</p>
    </div>
  </div>

  <div className="analytics-grid">

    <div className="analytics-item">
      <div className="analytics-label">
        <span>🔥 Thermal Detections</span>
        <strong>{hotspots.length}</strong>
      </div>
      <div className="progress-track">
        <div
          className="progress-fill"
          style={{
            width: `${Math.min((hotspots.length / 1500) * 100, 100)}%`
          }}
        ></div>
      </div>
    </div>

    <div className="analytics-item">
      <div className="analytics-label">
        <span>🏭 Industrial Associations</span>
        <strong>{industrialHotspots}</strong>
      </div>
      <div className="progress-track">
        <div
          className="progress-fill"
          style={{
            width: `${Math.min((industrialHotspots / Math.max(hotspots.length, 1)) * 100, 100)}%`
          }}
        ></div>
      </div>
    </div>

    <div className="analytics-item">
      <div className="analytics-label">
        <span>🚨 High Risk</span>
        <strong>{highRisk}</strong>
      </div>
      <div className="progress-track">
        <div
          className="progress-fill"
          style={{
            width: `${Math.min((highRisk / Math.max(hotspots.length, 1)) * 100, 100)}%`
          }}
        ></div>
      </div>
    </div>

    <div className="analytics-item">
      <div className="analytics-label">
        <span>♨️ Persistent Sources</span>
        <strong>{persistentSources}</strong>
      </div>
      <div className="progress-track">
        <div
          className="progress-fill"
          style={{
            width: `${Math.min((persistentSources / Math.max(hotspots.length, 1)) * 100, 100)}%`
          }}
        ></div>
      </div>
    </div>

  </div>

</div>

<div className="incident-center" id="incidents">

  <div className="analytics-header">
    <div>
      <h2>🚨 Incident Center</h2>
      <p>Thermal events derived from NASA FIRMS observations</p>
    </div>

    <div className="incident-count">
      {incidents.length} incidents
    </div>
  </div>

  <div className="incident-table">

    <div className="incident-table-header">
      <span>INCIDENT</span>
      <span>RISK</span>
      <span>OBS.</span>
      <span>MAX FRP</span>
      <span>PERSISTENCE</span>
      <span>INDUSTRIAL LINK</span>
    </div>

    {incidents.slice(0, 10).map((incident) => (

      <div className="incident-row" key={incident.incident_id}>

        <div>
          <strong>{incident.incident_id}</strong>
          <small>
            {incident.center_latitude.toFixed(4)},
            {' '}
            {incident.center_longitude.toFixed(4)}
          </small>
        </div>

        <span
          className={`risk-badge ${incident.risk_level.toLowerCase()}`}
        >
          {incident.risk_level}
        </span>

        <span>{incident.observation_count}</span>

        <span>{incident.maximum_frp} MW</span>

        <span>{incident.persistence_days} day(s)</span>

        <span>
          {incident.industrial_link ? (
            <strong className="industrial-yes">YES</strong>
          ) : (
            <span className="industrial-no">NONE</span>
          )}
        </span>

      </div>

    ))}

  </div>

  <div className="incident-footer-note">
    Showing 10 of {incidents.length} detected incidents
  </div>

</div>

<div className="facilities-section" id="facilities">
  <div className="analytics-header">
    <div>
      <h2>🏭 Industrial Facilities Intelligence</h2>
      <p>Industrial infrastructure identified from OpenStreetMap</p>
    </div>

    <div className="incident-count">
      {facilities.length} facilities
    </div>
  </div>

  <div className="facilities-grid">
    {facilities.slice(0, 12).map((facility) => (
      <div className="facility-card" key={`${facility.osm_type}-${facility.osm_id}`}>
        <div className="facility-icon">🏭</div>

        <div>
          <h3>{facility.name || 'Unnamed Facility'}</h3>

          <p>
            {facility.type || 'Industrial Facility'}
          </p>

          {facility.operator && (
            <small>
              Operator: {facility.operator}
            </small>
          )}
        </div>
      </div>
    ))}
  </div>

  <div className="incident-footer-note">
    Showing {Math.min(facilities.length, 12)} of {facilities.length} facilities
  </div>
</div>

      <div className="map-container" id="map">

        <MapContainer
        center={[20, 78]}
        zoom={5}
        style={{ height: '650px', width: '100%' }}
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
    hotspot.risk_level === 'HIGH'
      ? 'red'
      : hotspot.risk_level === 'MEDIUM'
        ? 'orange'
        : 'green',
  fillColor:
    hotspot.risk_level === 'HIGH'
      ? 'red'
      : hotspot.risk_level === 'MEDIUM'
        ? 'orange'
        : 'green',
  fillOpacity: 0.8,
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
  <div>🔴 High Risk</div>
  <div>🟠 Medium Risk</div>
  <div>🟢 Low Risk</div>
  <div>🔵 Industrial Facility</div>
</div>

      </div>

    </div>
  )
}

export default App