// components/home/HeroSection.tsx
'use client';

import { TrendingUp, Package, User, ArrowRight } from 'lucide-react';

interface HeroSectionProps {
  totalProdutos: number;
}

export default function HeroSection({ totalProdutos }: HeroSectionProps) {
  return (
    <div className="relative pt-32 pb-20 px-6">
      <div className="max-w-7xl mx-auto">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          {/* Texto */}
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

            {/* Stats */}
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
                  <span className="text-3xl font-bold">{totalProdutos}+</span>
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

          {/* Imagem/Card */}
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
  );
}