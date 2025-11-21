// app/page.tsx
'use client';

import { useState, useEffect } from 'react';
import { Search, TrendingUp, Package, User, ArrowRight, Shield, Zap, Sparkles } from 'lucide-react';
import Navbar from '@/components/layout/Navbar';
import AuthModal from '@/components/auth/AuthModal';
import CarrinhoModal from '@/components/carrinho/CarrinhoModal';
import ProdutoCard from '@/components/produtos/ProdutoCard';
import { api } from '@/services/api';

export default function Home() {
  // Estados principais
  const [user, setUser] = useState(null);
  const [token, setToken] = useState<string | null>(null);
  const [produtos, setProdutos] = useState([]);
  const [categorias, setCategorias] = useState([]);
  const [carrinho, setCarrinho] = useState(null);
  const [categoriaAtiva, setCategoriaAtiva] = useState(null);
  const [loading, setLoading] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  // Estados de UI
  const [showAuth, setShowAuth] = useState(false);
  const [authMode, setAuthMode] = useState<'login' | 'register'>('login');
  const [showCart, setShowCart] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  // ============================================
  // 📡 EFFECTS
  // ============================================
  useEffect(() => {
    const storedToken = api.auth.getStoredToken();
    const storedUser = api.auth.getStoredUser();
    if (storedToken) setToken(storedToken);
    if (storedUser) setUser(storedUser);
  }, []);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 50);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  useEffect(() => {
    carregarProdutos();
    carregarCategorias();
  }, []);

  useEffect(() => {
    if (token) carregarCarrinho();
  }, [token]);

  // ============================================
  // 📦 CARREGAR DADOS
  // ============================================
  const carregarProdutos = async (categoria = null) => {
    setLoading(true);
    try {
      const params = categoria ? `?categoria=${categoria}` : '';
      const data = await api.produtos.getAll(params);
      setProdutos(Array.isArray(data) ? data : (data.results || []));
    } catch (error) {
      console.error('Erro ao carregar produtos:', error);
      setProdutos([]);
    }
    setLoading(false);
  };

  const carregarCategorias = async () => {
    try {
      const data = await api.categorias.getAll();
      setCategorias(Array.isArray(data) ? data : (data.results || []));
    } catch (error) {
      console.error('Erro ao carregar categorias:', error);
      setCategorias([]);
    }
  };

  const carregarCarrinho = async () => {
    if (!token) return;
    try {
      const data = await api.carrinho.get(token);
      setCarrinho(data);
    } catch (error) {
      console.error('Erro ao carregar carrinho:', error);
    }
  };

  // ============================================
  // 🔐 AUTH
  // ============================================
  const handleShowAuth = (mode: 'login' | 'register' = 'login') => {
    setAuthMode(mode);
    setShowAuth(true);
  };

  const handleLogin = async (email: string, password: string) => {
    const data = await api.auth.login(email, password);
    if (data.access) {
      api.auth.saveAuth(data.access, data.refresh, data.user);
      setToken(data.access);
      setUser(data.user);
      setShowAuth(false);
      await carregarCarrinho();
    }
  };

  const handleRegister = async (formData: any) => {
    await api.auth.register(formData);
  };

  const handleLogout = () => {
    api.auth.logout();
    setToken(null);
    setUser(null);
    setCarrinho(null);
  };

  // ============================================
  // 🛒 CARRINHO
  // ============================================
  const handleAdicionarCarrinho = async (produtoId: number) => {
    if (!token) {
      handleShowAuth('login');
      return;
    }
    try {
      await api.carrinho.adicionar(token, produtoId, 1);
      await carregarCarrinho();
      setShowCart(true);
    } catch (error) {
      alert('Erro ao adicionar ao carrinho');
    }
  };

  const handleAtualizarQuantidade = async (itemId: number, quantidade: number) => {
    try {
      await api.carrinho.atualizar(token!, itemId, quantidade);
      await carregarCarrinho();
    } catch (error) {
      alert('Erro ao atualizar quantidade');
    }
  };

  const handleRemoverItem = async (itemId: number) => {
    try {
      await api.carrinho.remover(token!, itemId);
      await carregarCarrinho();
    } catch (error) {
      alert('Erro ao remover item');
    }
  };

  const filtrarCategoria = (categoriaId: any) => {
    setCategoriaAtiva(categoriaId);
    carregarProdutos(categoriaId);
  };

  const produtosFiltrados = Array.isArray(produtos)
    ? produtos.filter((p: any) => p.nome && p.nome.toLowerCase().includes(searchTerm.toLowerCase()))
    : [];

  // ============================================
  // 🎨 RENDER
  // ============================================
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white">
      {/* Background animado */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute w-96 h-96 bg-purple-500/20 rounded-full blur-3xl -top-48 -left-48 animate-pulse"></div>
        <div className="absolute w-96 h-96 bg-pink-500/20 rounded-full blur-3xl top-1/2 -right-48 animate-pulse" style={{animationDelay: '1s'}}></div>
        <div className="absolute w-96 h-96 bg-blue-500/20 rounded-full blur-3xl -bottom-48 left-1/2 animate-pulse" style={{animationDelay: '0.5s'}}></div>
      </div>

      {/* Navbar */}
      <Navbar
        scrolled={scrolled}
        user={user}
        token={token}
        carrinho={carrinho}
        onShowAuth={handleShowAuth}
        onShowCart={() => setShowCart(true)}
        onLogout={handleLogout}
      />

      {/* Hero Section */}
      <div className="relative pt-32 pb-20 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div className="space-y-8">
              <div className="inline-flex items-center space-x-2 bg-purple-500/20 backdrop-blur-sm px-4 py-2 rounded-full border border-purple-500/30">
                <TrendingUp className="w-4 h-4 text-purple-400" />
                <span className="text-sm text-purple-300">Plataforma #1 em Vendas Online</span>
              </div>

              <div>
                <h1 className="text-5xl md:text-7xl font-bold leading-tight mb-6">
                  Descubra
                  <br />
                  <span className="bg-gradient-to-r from-purple-400 via-pink-400 to-orange-400 bg-clip-text text-transparent">
                    Produtos Incríveis
                  </span>
                </h1>
                <p className="text-xl text-gray-300 leading-relaxed">
                  Milhares de produtos selecionados especialmente para você.
                  <br />
                  Compre com segurança e receba em casa.
                </p>
              </div>

              <div className="flex flex-wrap gap-4">
                <a
                  href="#produtos"
                  className="group flex items-center space-x-2 bg-gradient-to-r from-purple-600 to-pink-600 px-8 py-4 rounded-xl font-semibold hover:shadow-2xl hover:shadow-purple-500/50 transition-all transform hover:scale-105"
                >
                  <span>Começar a Comprar</span>
                  <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </a>
              </div>

              <div className="flex items-center space-x-12 pt-8">
                <div>
                  <div className="flex items-center mb-2">
                    <User className="w-5 h-5 text-purple-400 mr-2" />
                    <span className="text-3xl font-bold">50K+</span>
                  </div>
                  <p className="text-gray-400">Clientes</p>
                </div>
                <div>
                  <div className="flex items-center mb-2">
                    <Package className="w-5 h-5 text-pink-400 mr-2" />
                    <span className="text-3xl font-bold">{produtos.length}+</span>
                  </div>
                  <p className="text-gray-400">Produtos</p>
                </div>
                <div>
                  <div className="flex items-center mb-2">
                    <TrendingUp className="w-5 h-5 text-orange-400 mr-2" />
                    <span className="text-3xl font-bold">98%</span>
                  </div>
                  <p className="text-gray-400">Satisfação</p>
                </div>
              </div>
            </div>

            <div className="relative">
              <div className="relative bg-gradient-to-br from-purple-500/20 to-pink-500/20 backdrop-blur-xl rounded-3xl p-8 border border-white/10 shadow-2xl">
                <div className="text-center space-y-6">
                  <div className="text-8xl">🛍️</div>
                  <div className="bg-slate-800/50 rounded-xl p-4">
                    <div className="text-green-400 font-mono text-sm">
                      const compra = await realizarPedido();
                    </div>
                    <div className="text-gray-400 text-sm mt-2">// Entrega em 24h</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Busca e Filtros */}
      <div className="py-8 px-6" id="produtos">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col md:flex-row gap-4 items-center justify-between mb-8">
            <div className="w-full md:w-96">
              <div className="relative">
                <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Buscar produtos..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full bg-white/5 border border-white/10 rounded-xl pl-12 pr-4 py-3 focus:outline-none focus:border-purple-500 transition-colors"
                />
              </div>
            </div>

            <div className="flex items-center gap-2 overflow-x-auto w-full md:w-auto">
              <button
                onClick={() => filtrarCategoria(null)}
                className={`px-4 py-2 rounded-lg whitespace-nowrap transition-all ${
                  !categoriaAtiva
                    ? 'bg-gradient-to-r from-purple-500 to-pink-500'
                    : 'bg-white/5 hover:bg-white/10'
                }`}
              >
                Todos
              </button>
              {categorias.map((cat: any) => (
                <button
                  key={cat.id}
                  onClick={() => filtrarCategoria(cat.id)}
                  className={`px-4 py-2 rounded-lg whitespace-nowrap transition-all ${
                    categoriaAtiva === cat.id
                      ? 'bg-gradient-to-r from-purple-500 to-pink-500'
                      : 'bg-white/5 hover:bg-white/10'
                  }`}
                >
                  {cat.nome}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Grid de Produtos */}
      <div className="py-12 px-6">
        <div className="max-w-7xl mx-auto">
          {loading ? (
            <div className="text-center py-20">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-500"></div>
            </div>
          ) : (
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {produtosFiltrados.map((produto: any) => (
                <ProdutoCard
                  key={produto.id}
                  produto={produto}
                  onAddToCart={handleAdicionarCarrinho}
                />
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Features */}
      <div className="py-20 px-6">
        <div className="max-w-7xl mx-auto grid md:grid-cols-3 gap-8">
          <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-8 border border-white/10">
            <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-emerald-500 rounded-xl flex items-center justify-center mb-4">
              <Shield className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-bold mb-2">Compra Segura</h3>
            <p className="text-gray-400">Proteção total em todas as transações</p>
          </div>

          <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-8 border border-white/10">
            <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-xl flex items-center justify-center mb-4">
              <Zap className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-bold mb-2">Entrega Rápida</h3>
            <p className="text-gray-400">Receba em até 24 horas na sua casa</p>
          </div>

          <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-8 border border-white/10">
            <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl flex items-center justify-center mb-4">
              <Sparkles className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-bold mb-2">Qualidade Premium</h3>
            <p className="text-gray-400">Produtos selecionados e verificados</p>
          </div>
        </div>
      </div>

      {/* Modals */}
      <AuthModal
        isOpen={showAuth}
        onClose={() => setShowAuth(false)}
        onLogin={handleLogin}
        onRegister={handleRegister}
        initialMode={authMode}
      />

      <CarrinhoModal
        isOpen={showCart}
        onClose={() => setShowCart(false)}
        carrinho={carrinho}
        token={token}
        onUpdateQuantidade={handleAtualizarQuantidade}
        onRemoverItem={handleRemoverItem}
        onShowAuth={() => handleShowAuth('login')}
      />
    </div>
  );
}