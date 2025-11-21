// components/auth/LoginForm.tsx
'use client';

import { useState } from 'react';

interface LoginFormProps {
  onSubmit: (email: string, password: string) => Promise<void>;
  onSwitchToRegister: () => void;
  loading: boolean;
}

export default function LoginForm({ onSubmit, onSwitchToRegister, loading }: LoginFormProps) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onSubmit(email, password);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <input
        type="email"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 focus:outline-none focus:border-purple-500 transition-colors"
        required
      />

      <input
        type="password"
        placeholder="Senha"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 focus:outline-none focus:border-purple-500 transition-colors"
        required
      />

      <button
        type="submit"
        disabled={loading}
        className="w-full bg-gradient-to-r from-purple-500 to-pink-500 py-3 rounded-xl font-semibold hover:shadow-lg transition-all disabled:opacity-50"
      >
        {loading ? 'Carregando...' : 'Entrar'}
      </button>

      <p className="text-center text-gray-400 mt-4">
        Não tem conta?{' '}
        <button
          type="button"
          onClick={onSwitchToRegister}
          className="text-purple-400 hover:text-purple-300 font-semibold"
        >
          Cadastre-se
        </button>
      </p>
    </form>
  );
}