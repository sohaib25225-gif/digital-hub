import { Link } from 'react-router-dom'

function Products() {
  return (
    <div style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
      <h1>Products</h1>
      <p style={{ marginTop: '1rem', color: '#666' }}>
        Product listing will be implemented in Phase 1B.
      </p>
      <Link to="/" style={{
        display: 'inline-block',
        marginTop: '2rem',
        color: '#007bff',
        textDecoration: 'none'
      }}>
        ← Back to Home
      </Link>
    </div>
  )
}

export default Products
