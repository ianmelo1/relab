// components/ui/Loading.tsx
'use client';

interface LoadingProps {
  size?: 'sm' | 'md' | 'lg';
  text?: string;
}

export default function Loading({ size = 'md', text }: LoadingProps) {
  const sizeClasses = {
    sm: 'h-6 w-6',
    md: 'h-12 w-12',
    lg: 'h-16 w-16'
  };

  return (
    <div className="text-center py-20">
      <div className={`inline-block animate-spin rounded-full border-t-2 border-b-2 border-purple-500 ${sizeClasses[size]}`}></div>
      {text && <p className="text-gray-400 mt-4">{text}</p>}
    </div>
  );
}