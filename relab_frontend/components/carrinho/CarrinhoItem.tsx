// components/carrinho/CarrinhoItem.tsx
'use client';

import { X, Plus, Minus } from 'lucide-react';

interface CarrinhoItemProps {
  item: {
    id: number;
    quantidade: number;
    preco_unitario: string;
    subtotal: string;
    produto_detalhes: {
      nome: string;
      imagem?: string;
    };
  };
  onUpdateQuantidade: (itemId: number, quantidade: number) => void;
  onRemover: (itemId: number) => void;
}

export default function CarrinhoItem({ item, onUpdateQuantidade, onRemover }: CarrinhoItemProps) {
  return (
    <div className="flex gap-4 bg-white/5 rounded-xl p-4 border border-white/10">
      <div className="w-20 h-20 bg-white/5 rounded-lg overflow-hidden flex-shrink-0">
        {item.produto_detalhes.imagem ? (
          <img
            src={`http://localhost:8000${item.produto_detalhes.imagem}`}
            alt={item.produto_detalhes.nome}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-2xl">📦</div>
        )}
      </div>

      <div className="flex-1">
        <h3 className="font-semibold mb-1">{item.produto_detalhes.nome}</h3>
        <p className="text-sm text-purple-400 mb-2">
          R$ {parseFloat(item.preco_unitario).toFixed(2)}
        </p>

        <div className="flex items-center gap-2">
          <button
            onClick={() => {
              if (item.quantidade > 1) {
                onUpdateQuantidade(item.id, item.quantidade - 1);
              }
            }}
            className="p-1 bg-white/10 rounded hover:bg-white/20 transition-all"
            disabled={item.quantidade <= 1}
          >
            <Minus className="w-4 h-4" />
          </button>
          <span className="w-8 text-center">{item.quantidade}</span>
          <button
            onClick={() => onUpdateQuantidade(item.id, item.quantidade + 1)}
            className="p-1 bg-white/10 rounded hover:bg-white/20 transition-all"
          >
            <Plus className="w-4 h-4" />
          </button>
        </div>
      </div>

      <div className="flex flex-col items-end justify-between">
        <button
          onClick={() => onRemover(item.id)}
          className="p-2 hover:bg-red-500/20 rounded-lg transition-all text-red-400"
        >
          <X className="w-5 h-5" />
        </button>
        <p className="text-xl font-bold">
          R$ {parseFloat(item.subtotal).toFixed(2)}
        </p>
      </div>
    </div>
  );
}