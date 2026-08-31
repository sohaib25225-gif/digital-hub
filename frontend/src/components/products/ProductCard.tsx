import { Link } from 'react-router-dom';
import Card from '../common/Card';
import { Product } from '../../types/product';

interface ProductCardProps {
  product: Product;
}

export default function ProductCard({ product }: ProductCardProps) {
  return (
    <Link to={`/products/${product.slug}`} style={{ textDecoration: 'none', color: 'inherit' }}>
      <Card>
        {product.thumbnail_url && (
          <img
            src={product.thumbnail_url}
            alt={product.title}
            style={{
              width: '100%',
              height: '200px',
              objectFit: 'cover',
              borderRadius: '4px',
              marginBottom: '1rem'
            }}
          />
        )}

        <h3 style={{ margin: '0 0 0.5rem 0', fontSize: '1.25rem', fontWeight: '600' }}>
          {product.title}
        </h3>

        <p style={{
          margin: '0 0 1rem 0',
          color: '#6b7280',
          fontSize: '0.875rem',
          display: '-webkit-box',
          WebkitLineClamp: 2,
          WebkitBoxOrient: 'vertical',
          overflow: 'hidden'
        }}>
          {product.description}
        </p>

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ fontSize: '1.25rem', fontWeight: 'bold', color: '#111' }}>
            ${product.price.toFixed(2)}
          </span>
        </div>
      </Card>
    </Link>
  );
}
