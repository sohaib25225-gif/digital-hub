import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger';
  loading?: boolean;
}

export default function Button({
  variant = 'primary',
  loading = false,
  disabled,
  children,
  style,
  ...props
}: ButtonProps) {
  const getVariantStyles = (): React.CSSProperties => {
    const base: React.CSSProperties = {
      padding: '0.75rem 1.5rem',
      border: 'none',
      borderRadius: '4px',
      fontSize: '1rem',
      fontWeight: '500',
      cursor: disabled || loading ? 'not-allowed' : 'pointer',
      opacity: disabled || loading ? 0.6 : 1,
      transition: 'all 0.2s'
    };

    const variants = {
      primary: { backgroundColor: '#007bff', color: 'white' },
      secondary: { backgroundColor: '#6c757d', color: 'white' },
      danger: { backgroundColor: '#dc2626', color: 'white' }
    };

    return { ...base, ...variants[variant] };
  };

  return (
    <button
      disabled={disabled || loading}
      style={{ ...getVariantStyles(), ...style }}
      {...props}
    >
      {loading ? 'Loading...' : children}
    </button>
  );
}
