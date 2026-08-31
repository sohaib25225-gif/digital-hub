import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { productsAPI } from '../api/products';
import { purchasesAPI } from '../api/purchases';
import { useAuth } from '../hooks/useAuth';
import { Product } from '../types/product';
import Loader from '../components/common/Loader';
import Button from '../components/common/Button';

export default function ProductDetail() {
  const { slug } = useParams<{ slug: string }>();
  const { isAuthenticated } = useAuth();

  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [purchasing, setPurchasing] = useState(false);
  const [purchaseStatus, setPurchaseStatus] = useState<'none' | 'pending' | 'completed'>('none');
  const [successMessage, setSuccessMessage] = useState('');

  useEffect(() => {
    const fetchProduct = async () => {
      if (!slug) return;

      try {
        const data = await productsAPI.getProductBySlug(slug);
        setProduct(data);

        // Check purchase status if authenticated
        if (isAuthenticated) {
          try {
            const purchases = await purchasesAPI.getMyPurchases();
            const existingPurchase = purchases.find(p => p.product_id === data.id);

            if (existingPurchase) {
              setPurchaseStatus(existingPurchase.status === 'completed' ? 'completed' : 'pending');
            }
          } catch (err) {
            console.error('Failed to check purchase status:', err);
          }
        }
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to load product');
      } finally {
        setLoading(false);
      }
    };

    fetchProduct();
  }, [slug, isAuthenticated]);

  const handlePurchase = async () => {
    if (!product || !isAuthenticated) return;

    setPurchasing(true);
    setError('');
    setSuccessMessage('');

    try {
      await purchasesAPI.createPurchase({
        product_id: product.id,
        amount: product.price,
        currency: 'USD'
      });
      setPurchaseStatus('pending');
      setSuccessMessage('Purchase created! Awaiting admin approval.');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Purchase failed. Please try again.');
    } finally {
      setPurchasing(false);
    }
  };

  if (loading) return <Loader fullPage />;

  if (error && !product) {
    return (
      <div style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
        <div style={{
          padding: '1rem',
          backgroundColor: '#fee',
          color: '#c00',
          borderRadius: '4px',
          border: '1px solid #fcc'
        }}>
          {error}
        </div>
        <Link to="/products" style={{ display: 'inline-block', marginTop: '1rem', color: '#007bff' }}>
          ← Back to Products
        </Link>
      </div>
    );
  }

  if (!product) return null;

  return (
    <div style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
      <Link to="/products" style={{ display: 'inline-block', marginBottom: '1rem', color: '#007bff' }}>
        ← Back to Products
      </Link>

      {product.thumbnail_url && (
        <img
          src={product.thumbnail_url}
          alt={product.title}
          style={{
            width: '100%',
            maxHeight: '400px',
            objectFit: 'cover',
            borderRadius: '8px',
            marginBottom: '2rem'
          }}
        />
      )}

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '2rem' }}>
        <div>
          <h1 style={{ margin: '0 0 0.5rem 0' }}>{product.title}</h1>
          <span style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>
            ${product.price.toFixed(2)}
          </span>
        </div>

        <div>
          {!isAuthenticated ? (
            <Link to="/login">
              <Button>Login to Purchase</Button>
            </Link>
          ) : purchaseStatus === 'completed' ? (
            <Button variant="secondary" disabled>Purchased</Button>
          ) : purchaseStatus === 'pending' ? (
            <div style={{ textAlign: 'right' }}>
              <Button variant="secondary" disabled>Purchase Pending</Button>
              <p style={{ marginTop: '0.5rem', color: '#6b7280', fontSize: '0.875rem' }}>
                Awaiting admin approval
              </p>
            </div>
          ) : (
            <Button onClick={handlePurchase} loading={purchasing}>
              Purchase Now
            </Button>
          )}
        </div>
      </div>

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

      {successMessage && (
        <div style={{
          padding: '1rem',
          backgroundColor: '#d1fae5',
          color: '#065f46',
          borderRadius: '4px',
          marginBottom: '1rem',
          border: '1px solid #a7f3d0'
        }}>
          {successMessage}
        </div>
      )}

      <div style={{ marginBottom: '3rem' }}>
        <h2 style={{ marginBottom: '1rem' }}>About This Product</h2>
        <p style={{ color: '#4b5563', lineHeight: '1.6' }}>{product.description}</p>
      </div>

      {purchaseStatus === 'completed' && (
        <div style={{
          padding: '1.5rem',
          backgroundColor: 'white',
          borderRadius: '8px',
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
        }}>
          <h3 style={{ marginBottom: '1rem' }}>Download</h3>
          <a
            href={product.file_url}
            target="_blank"
            rel="noopener noreferrer"
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
            Download Product File
          </a>
        </div>
      )}
    </div>
  );
}
