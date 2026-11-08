import React, { useState } from 'react';

interface ButtonProps {
  label: string;
  onClick: () => void;
  variant?: 'primary' | 'secondary';
  disabled?: boolean;
  count: number;
}

export function Button({ label, onClick, variant = 'primary', disabled = false, count }: ButtonProps) {
  const [pressed, setPressed] = useState(false);
  return (
    <button
      className={`btn btn-${variant}`}
      disabled={disabled}
      aria-pressed={pressed}
      onClick={() => {
        setPressed(!pressed);
        onClick();
      }}
    >
      {label} ({count})
    </button>
  );
}
