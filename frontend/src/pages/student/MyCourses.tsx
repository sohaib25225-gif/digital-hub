import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { enrollmentsAPI } from '../../api/enrollments';
import { EnrollmentWithCourse } from '../../types/enrollment';
import Card from '../../components/common/Card';
import Loader from '../../components/common/Loader';

export default function MyCourses() {
  const [enrollments, setEnrollments] = useState<EnrollmentWithCourse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchEnrollments = async () => {
      try {
        const data = await enrollmentsAPI.getMyEnrollments();
        setEnrollments(data);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to load enrollments');
      } finally {
        setLoading(false);
      }
    };

    fetchEnrollments();
  }, []);

  if (loading) return <Loader fullPage />;

  return (
    <div style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ marginBottom: '2rem' }}>
        <Link to="/dashboard" style={{ color: '#007bff', textDecoration: 'none' }}>
          ← Back to Dashboard
        </Link>
      </div>

      <h1 style={{ marginBottom: '2rem' }}>My Courses</h1>

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

      {enrollments.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '4rem 0' }}>
          <p style={{ color: '#6b7280', fontSize: '1.125rem', marginBottom: '1.5rem' }}>
            You haven't enrolled in any courses yet
          </p>
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
        </div>
      ) : (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
          gap: '1.5rem'
        }}>
          {enrollments.map(enrollment => (
            <Link
              key={enrollment.id}
              to={`/courses/${enrollment.course_slug}`}
              style={{ textDecoration: 'none', color: 'inherit' }}
            >
              <Card>
                {enrollment.course_thumbnail && (
                  <img
                    src={enrollment.course_thumbnail}
                    alt={enrollment.course_title}
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
                  {enrollment.course_title}
                </h3>

                <div style={{
                  marginTop: '1rem',
                  padding: '0.5rem',
                  backgroundColor: '#f3f4f6',
                  borderRadius: '4px'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
                    <span style={{ fontSize: '0.875rem', color: '#6b7280' }}>Progress</span>
                    <span style={{ fontSize: '0.875rem', fontWeight: '600' }}>
                      {enrollment.progress_percent}%
                    </span>
                  </div>
                  <div style={{
                    height: '8px',
                    backgroundColor: '#e5e7eb',
                    borderRadius: '4px',
                    overflow: 'hidden'
                  }}>
                    <div style={{
                      height: '100%',
                      width: `${enrollment.progress_percent}%`,
                      backgroundColor: '#007bff',
                      transition: 'width 0.3s'
                    }}></div>
                  </div>
                </div>

                <p style={{
                  marginTop: '0.75rem',
                  fontSize: '0.75rem',
                  color: '#9ca3af'
                }}>
                  Enrolled {new Date(enrollment.enrolled_at).toLocaleDateString()}
                </p>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
