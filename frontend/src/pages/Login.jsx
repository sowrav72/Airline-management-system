import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../App'
import { authAPI } from '../services/api'

function Login() {
  const [loginType, setLoginType] = useState('passenger')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [staffId, setStaffId] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    const data = {
      email,
      password,
      ...(loginType === 'staff' && { staff_id: staffId })
    }

    try {
      const response = await authAPI.login(data)
      login(response.data.user, response.data.access_token)
      navigate('/dashboard')
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed. Please try again.')
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
            <Link to="/register">Register</Link>
          </div>
        </div>
      </nav>

      <div className="container">
        <div className="form-container">
          <h2>🔐 Welcome Back</h2>
          
          <div className="login-type-selector">
            <button
              type="button"
              className={`login-type-btn ${loginType === 'passenger' ? 'active' : ''}`}
              onClick={() => setLoginType('passenger')}
            >
              👤 Passenger
            </button>
            <button
              type="button"
              className={`login-type-btn ${loginType === 'staff' ? 'active' : ''}`}
              onClick={() => setLoginType('staff')}
            >
              🧑‍✈️ Staff/Admin
            </button>
          </div>

          {error && <div className="error-message">{error}</div>}

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Email Address</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="your.email@example.com"
                required
              />
            </div>

            {loginType === 'staff' && (
              <div className="form-group">
                <label>Staff ID <span className="required-indicator">*</span></label>
                <input
                  type="text"
                  value={staffId}
                  onChange={(e) => setStaffId(e.target.value)}
                  placeholder="e.g., STAFF001 or ADMIN001"
                  required={loginType === 'staff'}
                />
                <div className="field-note">🔐 Enter your authorized Staff ID</div>
              </div>
            )}

            <div className="form-group">
              <label>Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                required
              />
            </div>

            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Logging in...' : 'Login to Dashboard'}
            </button>
          </form>

          <p className="form-footer">
            <Link to="/forgot-password">Forgot Password?</Link>
          </p>
          <p className="form-footer">
            Don't have an account? <Link to="/register">Register here</Link>
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

export default Login