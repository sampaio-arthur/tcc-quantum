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

export interface SearchMetrics {
  recall_at_k?: number | null;
  mrr?: number | null;
  ndcg_at_k?: number | null;
  latency_ms: number;
  k: number;
  candidate_k: number;
  has_labels: boolean;
}

export interface SearchResponseLite {
  results: SearchResult[];
  answer?: string;
  metrics?: SearchMetrics;
}

export interface SearchComparison {
  classical: SearchResponseLite;
  quantum: SearchResponseLite;
}

export interface SearchResponse {
  query: string;
  mode: string;
  results: SearchResult[];
  answer?: string;
  metrics?: SearchMetrics;
  comparison?: SearchComparison;
}

export interface DatasetSummary {
  dataset_id: string;
  name: string;
  description: string;
  document_count: number;
  query_count: number;
}

export interface DatasetQuery {
  query_id: string;
  query: string;
  relevant_count: number;
}

export interface DatasetDetail {
  dataset_id: string;
  name: string;
  description: string;
  queries: DatasetQuery[];
}

export interface SearchOptions {
  mode?: string;
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

  async getDatasets(): Promise<DatasetSummary[]> {
    const response = await fetch(`${API_BASE_URL}/datasets`, {
      headers: this.getHeaders(),
    });

    if (!response.ok) {
      throw new Error('Erro ao carregar datasets');
    }

    return response.json();
  }

  async getDataset(datasetId: string): Promise<DatasetDetail> {
    const response = await fetch(`${API_BASE_URL}/datasets/${datasetId}`, {
      headers: this.getHeaders(),
    });

    if (!response.ok) {
      throw new Error('Dataset não encontrado');
    }

    return response.json();
  }

  async searchDataset(
    datasetId: string,
    queryId: string,
    options: SearchOptions = {}
  ): Promise<SearchResponse> {
    const response = await fetch(`${API_BASE_URL}/search/dataset`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({
        dataset_id: datasetId,
        query_id: queryId,
        mode: options.mode ?? 'compare',
      }),
    });

    if (!response.ok) {
      throw new Error('Erro na busca do dataset');
    }

    return response.json();
  }

  async searchWithFile(query: string, file: File, options: SearchOptions = {}): Promise<SearchResponse> {
    const formData = new FormData();
    formData.append('query', query);
    formData.append('file', file);
    formData.append('mode', options.mode ?? 'classical');

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

  async search(query: string, documents: string[], options: SearchOptions = {}): Promise<SearchResponse> {
    const response = await fetch(`${API_BASE_URL}/search`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({
        query,
        documents,
        mode: options.mode ?? 'classical',
      }),
    });

    if (!response.ok) {
      throw new Error('Erro na busca');
    }

    return response.json();
  }
}

export const api = new ApiClient();
