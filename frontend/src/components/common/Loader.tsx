import React from 'react';

interface LoaderProps {
  fullPage?: boolean;
  size?: 'small' | 'medium' | 'large';
}

export default function Loader({ fullPage = false, size = 'medium' }: LoaderProps) {
  const sizes = {
    small: '24px',
    medium: '40px',
    large: '60px'
  };

  const spinnerStyle: React.CSSProperties = {
    border: `4px solid #f3f4f6`,
    borderTop: `4px solid #007bff`,
    borderRadius: '50%',
    width: sizes[size],
    height: sizes[size],
    animation: 'spin 1s linear infinite'
  };

  const containerStyle: React.CSSProperties = fullPage ? {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    minHeight: '100vh'
  } : {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    padding: '2rem'
  };

  return (
    <>
      <style>
        {`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}
      </style>
      <div style={containerStyle}>
        <div style={spinnerStyle}></div>
      </div>
    </>
  );
}
