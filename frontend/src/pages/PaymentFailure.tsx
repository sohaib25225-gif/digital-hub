/**
 * Payment Failure Page (Phase 6 Stage 7)
 */

import { Link, useSearchParams } from 'react-router-dom';
import Button from '../components/common/Button';

export default function PaymentFailure() {
  const [searchParams] = useSearchParams();
  const reason = searchParams.get('reason') || 'Unknown error';
  const purchaseId = searchParams.get('purchase_id');

  return (
    <div style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto', textAlign: 'center' }}>
      <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>❌</div>

      <h1 style={{ color: '#c00', marginBottom: '1rem' }}>Payment Failed</h1>

      <p style={{ color: '#666', marginBottom: '1rem' }}>
        Your payment could not be processed.
      </p>

      {reason && (
        <p style={{
          color: '#999',
          fontSize: '0.875rem',
          padding: '0.75rem',
          backgroundColor: '#fee',
          borderRadius: '4px',
          marginBottom: '2rem',
          maxWidth: '500px',
          margin: '0 auto 2rem auto'
        }}>
          Reason: {reason}
        </p>
      )}

      {purchaseId && (
        <p style={{ color: '#999', fontSize: '0.875rem', marginBottom: '2rem' }}>
          Purchase ID: {purchaseId}
        </p>
      )}

      <p style={{ color: '#666', marginBottom: '2rem' }}>
        Please try again or contact support if the problem persists.
      </p>

      <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', marginBottom: '2rem' }}>
        <Link to="/products">
          <Button>Try Again</Button>
        </Link>
        <Link to="/my-purchases">
          <Button variant="secondary">View Purchase History</Button>
        </Link>
      </div>

      <p style={{ color: '#999', fontSize: '0.875rem' }}>
        Need help? Contact support with the purchase ID above.
      </p>
    </div>
  );
}
