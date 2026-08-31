import { Link } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import Card from '../../components/common/Card';

export default function Dashboard() {
  const { user } = useAuth();

  return (
    <div style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
      <h1 style={{ marginBottom: '0.5rem' }}>Welcome, {user?.full_name}!</h1>
      <p style={{ color: '#6b7280', marginBottom: '3rem' }}>
        Manage your courses and purchases from your dashboard
      </p>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
        gap: '1.5rem',
        marginBottom: '3rem'
      }}>
        <Link to="/my-courses" style={{ textDecoration: 'none', color: 'inherit' }}>
          <Card onClick={() => {}}>
            <div style={{ textAlign: 'center', padding: '2rem 0' }}>
              <div style={{
                fontSize: '3rem',
                marginBottom: '1rem'
              }}>📚</div>
              <h2 style={{ margin: '0 0 0.5rem 0' }}>My Courses</h2>
              <p style={{ color: '#6b7280', margin: 0 }}>
                View your enrolled courses
              </p>
            </div>
          </Card>
        </Link>

        <Link to="/my-purchases" style={{ textDecoration: 'none', color: 'inherit' }}>
          <Card onClick={() => {}}>
            <div style={{ textAlign: 'center', padding: '2rem 0' }}>
              <div style={{
                fontSize: '3rem',
                marginBottom: '1rem'
              }}>🛒</div>
              <h2 style={{ margin: '0 0 0.5rem 0' }}>My Purchases</h2>
              <p style={{ color: '#6b7280', margin: 0 }}>
                View your purchase history
              </p>
            </div>
          </Card>
        </Link>
      </div>

      <div style={{
        backgroundColor: 'white',
        padding: '2rem',
        borderRadius: '8px',
        boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
      }}>
        <h2 style={{ marginBottom: '1rem' }}>Quick Links</h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          <Link to="/courses" style={{ color: '#007bff', textDecoration: 'none' }}>
            → Browse All Courses
          </Link>
          <Link to="/products" style={{ color: '#007bff', textDecoration: 'none' }}>
            → Browse All Products
          </Link>
        </div>
      </div>
    </div>
  );
}
