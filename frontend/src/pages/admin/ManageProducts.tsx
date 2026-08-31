import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { productsAPI } from '../../api/products';
import { Product } from '../../types/product';
import Loader from '../../components/common/Loader';
import Button from '../../components/common/Button';

export default function ManageProducts() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchProducts();
  }, []);

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

  const handleDelete = async (id: string) => {
    if (!window.confirm('Are you sure you want to delete this product?')) return;

    try {
      await productsAPI.deleteProduct(id);
      setProducts(products.filter(p => p.id !== id));
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to delete product');
    }
  };

  if (loading) return <Loader fullPage />;

  return (
    <div style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <Link to="/admin" style={{ color: '#007bff', textDecoration: 'none', display: 'block', marginBottom: '0.5rem' }}>
            ← Back to Admin
          </Link>
          <h1 style={{ margin: 0 }}>Manage Products</h1>
        </div>
        <Link to="/admin/products/create">
          <Button>+ Create Product</Button>
        </Link>
      </div>

      {error && (
        <div style={{ padding: '1rem', backgroundColor: '#fee', color: '#c00', borderRadius: '4px', marginBottom: '1rem', border: '1px solid #fcc' }}>
          {error}
        </div>
      )}

      {products.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '4rem 0' }}>
          <p style={{ color: '#6b7280', fontSize: '1.125rem', marginBottom: '1.5rem' }}>
            No products yet. Create your first product!
          </p>
        </div>
      ) : (
        <div style={{ backgroundColor: 'white', borderRadius: '8px', boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)', overflow: 'hidden' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead style={{ backgroundColor: '#f9fafb', borderBottom: '1px solid #e5e7eb' }}>
              <tr>
                <th style={{ padding: '1rem', textAlign: 'left', fontWeight: '600' }}>Title</th>
                <th style={{ padding: '1rem', textAlign: 'center', fontWeight: '600' }}>Price</th>
                <th style={{ padding: '1rem', textAlign: 'center', fontWeight: '600' }}>Status</th>
                <th style={{ padding: '1rem', textAlign: 'right', fontWeight: '600' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {products.map(product => (
                <tr key={product.id} style={{ borderBottom: '1px solid #e5e7eb' }}>
                  <td style={{ padding: '1rem' }}>
                    <div style={{ fontWeight: '500' }}>{product.title}</div>
                    <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>{product.slug}</div>
                  </td>
                  <td style={{ padding: '1rem', textAlign: 'center' }}>${product.price.toFixed(2)}</td>
                  <td style={{ padding: '1rem', textAlign: 'center' }}>
                    <span style={{
                      padding: '0.25rem 0.75rem',
                      backgroundColor: product.status === 'published' ? '#d1fae5' : '#fef3c7',
                      color: product.status === 'published' ? '#065f46' : '#92400e',
                      borderRadius: '4px',
                      fontSize: '0.75rem',
                      fontWeight: '600',
                      textTransform: 'capitalize'
                    }}>
                      {product.status}
                    </span>
                  </td>
                  <td style={{ padding: '1rem', textAlign: 'right' }}>
                    <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'flex-end' }}>
                      <Link to={`/admin/products/${product.id}/edit`}>
                        <Button variant="secondary">Edit</Button>
                      </Link>
                      <Button variant="danger" onClick={() => handleDelete(product.id)}>Delete</Button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
