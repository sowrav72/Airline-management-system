import { useState } from 'react'
import { Link, useSearchParams, useNavigate } from 'react-router-dom'
import { authAPI } from '../services/api'

function ResetPassword() {
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const res = await authAPI.resetPassword(token, password)
      setMessage(res.data.message)
      setTimeout(() => navigate('/login'), 2000)
    } catch (err) {
      setMessage(err.response?.data?.detail || 'Error resetting password')
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
          <h2>🔐 New Password</h2>
          {message && <div className="error-message" style={{ background: message.includes('success') ? '#d4edda' : '#fee', color: message.includes('success') ? '#155724' : '#721c24' }}>{message}</div>}
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>New Password</label>
              <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required placeholder="Minimum 6 characters" />
            </div>
            <button type="submit" className="btn btn-primary" disabled={loading || !token}>
              {loading ? 'Resetting...' : 'Reset Password'}
            </button>
          </form>
          <p className="form-footer">
            <Link to="/login">Back to Login</Link>
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

export default ResetPassword