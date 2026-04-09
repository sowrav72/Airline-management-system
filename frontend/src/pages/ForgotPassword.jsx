import { useState } from 'react'
import { Link } from 'react-router-dom'
import { authAPI } from '../services/api'

function ForgotPassword() {
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const res = await authAPI.forgotPassword(email)
      setMessage(res.data.message)
    } catch (err) {
      setMessage(err.response?.data?.detail || 'Error sending reset email')
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
          <h2>🔐 Reset Password</h2>
          {message && <div className="error-message" style={{ background: message.includes('email') ? '#d4edda' : '#fee', color: message.includes('email') ? '#155724' : '#721c24' }}>{message}</div>}
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Email Address</label>
              <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required placeholder="your.email@example.com" />
            </div>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Sending...' : 'Send Reset Link'}
            </button>
          </form>
          <p className="form-footer">
            Remember your password? <Link to="/login">Login here</Link>
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

export default ForgotPassword