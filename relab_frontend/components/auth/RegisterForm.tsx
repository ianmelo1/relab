// components/auth/RegisterForm.tsx
'use client';

import { useState } from 'react';

interface RegisterFormProps {
  onSubmit: (data: any) => Promise<void>;
  onSwitchToLogin: () => void;
  loading: boolean;
}

export default function RegisterForm({ onSubmit, onSwitchToLogin, loading }: RegisterFormProps) {
  const [formData, setFormData] = useState({
    username: '',
    first_name: '',
    last_name: '',
    email: '',
    cpf: '',
    telefone: '',
    password: '',
    password_confirm: ''
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (formData.password !== formData.password_confirm) {
      alert('As senhas não coincidem!');
      return;
    }

    await onSubmit(formData);
  };

  const updateField = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <input
        type="text"
        placeholder="Username"
        value={formData.username}
        onChange={(e) => updateField('username', e.target.value)}
        className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 focus:outline-none focus:border-purple-500"
        required
      />

      <div className="grid grid-cols-2 gap-4">
        <input
          type="text"
          placeholder="Nome"
          value={formData.first_name}
          onChange={(e) => updateField('first_name', e.target.value)}
          className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 focus:outline-none focus:border-purple-500"
          required
        />
        <input
          type="text"
          placeholder="Sobrenome"
          value={formData.last_name}
          onChange={(e) => updateField('last_name', e.target.value)}
          className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 focus:outline-none focus:border-purple-500"
          required
        />
      </div>

      <input
        type="email"
        placeholder="Email"
        value={formData.email}
        onChange={(e) => updateField('email', e.target.value)}
        className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 focus:outline-none focus:border-purple-500"
        required
      />

      <input
        type="text"
        placeholder="CPF (apenas números)"
        value={formData.cpf}
        onChange={(e) => updateField('cpf', e.target.value.replace(/\D/g, ''))}
        className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 focus:outline-none focus:border-purple-500"
        required
        maxLength={11}
      />

      <input
        type="text"
        placeholder="Telefone (apenas números)"
        value={formData.telefone}
        onChange={(e) => updateField('telefone', e.target.value.replace(/\D/g, ''))}
        className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 focus:outline-none focus:border-purple-500"
        required
        maxLength={11}
      />

      <input
        type="password"
        placeholder="Senha"
        value={formData.password}
        onChange={(e) => updateField('password', e.target.value)}
        className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 focus:outline-none focus:border-purple-500"
        required
      />

      <input
        type="password"
        placeholder="Confirmar senha"
        value={formData.password_confirm}
        onChange={(e) => updateField('password_confirm', e.target.value)}
        className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 focus:outline-none focus:border-purple-500"
        required
      />

      <button
        type="submit"
        disabled={loading}
        className="w-full bg-gradient-to-r from-purple-500 to-pink-500 py-3 rounded-xl font-semibold hover:shadow-lg transition-all disabled:opacity-50"
      >
        {loading ? 'Carregando...' : 'Cadastrar'}
      </button>

      <p className="text-center text-gray-400 mt-4">
        Já tem conta?{' '}
        <button
          type="button"
          onClick={onSwitchToLogin}
          className="text-purple-400 hover:text-purple-300 font-semibold"
        >
          Faça login
        </button>
      </p>
    </form>
  );
}