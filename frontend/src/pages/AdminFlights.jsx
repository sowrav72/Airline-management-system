import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../App'
import { flightsAPI } from '../services/api'

function AdminFlights() {
  const { logout, user } = useAuth()
  const [flights, setFlights] = useState([])
  const [airports, setAirports] = useState([])
  const [aircraft, setAircraft] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [formData, setFormData] = useState({ flight_number: '', route_id: 1, aircraft_id: '', departure_datetime: '', arrival_datetime: '', gate: '' })

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [flightsRes, airportsRes, aircraftRes] = await Promise.all([
        flightsAPI.searchFlights({}),
        flightsAPI.getAirports(),
        flightsAPI.getAircraft()
      ])
      setFlights(flightsRes.data)
      setAirports(airportsRes.data)
      setAircraft(aircraftRes.data)
    } catch (err) {
      console.error('Error loading data:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    try {
      await flightsAPI.createAircraft(formData)
      setShowModal(false)
      loadData()
    } catch (err) {
      alert(err.response?.data?.detail || 'Error creating flight')
    }
  }

  return (
    <>
      <nav className="navbar">
        <div className="container">
          <div className="nav-brand">✈️ SkyLink Airlines - Admin</div>
          <div className="nav-links">
            <Link to="/dashboard">Dashboard</Link>
            <Link to="/admin/aircraft">Aircraft</Link>
            <Link to="/admin/flights">Flights</Link>
            <Link to="/flights">Search Flights</Link>
            <Link to="/profile">Profile</Link>
            <a href="#" onClick={(e) => { e.preventDefault(); logout(); }}>Logout</a>
          </div>
        </div>
      </nav>

      <div className="container">
        <div className="form-container" style={{ maxWidth: '100%', marginTop: '2rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
            <h2>🛫 Flight Management</h2>
            <button className="btn btn-primary" onClick={() => setShowModal(true)} style={{ width: 'auto' }}>+ Create New Flight</button>
          </div>

          {loading ? (
            <div className="loading">Loading...</div>
          ) : flights.length === 0 ? (
            <div className="empty-state">No flights found.</div>
          ) : (
            <div style={{ display: 'grid', gap: '1rem' }}>
              {flights.map(f => (
                <div key={f.id} style={{ border: '2px solid #e0e0e0', borderRadius: '12px', padding: '1rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <span style={{ fontSize: '1.25rem', fontWeight: 'bold', color: '#667eea' }}>{f.flight_number}</span>
                    <p style={{ margin: '0.5rem 0' }}>
                      {f.origin?.code} → {f.destination?.code} | {new Date(f.departure_datetime).toLocaleDateString()}
                    </p>
                  </div>
                  <span style={{ padding: '0.3rem 1rem', borderRadius: '20px', fontSize: '0.8rem', background: f.status === 'scheduled' ? '#e8f5e9' : '#fff3e0', color: f.status === 'scheduled' ? '#2e7d32' : '#ef6c00' }}>
                    {f.status}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <footer>
        <div className="container">
          <p>&copy; 2024 SkyLink Airlines. All rights reserved.</p>
        </div>
      </footer>
    </>
  )
}

export default AdminFlights