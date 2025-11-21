// components/produtos/ProdutoCard.tsx
'use client';

import { ShoppingCart, Heart } from 'lucide-react';

interface ProdutoCardProps {
  produto: {
    id: number;
    nome: string;
    descricao_curta?: string;
    preco: string;
    preco_final: string;
    preco_promocional?: string;
    em_promocao: boolean;
    desconto_percentual?: number;
    imagem?: string;
    categoria_nome: string;
    disponivel_venda: boolean;
  };
  onAddToCart: (produtoId: number) => void;
}

export default function ProdutoCard({ produto, onAddToCart }: ProdutoCardProps) {
  return (
    <div className="group bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10 hover:border-purple-500/50 transition-all hover:shadow-2xl hover:shadow-purple-500/20 hover:scale-105">
      <div className="relative mb-4">
        <div className="aspect-square bg-white/5 rounded-xl overflow-hidden mb-4">
          {produto.imagem ? (
            <img
              src={`http://localhost:8000${produto.imagem}`}
              alt={produto.nome}
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-6xl">
              📦
            </div>
          )}
        </div>

        {produto.em_promocao && (
          <span className="absolute top-2 right-2 bg-gradient-to-r from-purple-500 to-pink-500 text-white text-xs font-bold px-3 py-1 rounded-full">
            -{produto.desconto_percentual}%
          </span>
        )}

        <button className="absolute top-2 left-2 p-2 bg-white/10 backdrop-blur-sm rounded-full opacity-0 group-hover:opacity-100 transition-opacity">
          <Heart className="w-4 h-4" />
        </button>
      </div>

      <div className="space-y-2">
        <p className="text-xs text-purple-400">{produto.categoria_nome}</p>
        <h3 className="font-semibold text-lg line-clamp-2">{produto.nome}</h3>

        {produto.descricao_curta && (
          <p className="text-sm text-gray-400 line-clamp-2">{produto.descricao_curta}</p>
        )}

        <div className="flex items-center justify-between pt-2">
          <div>
            {produto.em_promocao && (
              <span className="text-sm text-gray-400 line-through block">
                R$ {parseFloat(produto.preco).toFixed(2)}
              </span>
            )}
            <span className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
              R$ {parseFloat(produto.preco_final).toFixed(2)}
            </span>
          </div>

          <button
            onClick={() => onAddToCart(produto.id)}
            disabled={!produto.disponivel_venda}
            className={`p-3 rounded-lg transition-all ${
              produto.disponivel_venda
                ? 'bg-gradient-to-r from-purple-500 to-pink-500 hover:shadow-lg hover:shadow-purple-500/50'
                : 'bg-gray-500 cursor-not-allowed opacity-50'
            }`}
          >
            <ShoppingCart className="w-5 h-5" />
          </button>
        </div>

        {!produto.disponivel_venda && (
          <p className="text-xs text-red-400 mt-2">Indisponível</p>
        )}
      </div>
    </div>
  );
}