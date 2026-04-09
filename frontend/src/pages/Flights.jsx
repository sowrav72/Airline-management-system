import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../App'
import { flightsAPI } from '../services/api'

function Flights() {
  const { logout, user } = useAuth()
  const [airports, setAirports] = useState([])
  const [flights, setFlights] = useState([])
  const [loading, setLoading] = useState(false)
  const [searchParams, setSearchParams] = useState({ origin: '', destination: '', departure_date: '' })

  useEffect(() => {
    loadAirports()
  }, [])

  const loadAirports = async () => {
    try {
      const res = await flightsAPI.getAirports()
      setAirports(res.data)
    } catch (err) {
      console.error('Error loading airports:', err)
    }
  }

  const handleSearch = async (e) => {
    e.preventDefault()
    if (searchParams.origin === searchParams.destination) {
      alert('Origin and destination cannot be the same!')
      return
    }

    setLoading(true)
    try {
      const res = await flightsAPI.searchFlights(searchParams)
      setFlights(res.data)
    } catch (err) {
      console.error('Error searching flights:', err)
      alert('Error searching flights. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <nav className="navbar">
        <div className="container">
          <div className="nav-brand">✈️ SkyLink Airlines</div>
          <div className="nav-links">
            <Link to="/dashboard">Dashboard</Link>
            <Link to="/flights">Search Flights</Link>
            <Link to="/profile">Profile</Link>
            <a href="#" onClick={(e) => { e.preventDefault(); logout(); }}>Logout</a>
          </div>
        </div>
      </nav>

      <div className="container">
        <div className="search-form">
          <h2>🔍 Search Flights</h2>
          <form onSubmit={handleSearch}>
            <div className="search-grid">
              <div className="form-group">
                <label>From:</label>
                <select 
                  value={searchParams.origin}
                  onChange={(e) => setSearchParams({...searchParams, origin: e.target.value})}
                  required
                >
                  <option value="">Select Origin</option>
                  {airports.map(airport => (
                    <option key={airport.id} value={airport.code}>
                      {airport.code} - {airport.city}, {airport.country}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>To:</label>
                <select 
                  value={searchParams.destination}
                  onChange={(e) => setSearchParams({...searchParams, destination: e.target.value})}
                  required
                >
                  <option value="">Select Destination</option>
                  {airports.map(airport => (
                    <option key={airport.id} value={airport.code}>
                      {airport.code} - {airport.city}, {airport.country}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Date:</label>
                <input
                  type="date"
                  value={searchParams.departure_date}
                  onChange={(e) => setSearchParams({...searchParams, departure_date: e.target.value})}
                  min={new Date().toISOString().split('T')[0]}
                  required
                />
              </div>
            </div>
            <button type="submit" className="btn btn-primary" style={{ marginTop: '1rem' }}>
              🔍 Search Flights
            </button>
          </form>
        </div>

        {loading && <div className="loading">Searching for flights...</div>}

        {!loading && flights.length > 0 && (
          <div>
            <h2 style={{ color: 'white', marginBottom: '1rem' }}>Found {flights.length} Flight(s)</h2>
            {flights.map(flight => (
              <div key={flight.id} className="flight-card">
                <div className="flight-header">
                  <span className="flight-number">{flight.flight_number}</span>
                  <span className="flight-status">{flight.status}</span>
                </div>
                <div className="flight-route">
                  <div className="route-point">
                    <div className="code">{flight.origin.code}</div>
                    <div className="city">{flight.origin.city}</div>
                    <div className="time">{new Date(flight.departure_datetime).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}</div>
                  </div>
                  <div className="route-duration">
                    <div>✈️</div>
                    <div>{flight.duration} min</div>
                  </div>
                  <div className="route-point">
                    <div className="code">{flight.destination.code}</div>
                    <div className="city">{flight.destination.city}</div>
                    <div className="time">{new Date(flight.arrival_datetime).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}</div>
                  </div>
                </div>
                <div className="flight-pricing">
                  <div className="price-option">
                    <div className="price-label">Economy</div>
                    <div className="price-value">৳{flight.prices.economy.toLocaleString()}</div>
                    <div className="seats-available">{flight.available_seats.economy} seats</div>
                  </div>
                  <div className="price-option">
                    <div className="price-label">Business</div>
                    <div className="price-value">৳{flight.prices.business.toLocaleString()}</div>
                    <div className="seats-available">{flight.available_seats.business} seats</div>
                  </div>
                  <div className="price-option">
                    <div className="price-label">First Class</div>
                    <div className="price-value">৳{flight.prices.first.toLocaleString()}</div>
                    <div className="seats-available">{flight.available_seats.first} seats</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {!loading && flights.length === 0 && (
          <div className="empty-state" style={{ color: 'white' }}>
            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>✈️</div>
            <p>Search for available flights</p>
          </div>
        )}
      </div>

      <footer>
        <div className="container">
          <p>&copy; 2024 SkyLink Airlines. All rights reserved.</p>
        </div>
      </footer>
    </>
  )
}

export default Flights