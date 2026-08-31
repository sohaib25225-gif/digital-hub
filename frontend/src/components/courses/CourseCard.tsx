import { Link } from 'react-router-dom';
import Card from '../common/Card';
import { Course } from '../../types/course';

interface CourseCardProps {
  course: Course;
}

export default function CourseCard({ course }: CourseCardProps) {
  return (
    <Link to={`/courses/${course.slug}`} style={{ textDecoration: 'none', color: 'inherit' }}>
      <Card>
        {course.thumbnail_url && (
          <img
            src={course.thumbnail_url}
            alt={course.title}
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
          {course.title}
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
          {course.description}
        </p>

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          {course.price === 0 ? (
            <span style={{
              padding: '0.25rem 0.75rem',
              backgroundColor: '#10b981',
              color: 'white',
              borderRadius: '4px',
              fontSize: '0.875rem',
              fontWeight: '600'
            }}>
              Free
            </span>
          ) : (
            <span style={{ fontSize: '1.25rem', fontWeight: 'bold', color: '#111' }}>
              ${course.price.toFixed(2)}
            </span>
          )}
        </div>
      </Card>
    </Link>
  );
}
