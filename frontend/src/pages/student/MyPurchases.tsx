import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { purchasesAPI } from '../../api/purchases';
import { PurchaseWithDetails } from '../../types/purchase';
import Loader from '../../components/common/Loader';

export default function MyPurchases() {
  const [purchases, setPurchases] = useState<PurchaseWithDetails[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchPurchases = async () => {
      try {
        const data = await purchasesAPI.getMyPurchases();
        setPurchases(data);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to load purchases');
      } finally {
        setLoading(false);
      }
    };

    fetchPurchases();
  }, []);

  if (loading) return <Loader fullPage />;

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return { bg: '#d1fae5', text: '#065f46', border: '#a7f3d0' };
      case 'pending':
        return { bg: '#fef3c7', text: '#92400e', border: '#fde68a' };
      case 'failed':
        return { bg: '#fee', text: '#c00', border: '#fcc' };
      default:
        return { bg: '#f3f4f6', text: '#6b7280', border: '#e5e7eb' };
    }
  };

  return (
    <div style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ marginBottom: '2rem' }}>
        <Link to="/dashboard" style={{ color: '#007bff', textDecoration: 'none' }}>
          ← Back to Dashboard
        </Link>
      </div>

      <h1 style={{ marginBottom: '2rem' }}>My Purchases</h1>

      {error && (
        <div style={{
          padding: '1rem',
          backgroundColor: '#fee',
          color: '#c00',
          borderRadius: '4px',
          marginBottom: '1rem',
          border: '1px solid #fcc'
        }}>
          {error}
        </div>
      )}

      {purchases.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '4rem 0' }}>
          <p style={{ color: '#6b7280', fontSize: '1.125rem', marginBottom: '1.5rem' }}>
            You haven't made any purchases yet
          </p>
          <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
            <Link
              to="/courses"
              style={{
                display: 'inline-block',
                padding: '0.75rem 1.5rem',
                backgroundColor: '#007bff',
                color: 'white',
                textDecoration: 'none',
                borderRadius: '4px',
                fontWeight: '500'
              }}
            >
              Browse Courses
            </Link>
            <Link
              to="/products"
              style={{
                display: 'inline-block',
                padding: '0.75rem 1.5rem',
                backgroundColor: '#28a745',
                color: 'white',
                textDecoration: 'none',
                borderRadius: '4px',
                fontWeight: '500'
              }}
            >
              Browse Products
            </Link>
          </div>
        </div>
      ) : (
        <div style={{
          backgroundColor: 'white',
          borderRadius: '8px',
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
          overflow: 'hidden'
        }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead style={{ backgroundColor: '#f9fafb', borderBottom: '1px solid #e5e7eb' }}>
              <tr>
                <th style={{ padding: '1rem', textAlign: 'left', fontWeight: '600' }}>Item</th>
                <th style={{ padding: '1rem', textAlign: 'left', fontWeight: '600' }}>Type</th>
                <th style={{ padding: '1rem', textAlign: 'right', fontWeight: '600' }}>Amount</th>
                <th style={{ padding: '1rem', textAlign: 'center', fontWeight: '600' }}>Status</th>
                <th style={{ padding: '1rem', textAlign: 'left', fontWeight: '600' }}>Date</th>
              </tr>
            </thead>
            <tbody>
              {purchases.map(purchase => {
                const statusColor = getStatusColor(purchase.status);
                return (
                  <tr key={purchase.id} style={{ borderBottom: '1px solid #e5e7eb' }}>
                    <td style={{ padding: '1rem' }}>
                      <div style={{ fontWeight: '500' }}>{purchase.item_title}</div>
                    </td>
                    <td style={{ padding: '1rem' }}>
                      <span style={{
                        padding: '0.25rem 0.5rem',
                        backgroundColor: '#e0e7ff',
                        color: '#3730a3',
                        borderRadius: '4px',
                        fontSize: '0.75rem',
                        textTransform: 'capitalize'
                      }}>
                        {purchase.item_type}
                      </span>
                    </td>
                    <td style={{ padding: '1rem', textAlign: 'right', fontWeight: '600' }}>
                      {purchase.currency} ${purchase.amount.toFixed(2)}
                    </td>
                    <td style={{ padding: '1rem', textAlign: 'center' }}>
                      <span style={{
                        padding: '0.25rem 0.75rem',
                        backgroundColor: statusColor.bg,
                        color: statusColor.text,
                        border: `1px solid ${statusColor.border}`,
                        borderRadius: '4px',
                        fontSize: '0.75rem',
                        fontWeight: '600',
                        textTransform: 'capitalize'
                      }}>
                        {purchase.status}
                      </span>
                    </td>
                    <td style={{ padding: '1rem', fontSize: '0.875rem', color: '#6b7280' }}>
                      {new Date(purchase.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {purchases.some(p => p.status === 'pending') && (
        <div style={{
          marginTop: '2rem',
          padding: '1rem',
          backgroundColor: '#fffbeb',
          borderRadius: '4px',
          border: '1px solid #fde68a'
        }}>
          <p style={{ margin: 0, color: '#92400e' }}>
            <strong>Note:</strong> Purchases with "pending" status are awaiting admin approval.
            You'll receive access once approved.
          </p>
        </div>
      )}
    </div>
  );
}
