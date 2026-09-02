/**
 * Payment Success Page (Phase 6 Stage 7)
 *
 * IMPORTANT: Does NOT trust URL parameters for payment status.
 * Always queries backend for actual purchase status.
 */

import { useEffect, useState } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { purchasesAPI } from '../api/purchases';
import { PurchaseWithDetails } from '../types/purchase';
import Loader from '../components/common/Loader';
import Button from '../components/common/Button';

export default function PaymentSuccess() {
  const [searchParams] = useSearchParams();

  const [loading, setLoading] = useState(true);
  const [purchase, setPurchase] = useState<PurchaseWithDetails | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    const purchaseId = searchParams.get('purchase_id');

    if (!purchaseId) {
      setError('No purchase ID provided');
      setLoading(false);
      return;
    }

    loadPurchase(purchaseId);
  }, [searchParams]);

  const loadPurchase = async (purchaseId: string) => {
    try {
      const data = await purchasesAPI.getPurchase(purchaseId);
      setPurchase(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load purchase details');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    const purchaseId = searchParams.get('purchase_id');
    if (purchaseId) {
      setLoading(true);
      setError('');
      loadPurchase(purchaseId);
    }
  };

  if (loading) {
    return <Loader fullPage />;
  }

  if (error) {
    return (
      <div style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto', textAlign: 'center' }}>
        <h1 style={{ color: '#c00', marginBottom: '1rem' }}>Error</h1>
        <p style={{ color: '#666', marginBottom: '2rem' }}>{error}</p>
        <Link to="/products">
          <Button>Browse Products</Button>
        </Link>
      </div>
    );
  }

  if (!purchase) {
    return (
      <div style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto', textAlign: 'center' }}>
        <h1 style={{ marginBottom: '1rem' }}>Purchase Not Found</h1>
        <Link to="/products">
          <Button>Browse Products</Button>
        </Link>
      </div>
    );
  }

  // Check actual status from database (NOT query params)
  if (purchase.status === 'completed') {
    return (
      <div style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto', textAlign: 'center' }}>
        <div style={{
          fontSize: '4rem',
          marginBottom: '1rem',
        }}>
          ✅
        </div>
        <h1 style={{ color: '#10b981', marginBottom: '1rem' }}>Payment Successful!</h1>
        <p style={{ color: '#666', marginBottom: '0.5rem', fontSize: '1.125rem' }}>
          Your purchase is complete.
        </p>
        <p style={{ color: '#999', marginBottom: '2rem' }}>
          Purchase ID: {purchase.id}
        </p>

        {purchase.item_type === 'course' && purchase.course_id && (
          <div style={{ marginBottom: '2rem' }}>
            <p style={{ marginBottom: '1rem' }}>You can now access the course:</p>
            <p style={{ fontWeight: 'bold', marginBottom: '1rem' }}>{purchase.item_title}</p>
            <Link to={`/courses/${purchase.course_id}`}>
              <Button>Go to Course</Button>
            </Link>
          </div>
        )}

        {purchase.item_type === 'product' && purchase.product_id && (
          <div style={{ marginBottom: '2rem' }}>
            <p style={{ marginBottom: '1rem' }}>Your product is ready:</p>
            <p style={{ fontWeight: 'bold', marginBottom: '1rem' }}>{purchase.item_title}</p>
            <Link to={`/products/${purchase.product_id}`}>
              <Button>View Product</Button>
            </Link>
          </div>
        )}

        <div style={{ marginTop: '2rem' }}>
          <Link to="/products" style={{ color: '#007bff', textDecoration: 'none' }}>
            ← Browse More Products
          </Link>
        </div>
      </div>
    );
  }

  if (purchase.status === 'failed') {
    return (
      <div style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto', textAlign: 'center' }}>
        <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>❌</div>
        <h1 style={{ color: '#c00', marginBottom: '1rem' }}>Payment Failed</h1>
        <p style={{ color: '#666', marginBottom: '2rem' }}>
          Your payment could not be completed. Please try again.
        </p>
        <Link to="/products">
          <Button>Try Again</Button>
        </Link>
      </div>
    );
  }

  // Status is 'pending' - waiting for webhook confirmation
  return (
    <div style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto', textAlign: 'center' }}>
      <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>⏳</div>
      <h1 style={{ color: '#f59e0b', marginBottom: '1rem' }}>Payment Processing</h1>
      <p style={{ color: '#666', marginBottom: '1rem' }}>
        Your payment is being confirmed. This usually takes a few seconds.
      </p>
      <p style={{ color: '#999', fontSize: '0.875rem', marginBottom: '2rem' }}>
        Purchase ID: {purchase.id}
      </p>

      <div style={{ marginBottom: '2rem' }}>
        <Button onClick={handleRefresh}>
          Check Status
        </Button>
      </div>

      <p style={{ color: '#999', fontSize: '0.875rem' }}>
        The page will not automatically refresh. Click "Check Status" to see if your payment has been confirmed.
      </p>
    </div>
  );
}
