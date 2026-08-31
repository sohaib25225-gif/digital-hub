import { useState, useEffect, FormEvent } from 'react';
import { useNavigate, useParams, Link } from 'react-router-dom';
import { coursesAPI } from '../../api/courses';
import Button from '../../components/common/Button';
import Loader from '../../components/common/Loader';

export default function EditCourse() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const [formData, setFormData] = useState({
    title: '',
    description: '',
    price: 0,
    status: 'draft' as 'draft' | 'published',
    thumbnail_url: ''
  });

  useEffect(() => {
    const fetchCourse = async () => {
      if (!id) return;
      try {
        const course = await coursesAPI.getCourseById(id);
        setFormData({
          title: course.title,
          description: course.description,
          price: course.price,
          status: course.status,
          thumbnail_url: course.thumbnail_url || ''
        });
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to load course');
      } finally {
        setLoading(false);
      }
    };

    fetchCourse();
  }, [id]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!id) return;

    setSubmitting(true);
    setError('');

    try {
      await coursesAPI.updateCourse(id, formData);
      navigate('/admin/courses');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update course');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <Loader fullPage />;

  return (
    <div style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto' }}>
      <Link to="/admin/courses" style={{ color: '#007bff', textDecoration: 'none', display: 'block', marginBottom: '1rem' }}>
        ← Back to Courses
      </Link>

      <h1 style={{ marginBottom: '2rem' }}>Edit Course</h1>

      <form onSubmit={handleSubmit} style={{ backgroundColor: 'white', padding: '2rem', borderRadius: '8px', boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)' }}>
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

        <div style={{ marginBottom: '1.5rem' }}>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>Title *</label>
          <input
            type="text"
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            required
            style={{ width: '100%', padding: '0.75rem', border: '1px solid #d1d5db', borderRadius: '4px', fontSize: '1rem' }}
          />
        </div>

        <div style={{ marginBottom: '1.5rem' }}>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>Description *</label>
          <textarea
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            required
            rows={5}
            style={{ width: '100%', padding: '0.75rem', border: '1px solid #d1d5db', borderRadius: '4px', fontSize: '1rem', fontFamily: 'inherit' }}
          />
        </div>

        <div style={{ marginBottom: '1.5rem' }}>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>Price (USD) *</label>
          <input
            type="number"
            value={formData.price}
            onChange={(e) => setFormData({ ...formData, price: parseFloat(e.target.value) })}
            required
            min="0"
            step="0.01"
            style={{ width: '100%', padding: '0.75rem', border: '1px solid #d1d5db', borderRadius: '4px', fontSize: '1rem' }}
          />
        </div>

        <div style={{ marginBottom: '1.5rem' }}>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>Status *</label>
          <select
            value={formData.status}
            onChange={(e) => setFormData({ ...formData, status: e.target.value as 'draft' | 'published' })}
            style={{ width: '100%', padding: '0.75rem', border: '1px solid #d1d5db', borderRadius: '4px', fontSize: '1rem' }}
          >
            <option value="draft">Draft</option>
            <option value="published">Published</option>
          </select>
        </div>

        <div style={{ display: 'flex', gap: '1rem' }}>
          <Button type="submit" loading={submitting} style={{ flex: 1 }}>Update Course</Button>
          <Button type="button" variant="secondary" onClick={() => navigate('/admin/courses')} style={{ flex: 1 }}>Cancel</Button>
        </div>
      </form>
    </div>
  );
}
