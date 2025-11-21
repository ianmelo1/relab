// components/ui/Input.tsx
'use client';

interface InputProps {
  type?: string;
  placeholder?: string;
  value: string;
  onChange: (value: string) => void;
  required?: boolean;
  disabled?: boolean;
  className?: string;
  maxLength?: number;
}

export default function Input({
  type = 'text',
  placeholder,
  value,
  onChange,
  required = false,
  disabled = false,
  className = '',
  maxLength
}: InputProps) {
  return (
    <input
      type={type}
      placeholder={placeholder}
      value={value}
      onChange={(e) => onChange(e.target.value)}
      required={required}
      disabled={disabled}
      maxLength={maxLength}
      className={`w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3
        focus:outline-none focus:border-purple-500 transition-colors
        disabled:opacity-50 disabled:cursor-not-allowed ${className}`}
    />
  );
}