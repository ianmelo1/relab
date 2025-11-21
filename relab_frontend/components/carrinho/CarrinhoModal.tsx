// components/carrinho/CarrinhoModal.tsx
'use client';

import { X, Plus, Minus, ShoppingCart } from 'lucide-react';

interface CarrinhoModalProps {
  isOpen: boolean;
  onClose: () => void;
  carrinho: any;
  token: string | null;
  onUpdateQuantidade: (itemId: number, quantidade: number) => void;
  onRemoverItem: (itemId: number) => void;
  onShowAuth: () => void;
}

export default function CarrinhoModal({
  isOpen,
  onClose,
  carrinho,
  token,
  onUpdateQuantidade,
  onRemoverItem,
  onShowAuth
}: CarrinhoModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-end md:items-center justify-center">
      <div className="bg-slate-900 rounded-t-3xl md:rounded-2xl p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto border border-white/10 relative">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-2 hover:bg-white/10 rounded-lg transition-all"
        >
          <X className="w-5 h-5" />
        </button>

        <h2 className="text-3xl font-bold mb-6">Carrinho</h2>

        {!token ? (
          <div className="text-center py-12">
            <ShoppingCart className="w-16 h-16 mx-auto mb-4 text-gray-500" />
            <p className="text-gray-400 mb-4">Faça login para ver seu carrinho</p>
            <button
              onClick={() => {
                onClose();
                onShowAuth();
              }}
              className="bg-gradient-to-r from-purple-500 to-pink-500 px-6 py-3 rounded-xl font-semibold"
            >
              Fazer Login
            </button>
          </div>
        ) : !carrinho || carrinho.total_itens === 0 ? (
          <div className="text-center py-12">
            <ShoppingCart className="w-16 h-16 mx-auto mb-4 text-gray-500" />
            <p className="text-gray-400">Seu carrinho está vazio</p>
          </div>
        ) : (
          <div className="space-y-6">
            {carrinho.itens.map((item: any) => (
              <div key={item.id} className="flex gap-4 bg-white/5 rounded-xl p-4 border border-white/10">
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
                    onClick={() => onRemoverItem(item.id)}
                    className="p-2 hover:bg-red-500/20 rounded-lg transition-all text-red-400"
                  >
                    <X className="w-5 h-5" />
                  </button>
                  <p className="text-xl font-bold">
                    R$ {parseFloat(item.subtotal).toFixed(2)}
                  </p>
                </div>
              </div>
            ))}

            <div className="border-t border-white/10 pt-6">
              <div className="flex justify-between items-center mb-2">
                <span className="text-gray-400">Subtotal</span>
                <span className="text-xl">R$ {parseFloat(carrinho.subtotal).toFixed(2)}</span>
              </div>
              <div className="flex justify-between items-center mb-6">
                <span className="text-2xl font-bold">Total</span>
                <span className="text-3xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                  R$ {parseFloat(carrinho.total).toFixed(2)}
                </span>
              </div>

              <button className="w-full bg-gradient-to-r from-purple-500 to-pink-500 py-4 rounded-xl font-semibold hover:shadow-lg hover:shadow-purple-500/50 transition-all">
                Finalizar Compra
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}