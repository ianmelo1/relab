// components/produtos/CategoriaFilter.tsx
'use client';

interface CategoriaFilterProps {
  categorias: any[];
  categoriaAtiva: number | null;
  onSelectCategoria: (categoriaId: number | null) => void;
}

export default function CategoriaFilter({
  categorias,
  categoriaAtiva,
  onSelectCategoria
}: CategoriaFilterProps) {
  return (
    <div className="flex items-center gap-2 overflow-x-auto w-full md:w-auto pb-2">
      <button
        onClick={() => onSelectCategoria(null)}
        className={`px-4 py-2 rounded-lg whitespace-nowrap transition-all ${
          !categoriaAtiva
            ? 'bg-gradient-to-r from-purple-500 to-pink-500 shadow-lg'
            : 'bg-white/5 hover:bg-white/10'
        }`}
      >
        Todos
      </button>

      {categorias.map((cat) => (
        <button
          key={cat.id}
          onClick={() => onSelectCategoria(cat.id)}
          className={`px-4 py-2 rounded-lg whitespace-nowrap transition-all ${
            categoriaAtiva === cat.id
              ? 'bg-gradient-to-r from-purple-500 to-pink-500 shadow-lg'
              : 'bg-white/5 hover:bg-white/10'
          }`}
        >
          {cat.nome}
        </button>
      ))}
    </div>
  );
}