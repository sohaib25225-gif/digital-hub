import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';

export default function Navbar() {
  const { isAuthenticated, isAdmin, user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav style={{
      backgroundColor: '#fff',
      borderBottom: '1px solid #e5e7eb',
      padding: '1rem 0',
      position: 'sticky',
      top: 0,
      zIndex: 1000,
      boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
    }}>
      <div style={{
        maxWidth: '1200px',
        margin: '0 auto',
        padding: '0 1rem',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '2rem' }}>
          <Link to="/" style={{
            fontSize: '1.5rem',
            fontWeight: 'bold',
            color: '#111',
            textDecoration: 'none'
          }}>
            Digital Hub
          </Link>

          <div style={{ display: 'flex', gap: '1.5rem' }}>
            <Link to="/courses" style={linkStyle}>Courses</Link>
            <Link to="/products" style={linkStyle}>Products</Link>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          {isAuthenticated ? (
            <>
              <Link to="/dashboard" style={linkStyle}>Dashboard</Link>
              {isAdmin && (
                <Link to="/admin" style={linkStyle}>Admin</Link>
              )}
              <div style={{
                padding: '0.5rem 1rem',
                backgroundColor: '#f3f4f6',
                borderRadius: '4px'
              }}>
                {user?.full_name}
              </div>
              <button onClick={handleLogout} style={buttonStyle}>
                Logout
              </button>
            </>
          ) : (
            <>
              <Link to="/login" style={linkStyle}>Login</Link>
              <Link to="/register" style={{
                ...linkStyle,
                backgroundColor: '#007bff',
                color: 'white',
                padding: '0.5rem 1rem',
                borderRadius: '4px'
              }}>
                Register
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}

const linkStyle: React.CSSProperties = {
  color: '#4b5563',
  textDecoration: 'none',
  fontSize: '1rem',
  fontWeight: '500'
};

const buttonStyle: React.CSSProperties = {
  padding: '0.5rem 1rem',
  backgroundColor: '#dc2626',
  color: 'white',
  border: 'none',
  borderRadius: '4px',
  cursor: 'pointer',
  fontSize: '0.875rem',
  fontWeight: '500'
};
