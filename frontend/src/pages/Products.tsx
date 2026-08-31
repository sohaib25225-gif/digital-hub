import { useState, useEffect } from 'react';
import { productsAPI } from '../api/products';
import { Product } from '../types/product';
import ProductCard from '../components/products/ProductCard';
import Loader from '../components/common/Loader';

export default function Products() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const data = await productsAPI.getPublishedProducts();
        setProducts(data.products);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to load products');
      } finally {
        setLoading(false);
      }
    };

    fetchProducts();
  }, []);

  if (loading) return <Loader fullPage />;

  if (error) {
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
      </div>
    );
  }

  return (
    <div style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
      <h1 style={{ marginBottom: '2rem' }}>Products</h1>

      {products.length === 0 ? (
        <p style={{ color: '#6b7280', fontSize: '1.125rem' }}>
          No products available yet. Check back soon!
        </p>
      ) : (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
          gap: '1.5rem'
        }}>
          {products.map(product => (
            <ProductCard key={product.id} product={product} />
          ))}
        </div>
      )}
    </div>
  );
}
