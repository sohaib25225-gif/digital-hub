import { useState, useEffect } from 'react';
import { coursesAPI } from '../api/courses';
import { Course } from '../types/course';
import CourseCard from '../components/courses/CourseCard';
import Loader from '../components/common/Loader';

export default function Courses() {
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchCourses = async () => {
      try {
        const data = await coursesAPI.getPublishedCourses();
        setCourses(data.courses);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to load courses');
      } finally {
        setLoading(false);
      }
    };

    fetchCourses();
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
      <h1 style={{ marginBottom: '2rem' }}>Courses</h1>

      {courses.length === 0 ? (
        <p style={{ color: '#6b7280', fontSize: '1.125rem' }}>
          No courses available yet. Check back soon!
        </p>
      ) : (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
          gap: '1.5rem'
        }}>
          {courses.map(course => (
            <CourseCard key={course.id} course={course} />
          ))}
        </div>
      )}
    </div>
  );
}
