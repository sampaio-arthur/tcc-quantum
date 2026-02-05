const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL as string) || 'http://localhost:8000';

export interface User {
  id: number;
  email: string;
  created_at: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface Conversation {
  id: number;
  title: string;
  created_at: string;
}

export interface Message {
  id: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  created_at: string;
}

export interface ConversationDetail extends Conversation {
  messages: Message[];
}

export interface SearchResult {
  doc_id: string;
  text: string;
  score: number;
}

export interface SearchResponse {
  query: string;
  results: SearchResult[];
}

class ApiClient {
  private getToken(): string | null {
    return localStorage.getItem('access_token');
  }

  private getHeaders(json = true): HeadersInit {
    const headers: HeadersInit = {};
    const token = this.getToken();
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    if (json) {
      headers['Content-Type'] = 'application/json';
    }
    
    return headers;
  }

  async register(email: string, password: string): Promise<User> {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Erro ao registrar');
    }

    return response.json();
  }

  async login(email: string, password: string): Promise<LoginResponse> {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Credenciais inválidas');
    }

    const data = await response.json();
    localStorage.setItem('access_token', data.access_token);
    return data;
  }

  async getMe(): Promise<User> {
    const response = await fetch(`${API_BASE_URL}/auth/me`, {
      headers: this.getHeaders(),
    });

    if (!response.ok) {
      throw new Error('Não autenticado');
    }

    return response.json();
  }

  logout(): void {
    localStorage.removeItem('access_token');
  }

  async getConversations(): Promise<Conversation[]> {
    const response = await fetch(`${API_BASE_URL}/conversations`, {
      headers: this.getHeaders(),
    });

    if (!response.ok) {
      throw new Error('Erro ao carregar conversas');
    }

    return response.json();
  }

  async createConversation(title: string): Promise<Conversation> {
    const response = await fetch(`${API_BASE_URL}/conversations`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ title }),
    });

    if (!response.ok) {
      throw new Error('Erro ao criar conversa');
    }

    return response.json();
  }

  async getConversation(id: number): Promise<ConversationDetail> {
    const response = await fetch(`${API_BASE_URL}/conversations/${id}`, {
      headers: this.getHeaders(),
    });

    if (!response.ok) {
      throw new Error('Conversa não encontrada');
    }

    return response.json();
  }

  async addMessage(conversationId: number, role: 'user' | 'assistant' | 'system', content: string): Promise<Message> {
    const response = await fetch(`${API_BASE_URL}/conversations/${conversationId}/messages`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ role, content }),
    });

    if (!response.ok) {
      throw new Error('Erro ao enviar mensagem');
    }

    return response.json();
  }

  async searchWithFile(query: string, file: File): Promise<SearchResponse> {
    const formData = new FormData();
    formData.append('query', query);
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/search/file`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${this.getToken()}`,
      },
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Erro na busca');
    }

    return response.json();
  }

  async search(query: string, documents: string[]): Promise<SearchResponse> {
    const response = await fetch(`${API_BASE_URL}/search`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ query, documents }),
    });

    if (!response.ok) {
      throw new Error('Erro na busca');
    }

    return response.json();
  }
}

export const api = new ApiClient();
