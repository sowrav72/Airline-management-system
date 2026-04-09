import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../App'

function Navbar() {
  const { user, logout, isAuthenticated } = useAuth()

  return (
    <nav className="navbar">
      <div className="container">
        <div className="nav-brand">✈️ SkyLink Airlines</div>
        <div className="nav-links">
          <Link to="/">Home</Link>
          <Link to="/flights">Search Flights</Link>
          {!isAuthenticated() && (
            <>
              <Link to="/login">Login</Link>
              <Link to="/register">Register</Link>
            </>
          )}
          {isAuthenticated() && (
            <>
              <Link to="/dashboard">Dashboard</Link>
              {user?.role !== 'passenger' && (
                <>
                  <Link to="/admin/aircraft">Aircraft</Link>
                  <Link to="/admin/flights">Flights</Link>
                </>
              )}
              <Link to="/profile">Profile</Link>
              <a href="#" onClick={(e) => { e.preventDefault(); logout(); }}>Logout</a>
            </>
          )}
        </div>
      </div>
    </nav>
  )
}

function Footer() {
  return (
    <footer>
      <div className="container">
        <p>&copy; 2024 SkyLink Airlines. All rights reserved.</p>
        <p style={{ marginTop: '0.5rem', fontSize: '0.9rem' }}>Built with ❤️ using FastAPI & PostgreSQL</p>
      </div>
    </footer>
  )
}

function Home() {
  const { user, isAuthenticated } = useAuth()
  const navigate = useNavigate()

  const features = [
    { icon: '🔐', title: 'Secure Authentication', desc: 'JWT-based authentication with bcrypt password hashing ensures maximum security for all user accounts' },
    { icon: '✈️', title: 'Flight Management', desc: 'Comprehensive flight scheduling, aircraft management, and route planning for efficient operations' },
    { icon: '🔍', title: 'Flight Search', desc: 'Advanced search with filters for date, origin, destination, and seat class with real-time availability' },
    { icon: '👥', title: 'Role Management', desc: 'Role-based access control supporting Passenger, Staff, and Admin with different permissions' },
    { icon: '📊', title: 'Activity Tracking', desc: 'Complete audit trail of all user activities with timestamps and detailed information logging' },
    { icon: '🛫', title: 'Aircraft Fleet', desc: 'Manage your entire aircraft fleet with detailed specifications, maintenance tracking, and seat configurations' }
  ]

  return (
    <>
      <Navbar />
      
      <div className="hero">
        <div className="container">
          <h1>Welcome to SkyLink Airlines</h1>
          <p>Complete Flight Management System</p>
          <p className="subtitle">Module 2.1 & 2.2 - Fully Operational</p>
          <div className="hero-buttons">
            {isAuthenticated() ? (
              <>
                <Link to="/dashboard" className="btn btn-primary">Go to Dashboard</Link>
                <Link to="/flights" className="btn btn-secondary">Search Flights</Link>
              </>
            ) : (
              <>
                <Link to="/register" className="btn btn-primary">Get Started</Link>
                <Link to="/login" className="btn btn-secondary">Login</Link>
              </>
            )}
          </div>
        </div>
      </div>

      <div className="container">
        <div className="features">
          {features.map((feature, index) => (
            <div className="feature-card" key={index}>
              <div className="feature-icon">{feature.icon}</div>
              <h3>{feature.title}</h3>
              <p>{feature.desc}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="info-section">
        <div className="container">
          <h2>About This System</h2>
          <p>
            SkyLink Airlines Management System is a comprehensive full-stack web application built for modern airline operations.
            It demonstrates professional software engineering practices with FastAPI backend, PostgreSQL database, 
            and responsive frontend design with aviation-themed interface.
          </p>

          <div className="tech-stack">
            <div className="tech-item">
              <strong>Backend</strong>
              FastAPI + Python
            </div>
            <div className="tech-item">
              <strong>Database</strong>
              PostgreSQL
            </div>
            <div className="tech-item">
              <strong>Frontend</strong>
              React + Vite
            </div>
            <div className="tech-item">
              <strong>Security</strong>
              JWT + Bcrypt
            </div>
          </div>

          <div style={{ marginTop: '3rem', textAlign: 'center' }}>
            <h3 style={{ color: '#667eea', marginBottom: '1rem' }}>✅ Completed Modules</h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem', marginTop: '2rem' }}>
              <div style={{ background: 'white', padding: '1.5rem', borderRadius: '10px', boxShadow: '0 4px 15px rgba(0,0,0,0.1)' }}>
                <h4 style={{ color: '#28a745', marginBottom: '0.5rem' }}>Module 2.1: User Management ✓</h4>
                <ul style={{ textAlign: 'left', color: '#666', lineHeight: '1.8' }}>
                  <li>User Registration & Authentication</li>
                  <li>Email Verification</li>
                  <li>Password Reset</li>
                  <li>Profile Management</li>
                  <li>Role-Based Access Control</li>
                </ul>
              </div>
              <div style={{ background: 'white', padding: '1.5rem', borderRadius: '10px', boxShadow: '0 4px 15px rgba(0,0,0,0.1)' }}>
                <h4 style={{ color: '#28a745', marginBottom: '0.5rem' }}>Module 2.2: Flight Management ✓</h4>
                <ul style={{ textAlign: 'left', color: '#666', lineHeight: '1.8' }}>
                  <li>Aircraft Fleet Management</li>
                  <li>Flight Scheduling</li>
                  <li>Route Management</li>
                  <li>Flight Search & Filters</li>
                  <li>Seat Availability Tracking</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>

      <Footer />
    </>
  )
}

export default Home