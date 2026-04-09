import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { authAPI } from '../services/api'

function Register() {
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    phone: '',
    password: '',
    role: 'passenger',
    staff_id: ''
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value,
      ...(name === 'role' && value === 'passenger' ? { staff_id: '' } : {})
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const data = { ...formData }
      if (data.role === 'passenger') {
        delete data.staff_id
      }

      await authAPI.register(data)
      alert('Registration successful! Please login.')
      navigate('/login')
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed. Please try again.')
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
            <Link to="/">Home</Link>
            <Link to="/login">Login</Link>
          </div>
        </div>
      </nav>

      <div className="container">
        <div className="form-container">
          <h2>✈️ Create Your Account</h2>
          
          {error && <div className="error-message">{error}</div>}

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Full Name <span className="required-indicator">*</span></label>
              <input
                type="text"
                name="full_name"
                value={formData.full_name}
                onChange={handleChange}
                placeholder="Enter your full name"
                required
              />
            </div>

            <div className="form-group">
              <label>Email Address <span className="required-indicator">*</span></label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="your.email@example.com"
                required
              />
            </div>

            <div className="form-group">
              <label>Phone Number (Optional)</label>
              <input
                type="tel"
                name="phone"
                value={formData.phone}
                onChange={handleChange}
                placeholder="+880 1234 567890"
              />
            </div>

            <div className="form-group">
              <label>Password <span className="required-indicator">*</span></label>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="Minimum 6 characters"
                required
              />
            </div>

            <div className="form-group">
              <label>Account Type <span className="required-indicator">*</span></label>
              <select name="role" value={formData.role} onChange={handleChange} required>
                <option value="passenger">Passenger</option>
                <option value="staff">Staff</option>
                <option value="admin">Admin</option>
              </select>
              <div className="field-note">ℹ️ Select "Passenger" for regular customers. Staff/Admin require an authorized ID.</div>
            </div>

            {formData.role !== 'passenger' && (
              <div className="form-group">
                <label>Staff ID <span className="required-indicator">*</span></label>
                <input
                  type="text"
                  name="staff_id"
                  value={formData.staff_id}
                  onChange={handleChange}
                  placeholder="e.g., STAFF001 or ADMIN001"
                  required={formData.role !== 'passenger'}
                />
                <div className="field-note">🔐 Only authorized personnel with valid Staff ID can register as Staff/Admin.</div>
              </div>
            )}

            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Creating Account...' : 'Create Account'}
            </button>
          </form>

          <p className="form-footer">
            Already have an account? <Link to="/login">Login here</Link>
          </p>
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

export default Register