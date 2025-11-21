// components/auth/AuthModal.tsx
'use client';

import { useState } from 'react';
import { X, AlertCircle } from 'lucide-react';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  onLogin: (email: string, password: string) => Promise<void>;
  onRegister: (data: any) => Promise<void>;
  initialMode?: 'login' | 'register';
}

export default function AuthModal({
  isOpen,
  onClose,
  onLogin,
  onRegister,
  initialMode = 'login'
}: AuthModalProps) {
  const [authMode, setAuthMode] = useState<'login' | 'register'>(initialMode);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    username: '',
    first_name: '',
    last_name: '',
    cpf: '',
    telefone: '',
    password_confirm: ''
  });

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      if (authMode === 'login') {
        await onLogin(formData.email, formData.password);
      } else {
        if (formData.password !== formData.password_confirm) {
          setError('As senhas não coincidem!');
          setLoading(false);
          return;
        }
        await onRegister(formData);
        alert('Cadastro realizado! Faça login.');
        setAuthMode('login');
        // Limpa os campos de senha
        setFormData(prev => ({ ...prev, password: '', password_confirm: '' }));
      }
    } catch (err: any) {
      setError(err.message || `Erro ao ${authMode === 'login' ? 'fazer login' : 'cadastrar'}`);
    }

    setLoading(false);
  };

  const updateField = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    setError(null); // Limpa erro ao digitar
  };

  const switchMode = (mode: 'login' | 'register') => {
    setAuthMode(mode);
    setError(null);
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-slate-900 rounded-2xl p-8 max-w-md w-full border border-white/10 relative max-h-[90vh] overflow-y-auto">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-2 hover:bg-white/10 rounded-lg transition-all"
        >
          <X className="w-5 h-5" />
        </button>

        <h2 className="text-3xl font-bold mb-6">
          {authMode === 'login' ? 'Entrar' : 'Cadastrar'}
        </h2>

        {/* Mensagem de erro */}
        {error && (
          <div className="mb-4 p-4 bg-red-500/20 border border-red-500/50 rounded-xl flex items-start space-x-3">
            <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
            <p className="text-red-300 text-sm whitespace-pre-line">{error}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {authMode === 'register' && (
            <>
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
            </>
          )}

          <input
            type="email"
            placeholder="Email"
            value={formData.email}
            onChange={(e) => updateField('email', e.target.value)}
            className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 focus:outline-none focus:border-purple-500"
            required
          />

          <input
            type="password"
            placeholder="Senha"
            value={formData.password}
            onChange={(e) => updateField('password', e.target.value)}
            className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 focus:outline-none focus:border-purple-500"
            required
          />

          {authMode === 'register' && (
            <input
              type="password"
              placeholder="Confirmar senha"
              value={formData.password_confirm}
              onChange={(e) => updateField('password_confirm', e.target.value)}
              className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 focus:outline-none focus:border-purple-500"
              required
            />
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-gradient-to-r from-purple-500 to-pink-500 py-3 rounded-xl font-semibold hover:shadow-lg transition-all disabled:opacity-50"
          >
            {loading ? 'Carregando...' : authMode === 'login' ? 'Entrar' : 'Cadastrar'}
          </button>
        </form>

        <p className="text-center text-gray-400 mt-4">
          {authMode === 'login' ? 'Não tem conta?' : 'Já tem conta?'}
          {' '}
          <button
            onClick={() => switchMode(authMode === 'login' ? 'register' : 'login')}
            className="text-purple-400 hover:text-purple-300 font-semibold"
          >
            {authMode === 'login' ? 'Cadastre-se' : 'Faça login'}
          </button>
        </p>
      </div>
    </div>
  );
}