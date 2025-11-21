// types/index.ts

export interface Usuario {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  cpf: string;
  telefone: string;
}

export interface Categoria {
  id: number;
  nome: string;
  slug: string;
  descricao?: string;
  imagem?: string;
  ativo: boolean;
  ordem: number;
}

export interface Produto {
  id: number;
  nome: string;
  slug: string;
  descricao: string;
  descricao_curta?: string;
  preco: string;
  preco_promocional?: string;
  preco_final: string;
  em_promocao: boolean;
  desconto_percentual?: number;
  estoque: number;
  disponivel: boolean;
  disponivel_venda: boolean;
  imagem?: string;
  categoria: number;
  categoria_nome: string;
  em_destaque: boolean;
  visualizacoes: number;
  vendas: number;
  criado_em: string;
  atualizado_em: string;
}

export interface ItemCarrinho {
  id: number;
  produto: number;
  produto_detalhes: {
    nome: string;
    imagem?: string;
  };
  quantidade: number;
  preco_unitario: string;
  subtotal: string;
}

export interface Carrinho {
  id: number;
  usuario: number;
  itens: ItemCarrinho[];
  total_itens: number;
  subtotal: string;
  total: string;
  criado_em: string;
  atualizado_em: string;
}

export interface LoginResponse {
  access: string;
  refresh: string;
  user: Usuario;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  cpf: string;
  telefone: string;
}