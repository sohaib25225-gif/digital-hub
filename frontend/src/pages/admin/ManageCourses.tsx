import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { coursesAPI } from '../../api/courses';
import { CourseWithSections } from '../../types/course';
import Loader from '../../components/common/Loader';
import Button from '../../components/common/Button';

export default function ManageCourses() {
  const [courses, setCourses] = useState<CourseWithSections[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchCourses();
  }, []);

  const fetchCourses = async () => {
    try {
      // Note: This endpoint returns only published courses
      // For a full admin view, we'd need a separate admin endpoint
      const data = await coursesAPI.getPublishedCourses();
      setCourses(data.courses as CourseWithSections[]);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load courses');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm('Are you sure you want to delete this course?')) return;

    try {
      await coursesAPI.deleteCourse(id);
      setCourses(courses.filter(c => c.id !== id));
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to delete course');
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
          <h1 style={{ margin: 0 }}>Manage Courses</h1>
        </div>
        <Link to="/admin/courses/create">
          <Button>+ Create Course</Button>
        </Link>
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

      {courses.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '4rem 0' }}>
          <p style={{ color: '#6b7280', fontSize: '1.125rem', marginBottom: '1.5rem' }}>
            No courses yet. Create your first course!
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
              {courses.map(course => (
                <tr key={course.id} style={{ borderBottom: '1px solid #e5e7eb' }}>
                  <td style={{ padding: '1rem' }}>
                    <div style={{ fontWeight: '500' }}>{course.title}</div>
                    <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>{course.slug}</div>
                  </td>
                  <td style={{ padding: '1rem', textAlign: 'center' }}>
                    {course.price === 0 ? 'Free' : `$${course.price.toFixed(2)}`}
                  </td>
                  <td style={{ padding: '1rem', textAlign: 'center' }}>
                    <span style={{
                      padding: '0.25rem 0.75rem',
                      backgroundColor: course.status === 'published' ? '#d1fae5' : '#fef3c7',
                      color: course.status === 'published' ? '#065f46' : '#92400e',
                      borderRadius: '4px',
                      fontSize: '0.75rem',
                      fontWeight: '600',
                      textTransform: 'capitalize'
                    }}>
                      {course.status}
                    </span>
                  </td>
                  <td style={{ padding: '1rem', textAlign: 'right' }}>
                    <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'flex-end' }}>
                      <Link to={`/admin/courses/${course.id}/edit`}>
                        <Button variant="secondary">Edit</Button>
                      </Link>
                      <Button variant="danger" onClick={() => handleDelete(course.id)}>
                        Delete
                      </Button>
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
