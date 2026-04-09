import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../App'
import { flightsAPI } from '../services/api'

function AdminAircraft() {
  const { logout, user } = useAuth()
  const [aircraft, setAircraft] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [editingAircraft, setEditingAircraft] = useState(null)
  const [formData, setFormData] = useState({ aircraft_number: '', manufacturer: '', model: '', economy_seats: 0, business_seats: 0, first_class_seats: 0, status: 'active' })

  useEffect(() => {
    loadAircraft()
  }, [])

  const loadAircraft = async () => {
    try {
      const res = await flightsAPI.getAircraft()
      setAircraft(res.data)
    } catch (err) {
      console.error('Error loading aircraft:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    try {
      const data = {
        ...formData,
        total_seats: formData.economy_seats + formData.business_seats + formData.first_class_seats
      }
      
      if (editingAircraft) {
        await flightsAPI.updateAircraft(editingAircraft.id, data)
      } else {
        await flightsAPI.createAircraft(data)
      }
      
      setShowModal(false)
      setEditingAircraft(null)
      setFormData({ aircraft_number: '', manufacturer: '', model: '', economy_seats: 0, business_seats: 0, first_class_seats: 0, status: 'active' })
      loadAircraft()
    } catch (err) {
      alert(err.response?.data?.detail || 'Error saving aircraft')
    }
  }

  const openCreate = () => {
    setEditingAircraft(null)
    setFormData({ aircraft_number: '', manufacturer: '', model: '', economy_seats: 150, business_seats: 20, first_class_seats: 6, status: 'active' })
    setShowModal(true)
  }

  const openEdit = (a) => {
    setEditingAircraft(a)
    setFormData({ aircraft_number: a.aircraft_number, manufacturer: a.manufacturer, model: a.model, economy_seats: a.economy_seats, business_seats: a.business_seats, first_class_seats: a.first_class_seats, status: a.status })
    setShowModal(true)
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
            <h2>✈️ Aircraft Fleet Management</h2>
            <button className="btn btn-primary" onClick={openCreate} style={{ width: 'auto' }}>+ Add New Aircraft</button>
          </div>

          {loading ? (
            <div className="loading">Loading...</div>
          ) : aircraft.length === 0 ? (
            <div className="empty-state">No aircraft found. Add one to get started.</div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1rem' }}>
              {aircraft.map(a => (
                <div key={a.id} style={{ border: '2px solid #e0e0e0', borderRadius: '12px', padding: '1rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
                    <span style={{ fontSize: '1.25rem', fontWeight: 'bold', color: '#667eea' }}>{a.aircraft_number}</span>
                    <span style={{ padding: '0.2rem 0.8rem', borderRadius: '12px', fontSize: '0.75rem', background: a.status === 'active' ? '#e8f5e9' : '#fff3e0', color: a.status === 'active' ? '#2e7d32' : '#ef6c00' }}>{a.status}</span>
                  </div>
                  <p><strong>Manufacturer:</strong> {a.manufacturer}</p>
                  <p><strong>Model:</strong> {a.model}</p>
                  <p><strong>Total Seats:</strong> {a.total_seats}</p>
                  <div style={{ display: 'flex', gap: '0.5rem', marginTop: '1rem' }}>
                    <button className="btn" onClick={() => openEdit(a)} style={{ background: '#ffc107', color: '#333', width: 'auto', padding: '8px 16px' }}>Edit</button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {showModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, width: '100%', height: '100%', background: 'rgba(0,0,0,0.5)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000 }}>
          <div style={{ background: 'white', padding: '2rem', borderRadius: '15px', width: '90%', maxWidth: '500px' }}>
            <h3>{editingAircraft ? 'Edit Aircraft' : 'Add New Aircraft'}</h3>
            <div className="form-group">
              <label>Aircraft Number</label>
              <input value={formData.aircraft_number} onChange={(e) => setFormData({...formData, aircraft_number: e.target.value})} disabled={!!editingAircraft} />
            </div>
            <div className="form-group">
              <label>Manufacturer</label>
              <input value={formData.manufacturer} onChange={(e) => setFormData({...formData, manufacturer: e.target.value})} />
            </div>
            <div className="form-group">
              <label>Model</label>
              <input value={formData.model} onChange={(e) => setFormData({...formData, model: e.target.value})} />
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem' }}>
              <div className="form-group">
                <label>Economy</label>
                <input type="number" value={formData.economy_seats} onChange={(e) => setFormData({...formData, economy_seats: parseInt(e.target.value)})} />
              </div>
              <div className="form-group">
                <label>Business</label>
                <input type="number" value={formData.business_seats} onChange={(e) => setFormData({...formData, business_seats: parseInt(e.target.value)})} />
              </div>
              <div className="form-group">
                <label>First Class</label>
                <input type="number" value={formData.first_class_seats} onChange={(e) => setFormData({...formData, first_class_seats: parseInt(e.target.value)})} />
              </div>
            </div>
            <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
              <button className="btn btn-primary" onClick={handleSave} style={{ flex: 1 }}>Save</button>
              <button className="btn" onClick={() => setShowModal(false)} style={{ flex: 1, background: '#f0f0f0' }}>Cancel</button>
            </div>
          </div>
        </div>
      )}

      <footer>
        <div className="container">
          <p>&copy; 2024 SkyLink Airlines. All rights reserved.</p>
        </div>
      </footer>
    </>
  )
}

export default AdminAircraft