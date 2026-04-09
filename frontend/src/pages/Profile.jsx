import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../App'
import { userAPI } from '../services/api'

function Profile() {
  const { user, logout } = useAuth()
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)
  const [editing, setEditing] = useState(false)
  const [formData, setFormData] = useState({ full_name: '', phone: '', password: '' })
  const navigate = useNavigate()

  useEffect(() => {
    loadProfile()
  }, [])

  const loadProfile = async () => {
    try {
      const res = await userAPI.getProfile()
      setProfile(res.data)
      setFormData({ full_name: res.data.full_name, phone: res.data.phone || '', password: '' })
    } catch (err) {
      if (err.response?.status === 401) {
        logout()
        navigate('/login')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    try {
      const data = {}
      if (formData.full_name) data.full_name = formData.full_name
      if (formData.phone) data.phone = formData.phone
      if (formData.password) data.password = formData.password
      
      await userAPI.updateProfile(data)
      setEditing(false)
      loadProfile()
      alert('Profile updated successfully!')
    } catch (err) {
      alert('Error updating profile')
    }
  }

  const handlePhotoUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    try {
      await userAPI.uploadPhoto(file)
      loadProfile()
      alert('Photo uploaded successfully!')
    } catch (err) {
      alert('Error uploading photo')
    }
  }

  if (loading) return <div className="loading">Loading...</div>

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
        <div className="profile-section">
          <div className="profile-header">
            {profile?.profile_photo ? (
              <img src={profile.profile_photo} alt="Profile" className="profile-photo" />
            ) : (
              <div style={{ width: '100px', height: '100px', borderRadius: '50%', background: '#667eea', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontSize: '2rem' }}>
                {profile?.full_name?.charAt(0) || 'U'}
              </div>
            )}
            <div className="profile-info">
              <h2>
                {profile?.full_name}
                <span className={`badge badge-${profile?.role}`}>{profile?.role}</span>
              </h2>
              <p>{profile?.email}</p>
              <label className="btn btn-primary" style={{ marginTop: '0.5rem', display: 'inline-block', width: 'auto', padding: '8px 16px' }}>
                Change Photo
                <input type="file" accept="image/*" onChange={handlePhotoUpload} style={{ display: 'none' }} />
              </label>
            </div>
          </div>

          {editing ? (
            <div>
              <div className="form-group">
                <label>Full Name</label>
                <input type="text" value={formData.full_name} onChange={(e) => setFormData({...formData, full_name: e.target.value})} />
              </div>
              <div className="form-group">
                <label>Phone</label>
                <input type="tel" value={formData.phone} onChange={(e) => setFormData({...formData, phone: e.target.value})} />
              </div>
              <div className="form-group">
                <label>New Password (leave blank to keep current)</label>
                <input type="password" value={formData.password} onChange={(e) => setFormData({...formData, password: e.target.value})} />
              </div>
              <button className="btn btn-primary" onClick={handleSave} style={{ marginRight: '0.5rem' }}>Save</button>
              <button className="btn" onClick={() => setEditing(false)} style={{ background: '#f0f0f0' }}>Cancel</button>
            </div>
          ) : (
            <div>
              <p><strong>Email:</strong> {profile?.email}</p>
              <p><strong>Phone:</strong> {profile?.phone || 'Not provided'}</p>
              <p><strong>Role:</strong> {profile?.role}</p>
              <p><strong>Verified:</strong> {profile?.is_verified ? 'Yes' : 'No'}</p>
              <p><strong>Member Since:</strong> {new Date(profile?.created_at).toLocaleDateString()}</p>
              <button className="btn btn-primary" onClick={() => setEditing(true)} style={{ marginTop: '1rem' }}>Edit Profile</button>
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

export default Profile