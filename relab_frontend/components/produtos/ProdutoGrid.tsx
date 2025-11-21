// components/produtos/ProdutoGrid.tsx
'use client';

import ProdutoCard from './ProdutoCard';

interface ProdutoGridProps {
  produtos: any[];
  loading: boolean;
  onAddToCart: (produtoId: number) => void;
}

export default function ProdutoGrid({ produtos, loading, onAddToCart }: ProdutoGridProps) {
  if (loading) {
    return (
      <div className="text-center py-20">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-500"></div>
        <p className="text-gray-400 mt-4">Carregando produtos...</p>
      </div>
    );
  }

  if (produtos.length === 0) {
    return (
      <div className="text-center py-20">
        <p className="text-2xl text-gray-400">😔 Nenhum produto encontrado</p>
        <p className="text-gray-500 mt-2">Tente buscar por outro termo ou categoria</p>
      </div>
    );
  }

  return (
    <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      {produtos.map((produto) => (
        <ProdutoCard
          key={produto.id}
          produto={produto}
          onAddToCart={onAddToCart}
        />
      ))}
    </div>
  );
}