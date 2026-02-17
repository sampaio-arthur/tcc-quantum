const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL as string) || 'http://localhost:8000';
const REQUEST_TIMEOUT_MS = 60000;

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

export interface DatasetSummary {
  dataset_id: string;
  name: string;
  description: string;
  document_count: number;
  query_count: number;
}

export interface DatasetDetail {
  dataset_id: string;
  name: string;
  description: string;
  queries: { query_id: string; query: string; relevant_count: number }[];
  documents: { doc_id: string }[];
}

export interface BenchmarkLabelInput {
  dataset_id: string;
  query_text: string;
  ideal_answer: string;
}

export interface BenchmarkLabel {
  benchmark_id: string;
  dataset_id: string;
  query_text: string;
  ideal_answer: string;
  relevant_doc_ids: string[];
}

export interface SearchResult {
  doc_id: string;
  text: string;
  score: number;
}

export interface SearchMetrics {
  accuracy_at_k?: number | null;
  recall_at_k?: number | null;
  mrr?: number | null;
  ndcg_at_k?: number | null;
  answer_similarity?: number | null;
  has_ideal_answer: boolean;
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

  private async fetchWithTimeout(input: RequestInfo | URL, init: RequestInit = {}, timeoutMs = REQUEST_TIMEOUT_MS): Promise<Response> {
    const controller = new AbortController();
    const timeoutId = window.setTimeout(() => controller.abort(), timeoutMs);

    try {
      return await fetch(input, { ...init, signal: controller.signal });
    } catch (error) {
      if (error instanceof DOMException && error.name === 'AbortError') {
        throw new Error('Tempo limite excedido ao aguardar resposta do servidor');
      }
      throw error;
    } finally {
      window.clearTimeout(timeoutId);
    }
  }

  private async readErrorDetail(response: Response, fallback: string): Promise<string> {
    try {
      const data = await response.json();
      if (typeof data?.detail === 'string' && data.detail.trim()) {
        return data.detail;
      }
    } catch {
      // ignore json parsing errors and fallback
    }
    return fallback;
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
      throw new Error(error.detail || 'Credenciais invalidas');
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
      throw new Error('Nao autenticado');
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

  async deleteConversation(id: number): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/conversations/${id}`, {
      method: 'DELETE',
      headers: this.getHeaders(),
    });

    if (!response.ok) {
      throw new Error('Erro ao remover conversa');
    }
  }

  async getConversation(id: number): Promise<ConversationDetail> {
    const response = await fetch(`${API_BASE_URL}/conversations/${id}`, {
      headers: this.getHeaders(),
    });

    if (!response.ok) {
      throw new Error('Conversa nao encontrada');
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
    formData.append('mode', 'compare');

    const response = await this.fetchWithTimeout(`${API_BASE_URL}/search/file`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${this.getToken()}`,
      },
      body: formData,
    });

    if (!response.ok) {
      const detail = await this.readErrorDetail(response, 'Erro na busca');
      throw new Error(detail);
    }

    return response.json();
  }

  async indexDataset(datasetId: string, forceReindex = false): Promise<void> {
    const response = await this.fetchWithTimeout(`${API_BASE_URL}/search/dataset/index`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ dataset_id: datasetId, force_reindex: forceReindex }),
    });

    if (!response.ok) {
      const detail = await this.readErrorDetail(response, 'Erro ao indexar dataset');
      throw new Error(detail);
    }
  }

  async searchDataset(query: string, datasetId: string, queryId?: string): Promise<SearchResponse> {
    const response = await this.fetchWithTimeout(`${API_BASE_URL}/search/dataset`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({
        dataset_id: datasetId,
        query,
        query_id: queryId,
        mode: 'compare',
        top_k: 5,
        candidate_k: 20,
      }),
    });

    if (!response.ok) {
      const detail = await this.readErrorDetail(response, 'Erro na busca no dataset');
      throw new Error(detail);
    }

    return response.json();
  }
  async listDatasets(): Promise<DatasetSummary[]> {
    const response = await this.fetchWithTimeout(`${API_BASE_URL}/datasets`, {
      headers: this.getHeaders(false),
    });

    if (!response.ok) {
      const detail = await this.readErrorDetail(response, 'Erro ao listar datasets');
      throw new Error(detail);
    }

    return response.json();
  }

  async getDataset(datasetId: string): Promise<DatasetDetail> {
    const response = await this.fetchWithTimeout(`${API_BASE_URL}/datasets/${datasetId}`, {
      headers: this.getHeaders(false),
    });

    if (!response.ok) {
      const detail = await this.readErrorDetail(response, 'Erro ao carregar dataset');
      throw new Error(detail);
    }

    return response.json();
  }

  async listBenchmarkLabels(datasetId: string): Promise<BenchmarkLabel[]> {
    const response = await this.fetchWithTimeout(`${API_BASE_URL}/benchmarks/labels?dataset_id=${encodeURIComponent(datasetId)}`, {
      headers: this.getHeaders(false),
    });

    if (!response.ok) {
      const detail = await this.readErrorDetail(response, 'Erro ao listar gabaritos');
      throw new Error(detail);
    }

    const payload = await response.json();
    return payload.items ?? [];
  }

  async upsertBenchmarkLabel(payload: BenchmarkLabelInput): Promise<BenchmarkLabel> {
    const response = await this.fetchWithTimeout(`${API_BASE_URL}/benchmarks/labels`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const detail = await this.readErrorDetail(response, 'Erro ao salvar gabarito');
      throw new Error(detail);
    }

    return response.json();
  }

  async deleteBenchmarkLabel(datasetId: string, benchmarkId: string): Promise<void> {
    const response = await this.fetchWithTimeout(`${API_BASE_URL}/benchmarks/labels/${encodeURIComponent(datasetId)}/${encodeURIComponent(benchmarkId)}`, {
      method: 'DELETE',
      headers: this.getHeaders(false),
    });

    if (!response.ok) {
      const detail = await this.readErrorDetail(response, 'Erro ao remover gabarito');
      throw new Error(detail);
    }
  }
}

export const api = new ApiClient();



