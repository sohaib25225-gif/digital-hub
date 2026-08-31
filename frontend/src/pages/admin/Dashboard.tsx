import { Link } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import Card from '../../components/common/Card';

export default function AdminDashboard() {
  const { user } = useAuth();

  return (
    <div style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
      <h1 style={{ marginBottom: '0.5rem' }}>Admin Dashboard</h1>
      <p style={{ color: '#6b7280', marginBottom: '3rem' }}>
        Welcome back, {user?.full_name}. Manage your platform content.
      </p>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
        gap: '1.5rem'
      }}>
        <Link to="/admin/courses" style={{ textDecoration: 'none', color: 'inherit' }}>
          <Card onClick={() => {}}>
            <div style={{ textAlign: 'center', padding: '2rem 0' }}>
              <div style={{
                fontSize: '3rem',
                marginBottom: '1rem'
              }}>📚</div>
              <h2 style={{ margin: '0 0 0.5rem 0' }}>Manage Courses</h2>
              <p style={{ color: '#6b7280', margin: 0 }}>
                Create, edit, and publish courses
              </p>
            </div>
          </Card>
        </Link>

        <Link to="/admin/products" style={{ textDecoration: 'none', color: 'inherit' }}>
          <Card onClick={() => {}}>
            <div style={{ textAlign: 'center', padding: '2rem 0' }}>
              <div style={{
                fontSize: '3rem',
                marginBottom: '1rem'
              }}>📦</div>
              <h2 style={{ margin: '0 0 0.5rem 0' }}>Manage Products</h2>
              <p style={{ color: '#6b7280', margin: 0 }}>
                Create, edit, and publish products
              </p>
            </div>
          </Card>
        </Link>
      </div>

      <div style={{
        marginTop: '3rem',
        backgroundColor: 'white',
        padding: '2rem',
        borderRadius: '8px',
        boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
      }}>
        <h2 style={{ marginBottom: '1rem' }}>Quick Actions</h2>
        <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
          <Link
            to="/admin/courses/create"
            style={{
              padding: '0.75rem 1.5rem',
              backgroundColor: '#007bff',
              color: 'white',
              textDecoration: 'none',
              borderRadius: '4px',
              fontWeight: '500'
            }}
          >
            + New Course
          </Link>
          <Link
            to="/admin/products/create"
            style={{
              padding: '0.75rem 1.5rem',
              backgroundColor: '#28a745',
              color: 'white',
              textDecoration: 'none',
              borderRadius: '4px',
              fontWeight: '500'
            }}
          >
            + New Product
          </Link>
        </div>
      </div>
    </div>
  );
}
