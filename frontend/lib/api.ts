/**
 * API Client for MedAssist RAG Backend
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Types
export interface Citation {
  id: number;
  title: string;
  authors?: string[];
  journal?: string;
  year?: number;
  doi?: string;
  pmid?: string;
  url?: string;
  snippet: string;
  relevance_score: number;
}

export interface ChatResponse {
  answer: string;
  sources: Citation[];
  conversation_id: string;
  query_id: string;
  processing_time_ms: number;
  model_used: string;
}

export interface ChatRequest {
  query: string;
  conversation_id?: string;
  language?: "en" | "ja";
  include_sources?: boolean;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: {
    id: string;
    email: string;
    name: string;
    role: string;
  };
}

export interface DrugInteraction {
  drug_a: string;
  drug_b: string;
  severity: "none" | "mild" | "moderate" | "severe" | "contraindicated";
  description: string;
  mechanism?: string;
  management?: string;
  clinical_effects: string[];
  source?: string;
}

export interface Drug {
  name: string;
  generic_name?: string;
  brand_names: string[];
  drug_class?: string;
  description?: string;
}

export interface DrugCheckResponse {
  interactions: DrugInteraction[];
  alternatives: Drug[];
  warnings: string[];
  checked_drugs: string[];
  has_severe_interactions: boolean;
  has_contraindications: boolean;
}

export interface ICD10Code {
  code: string;
  description: string;
  category?: string;
  subcategory?: string;
  includes: string[];
  excludes: string[];
}

export interface SNOMEDConcept {
  concept_id: string;
  term: string;
  semantic_type?: string;
  synonyms: string[];
}

export interface TranslationResponse {
  original_term: string;
  translated_term: string;
  from_language: string;
  to_language: string;
  medical_context?: string;
  icd10_codes: string[];
  layman_explanation?: string;
}

// Alias for backward compatibility
export type MedicalTermTranslation = TranslationResponse;

// API Client class
class ApiClient {
  private token: string | null = null;

  constructor() {
    // Load token from localStorage if available (client-side only)
    if (typeof window !== "undefined") {
      this.token = localStorage.getItem("token");
    }
  }

  setToken(token: string) {
    this.token = token;
    if (typeof window !== "undefined") {
      localStorage.setItem("token", token);
    }
  }

  clearToken() {
    this.token = null;
    if (typeof window !== "undefined") {
      localStorage.removeItem("token");
    }
  }

  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      "Content-Type": "application/json",
    };
    if (this.token) {
      headers["Authorization"] = `Bearer ${this.token}`;
    }
    return headers;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_URL}${endpoint}`;
    const response = await fetch(url, {
      ...options,
      headers: {
        ...this.getHeaders(),
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  // Auth endpoints
  async login(email: string, password: string): Promise<LoginResponse> {
    return this.request<LoginResponse>("/api/v1/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
  }

  async register(data: {
    email: string;
    password: string;
    name: string;
    role?: string;
  }): Promise<LoginResponse> {
    return this.request<LoginResponse>("/api/v1/auth/register", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async getMe(): Promise<any> {
    return this.request("/api/v1/auth/me");
  }

  // Chat endpoints
  async chat(request: ChatRequest): Promise<ChatResponse> {
    return this.request<ChatResponse>("/api/v1/chat", {
      method: "POST",
      body: JSON.stringify(request),
    });
  }

  async getSuggestions(): Promise<{ suggestions: any[] }> {
    return this.request("/api/v1/chat/suggestions");
  }

  // Drug endpoints
  async checkDrugInteractions(drugs: string[]): Promise<DrugCheckResponse> {
    return this.request<DrugCheckResponse>("/api/v1/drugs/check-interactions", {
      method: "POST",
      body: JSON.stringify({ drugs }),
    });
  }

  async searchDrugs(query: string, limit: number = 10): Promise<{ drugs: any[] }> {
    return this.request(`/api/v1/drugs/search?query=${encodeURIComponent(query)}&limit=${limit}`);
  }

  async getDrugInfo(drugName: string): Promise<any> {
    return this.request(`/api/v1/drugs/${encodeURIComponent(drugName)}`);
  }

  // Medical codes endpoints
  async searchICD10(query: string): Promise<ICD10Code[]> {
    return this.request(`/api/v1/codes/icd10/search?query=${encodeURIComponent(query)}`);
  }

  async searchSNOMED(query: string): Promise<any[]> {
    return this.request(`/api/v1/codes/snomed/search?query=${encodeURIComponent(query)}`);
  }

  async translateTerm(
    term: string,
    fromLang: "en" | "ja",
    toLang: "en" | "ja"
  ): Promise<TranslationResponse> {
    return this.request("/api/v1/codes/translate", {
      method: "POST",
      body: JSON.stringify({
        term,
        from_language: fromLang,
        to_language: toLang,
        include_explanation: true,
      }),
    });
  }

  // History endpoints
  async getHistory(page = 1, pageSize = 20): Promise<any> {
    return this.request(`/api/v1/history?page=${page}&page_size=${pageSize}`);
  }

  async bookmarkQuery(queryId: string, title: string, notes?: string): Promise<any> {
    return this.request(`/api/v1/history/${queryId}/bookmark`, {
      method: "POST",
      body: JSON.stringify({ title, notes }),
    });
  }
}

// Export singleton instance
export const api = new ApiClient();

