import { Link } from 'react-router-dom'

function Home() {
  return (
    <div style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
      <h1>Welcome to Digital Hub</h1>
      <p style={{ marginTop: '1rem', color: '#666' }}>
        Personal Digital Products & Courses Platform
      </p>

      <nav style={{ marginTop: '2rem', display: 'flex', gap: '1rem' }}>
        <Link to="/courses" style={{
          padding: '0.75rem 1.5rem',
          backgroundColor: '#007bff',
          color: 'white',
          textDecoration: 'none',
          borderRadius: '4px'
        }}>
          Browse Courses
        </Link>
        <Link to="/products" style={{
          padding: '0.75rem 1.5rem',
          backgroundColor: '#28a745',
          color: 'white',
          textDecoration: 'none',
          borderRadius: '4px'
        }}>
          Browse Products
        </Link>
      </nav>

      <div style={{ marginTop: '3rem', padding: '1.5rem', backgroundColor: 'white', borderRadius: '8px' }}>
        <h2>Phase 1A Setup Complete</h2>
        <p style={{ marginTop: '1rem', color: '#666' }}>
          The project foundation is ready. Authentication, course management, and product features will be implemented in Phase 1B.
        </p>
      </div>
    </div>
  )
}

export default Home
