import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { coursesAPI } from '../api/courses';
import { enrollmentsAPI } from '../api/enrollments';
import { useAuth } from '../hooks/useAuth';
import { CourseWithSections } from '../types/course';
import Loader from '../components/common/Loader';
import Button from '../components/common/Button';

export default function CourseDetail() {
  const { slug } = useParams<{ slug: string }>();
  const { isAuthenticated } = useAuth();

  const [course, setCourse] = useState<CourseWithSections | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [enrolling, setEnrolling] = useState(false);
  const [enrollmentStatus, setEnrollmentStatus] = useState<'not_enrolled' | 'enrolled' | 'requires_purchase'>('not_enrolled');

  useEffect(() => {
    const fetchCourse = async () => {
      if (!slug) return;

      try {
        const data = await coursesAPI.getCourseBySlug(slug);
        setCourse(data);

        // Check enrollment status if authenticated
        if (isAuthenticated) {
          try {
            const enrollments = await enrollmentsAPI.getMyEnrollments();
            const isEnrolled = enrollments.some(e => e.course_id === data.id);

            if (isEnrolled) {
              setEnrollmentStatus('enrolled');
            } else if (data.price > 0) {
              setEnrollmentStatus('requires_purchase');
            } else {
              setEnrollmentStatus('not_enrolled');
            }
          } catch (err) {
            // Enrollment check failed, but course loaded
            console.error('Failed to check enrollment:', err);
          }
        }
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to load course');
      } finally {
        setLoading(false);
      }
    };

    fetchCourse();
  }, [slug, isAuthenticated]);

  const handleEnroll = async () => {
    if (!course || !isAuthenticated) return;

    setEnrolling(true);
    setError('');

    try {
      await enrollmentsAPI.enrollInCourse({ course_id: course.id });
      setEnrollmentStatus('enrolled');
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Enrollment failed';
      if (err.response?.status === 402) {
        setEnrollmentStatus('requires_purchase');
      }
      setError(errorMsg);
    } finally {
      setEnrolling(false);
    }
  };

  if (loading) return <Loader fullPage />;

  if (error && !course) {
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
        <Link to="/courses" style={{ display: 'inline-block', marginTop: '1rem', color: '#007bff' }}>
          ← Back to Courses
        </Link>
      </div>
    );
  }

  if (!course) return null;

  return (
    <div style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
      <Link to="/courses" style={{ display: 'inline-block', marginBottom: '1rem', color: '#007bff' }}>
        ← Back to Courses
      </Link>

      {course.thumbnail_url && (
        <img
          src={course.thumbnail_url}
          alt={course.title}
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
          <h1 style={{ margin: '0 0 0.5rem 0' }}>{course.title}</h1>
          {course.price === 0 ? (
            <span style={{
              padding: '0.25rem 0.75rem',
              backgroundColor: '#10b981',
              color: 'white',
              borderRadius: '4px',
              fontSize: '0.875rem',
              fontWeight: '600'
            }}>
              Free Course
            </span>
          ) : (
            <span style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>
              ${course.price.toFixed(2)}
            </span>
          )}
        </div>

        <div>
          {!isAuthenticated ? (
            <Link to="/login">
              <Button>Login to Enroll</Button>
            </Link>
          ) : enrollmentStatus === 'enrolled' ? (
            <Button variant="secondary" disabled>Enrolled</Button>
          ) : enrollmentStatus === 'requires_purchase' ? (
            <div style={{ textAlign: 'right' }}>
              <p style={{ marginBottom: '0.5rem', color: '#6b7280' }}>
                Purchase required to enroll
              </p>
              <Link to={`/products`}>
                <Button>Purchase Course</Button>
              </Link>
            </div>
          ) : (
            <Button onClick={handleEnroll} loading={enrolling}>
              Enroll Now
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

      <div style={{ marginBottom: '3rem' }}>
        <h2 style={{ marginBottom: '1rem' }}>About This Course</h2>
        <p style={{ color: '#4b5563', lineHeight: '1.6' }}>{course.description}</p>
      </div>

      {course.sections && course.sections.length > 0 && (
        <div>
          <h2 style={{ marginBottom: '1rem' }}>Course Curriculum</h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {course.sections.map((section, index) => (
              <div key={section.id} style={{
                backgroundColor: 'white',
                padding: '1.5rem',
                borderRadius: '8px',
                boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
              }}>
                <h3 style={{ margin: '0 0 1rem 0' }}>
                  Section {index + 1}: {section.title}
                </h3>
                {section.lessons && section.lessons.length > 0 && (
                  <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                    {section.lessons.map((lesson) => (
                      <li key={lesson.id} style={{
                        padding: '0.75rem',
                        borderBottom: '1px solid #e5e7eb',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem'
                      }}>
                        <span style={{
                          width: '20px',
                          height: '20px',
                          borderRadius: '50%',
                          backgroundColor: lesson.is_preview ? '#10b981' : '#e5e7eb',
                          display: 'inline-block'
                        }}></span>
                        <span>{lesson.title}</span>
                        {lesson.is_preview && (
                          <span style={{
                            marginLeft: 'auto',
                            padding: '0.25rem 0.5rem',
                            backgroundColor: '#dbeafe',
                            color: '#1e40af',
                            borderRadius: '4px',
                            fontSize: '0.75rem'
                          }}>
                            Preview
                          </span>
                        )}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
