// services/api.ts
const API_BASE_URL = 'http://localhost:8000/api/v1';

export const api = {
  // ============================================
  // 🔐 AUTENTICAÇÃO
  // ============================================
  auth: {
    login: async (email: string, password: string) => {
      const response = await fetch(`${API_BASE_URL}/usuarios/auth/login/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || JSON.stringify(data));
      }

      return data;
    },

    register: async (userData: any) => {
      const response = await fetch(`${API_BASE_URL}/usuarios/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData)
      });

      const data = await response.json();

      if (!response.ok) {
        // Formata os erros do Django pra mostrar pro usuário
        const errors = Object.entries(data)
          .map(([field, msgs]) => `${field}: ${Array.isArray(msgs) ? msgs.join(', ') : msgs}`)
          .join('\n');
        throw new Error(errors);
      }

      return data;
    },

    logout: () => {
      if (typeof window !== 'undefined') {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user_data');
      }
    },

    getStoredToken: () => {
      if (typeof window !== 'undefined') {
        return localStorage.getItem('access_token');
      }
      return null;
    },

    getStoredUser: () => {
      if (typeof window !== 'undefined') {
        const userData = localStorage.getItem('user_data');
        if (userData && userData !== 'undefined') {
          try {
            return JSON.parse(userData);
          } catch {
            return null;
          }
        }
      }
      return null;
    },

    saveAuth: (token: string, refreshToken: string, user: any) => {
      if (typeof window !== 'undefined') {
        localStorage.setItem('access_token', token);
        localStorage.setItem('refresh_token', refreshToken);
        if (user) {
          localStorage.setItem('user_data', JSON.stringify(user));
        }
      }
    }
  },

  // ============================================
  // 📦 PRODUTOS
  // ============================================
  produtos: {
    getAll: async (params = '') => {
      const response = await fetch(`${API_BASE_URL}/produtos/${params}`);
      return response.json();
    },

    getById: async (id: number) => {
      const response = await fetch(`${API_BASE_URL}/produtos/${id}/`);
      return response.json();
    },

    getDestaques: async () => {
      const response = await fetch(`${API_BASE_URL}/produtos/destaques/`);
      return response.json();
    },

    getPromocoes: async () => {
      const response = await fetch(`${API_BASE_URL}/produtos/promocoes/`);
      return response.json();
    }
  },

  // ============================================
  // 🏷️ CATEGORIAS
  // ============================================
  categorias: {
    getAll: async () => {
      const response = await fetch(`${API_BASE_URL}/produtos/categorias/`);
      return response.json();
    },

    getById: async (id: number) => {
      const response = await fetch(`${API_BASE_URL}/produtos/categorias/${id}/`);
      return response.json();
    }
  },

  // ============================================
  // 🛒 CARRINHO
  // ============================================
  carrinho: {
    get: async (token: string) => {
      const response = await fetch(`${API_BASE_URL}/carrinho/`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      return response.json();
    },

    adicionar: async (token: string, produto_id: number, quantidade = 1) => {
      const response = await fetch(`${API_BASE_URL}/carrinho/adicionar/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ produto_id, quantidade })
      });
      return response.json();
    },

    atualizar: async (token: string, itemId: number, quantidade: number) => {
      const response = await fetch(`${API_BASE_URL}/carrinho/${itemId}/atualizar/`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ quantidade })
      });
      return response.json();
    },

    remover: async (token: string, itemId: number) => {
      const response = await fetch(`${API_BASE_URL}/carrinho/${itemId}/remover/`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      return response.ok;
    },

    limpar: async (token: string) => {
      const response = await fetch(`${API_BASE_URL}/carrinho/limpar/`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      return response.ok;
    }
  }
};