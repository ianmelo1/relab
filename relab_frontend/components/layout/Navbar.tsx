// components/layout/Navbar.tsx
'use client';

import { ShoppingBag, Heart, ShoppingCart, User, LogOut, UserPlus } from 'lucide-react';

interface NavbarProps {
  scrolled: boolean;
  user: any;
  token: string | null;
  carrinho: any;
  onShowAuth: (mode?: 'login' | 'register') => void;
  onShowCart: () => void;
  onLogout: () => void;
}

export default function Navbar({
  scrolled,
  user,
  token,
  carrinho,
  onShowAuth,
  onShowCart,
  onLogout
}: NavbarProps) {
  return (
    <nav className={`fixed top-0 w-full z-50 transition-all duration-300 ${
      scrolled ? 'bg-slate-900/80 backdrop-blur-lg shadow-lg' : 'bg-transparent'
    }`}>
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center space-x-2">
            <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl flex items-center justify-center shadow-lg">
              <ShoppingBag className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                Relab
              </h1>
              <p className="text-xs text-gray-400">Shop. Save. Smile.</p>
            </div>
          </div>

          {/* Menu Desktop */}
          <div className="hidden md:flex items-center space-x-8">
            <a href="#" className="hover:text-purple-400 transition-colors">Home</a>
            <a href="#produtos" className="hover:text-purple-400 transition-colors">Produtos</a>
            <a href="#" className="hover:text-purple-400 transition-colors">Ofertas</a>
          </div>

          {/* Actions */}
          <div className="flex items-center space-x-4">
            <button className="hidden md:block p-2 hover:bg-white/10 rounded-lg transition-all">
              <Heart className="w-5 h-5" />
            </button>

            <button
              onClick={onShowCart}
              className="p-2 hover:bg-white/10 rounded-lg transition-all relative"
            >
              <ShoppingCart className="w-5 h-5" />
              {carrinho?.total_itens > 0 && (
                <span className="absolute -top-1 -right-1 w-5 h-5 bg-pink-500 rounded-full text-xs flex items-center justify-center">
                  {carrinho.total_itens}
                </span>
              )}
            </button>

            {token ? (
              <div className="flex items-center space-x-3">
                <div className="hidden lg:flex flex-col items-end">
                  <span className="text-sm font-semibold text-white">
                    Olá, {user?.nome || user?.first_name || user?.username || 'Usuário'}
                  </span>
                  <span className="text-xs text-gray-400">{user?.email}</span>
                </div>

                <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center font-bold shadow-lg">
                  {(user?.first_name || user?.nome || user?.username || 'U')[0].toUpperCase()}
                </div>

                <button
                  onClick={onLogout}
                  className="flex items-center space-x-2 bg-red-500/20 hover:bg-red-500/30 border border-red-500/30 px-4 py-2 rounded-lg transition-all"
                  title="Sair"
                >
                  <LogOut className="w-4 h-4" />
                  <span className="hidden xl:inline">Sair</span>
                </button>
              </div>
            ) : (
              <div className="flex items-center space-x-2">
                {/* Botão Cadastrar */}
                <button
                  onClick={() => onShowAuth('register')}
                  className="hidden sm:flex items-center space-x-2 border border-purple-500/50 hover:bg-purple-500/20 px-4 py-2 rounded-lg transition-all"
                >
                  <UserPlus className="w-4 h-4" />
                  <span>Cadastrar</span>
                </button>

                {/* Botão Login */}
                <button
                  onClick={() => onShowAuth('login')}
                  className="flex items-center space-x-2 bg-gradient-to-r from-purple-500 to-pink-500 px-4 py-2 rounded-lg hover:shadow-lg transition-all"
                >
                  <User className="w-4 h-4" />
                  <span>Login</span>
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}