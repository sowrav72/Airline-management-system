import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../App'
import { userAPI } from '../services/api'

function Dashboard() {
  const { user, logout } = useAuth()
  const [profile, setProfile] = useState(null)
  const [activityLogs, setActivityLogs] = useState([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [profileRes, logsRes] = await Promise.all([
        userAPI.getProfile(),
        userAPI.getActivityLogs()
      ])
      setProfile(profileRes.data)
      setActivityLogs(logsRes.data)
    } catch (err) {
      if (err.response?.status === 401) {
        logout()
        navigate('/login')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = async () => {
    try {
      await userAPI.logout()
    } catch (err) {
      console.error('Logout error:', err)
    }
    logout()
    navigate('/')
  }

  if (loading) {
    return <div className="loading">Loading...</div>
  }

  const roleText = user?.role === 'admin' ? '👑 Admin Dashboard - Full System Control' : 
                   user?.role === 'staff' ? '🧑‍✈️ Staff Dashboard - Manage Operations' : 
                   '✈️ Search flights and manage your bookings'

  return (
    <>
      <nav className="navbar">
        <div className="container">
          <div className="nav-brand">✈️ SkyLink Airlines</div>
          <div className="nav-links">
            <Link to="/dashboard">Dashboard</Link>
            {user?.role !== 'passenger' && (
              <>
                <Link to="/admin/aircraft">Aircraft</Link>
                <Link to="/admin/flights">Flights</Link>
              </>
            )}
            <Link to="/flights">Search Flights</Link>
            <Link to="/profile">Profile</Link>
            <a href="#" onClick={(e) => { e.preventDefault(); handleLogout(); }}>Logout</a>
          </div>
        </div>
      </nav>

      <div className="container">
        <div style={{ background: 'white', padding: '2rem', borderRadius: '20px', margin: '3rem 0', boxShadow: '0 10px 30px rgba(0,0,0,0.1)' }}>
          <h1 style={{ color: '#667eea', marginBottom: '0.5rem' }}>
            Welcome, {profile?.full_name}! ✈️
          </h1>
          <p style={{ color: '#666', fontSize: '1.1rem' }}>{roleText}</p>
        </div>

        <div className="quick-actions">
          {user?.role === 'passenger' ? (
            <>
              <Link to="/flights" className="quick-action-card">
                <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>🔍</div>
                <div>Search Flights</div>
              </Link>
              <Link to="/profile" className="quick-action-card">
                <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>👤</div>
                <div>My Profile</div>
              </Link>
            </>
          ) : (
            <>
              <Link to="/admin/aircraft" className="quick-action-card">
                <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>✈️</div>
                <div>Manage Aircraft</div>
              </Link>
              <Link to="/admin/flights" className="quick-action-card">
                <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>🛫</div>
                <div>Manage Flights</div>
              </Link>
              <Link to="/flights" className="quick-action-card">
                <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>🔍</div>
                <div>Search Flights</div>
              </Link>
              <Link to="/profile" className="quick-action-card">
                <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>👤</div>
                <div>My Profile</div>
              </Link>
            </>
          )}
        </div>

        <div className="dashboard-cards">
          <div className="card">
            <h3>👤 User Information</h3>
            <div>
              <p><strong>📧 Email:</strong> {profile?.email}</p>
              <p><strong>👤 Role:</strong> <span className={`badge badge-${profile?.role}`}>{profile?.role}</span></p>
              <p><strong>📱 Phone:</strong> {profile?.phone || 'Not provided'}</p>
              <p><strong>✅ Verified:</strong> {profile?.is_verified ? 'Yes' : 'No'}</p>
            </div>
          </div>

          <div className="card">
            <h3>📊 Recent Activity</h3>
            {activityLogs.length === 0 ? (
              <p style={{ color: '#999' }}>No recent activity</p>
            ) : (
              activityLogs.slice(0, 5).map(log => (
                <div key={log.id} style={{ padding: '0.5rem 0', borderBottom: '1px solid #f0f0f0' }}>
                  <strong>{log.action}</strong>
                  <p style={{ fontSize: '0.85rem', color: '#666' }}>{log.details || 'No details'}</p>
                </div>
              ))
            )}
          </div>
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

export default Dashboard