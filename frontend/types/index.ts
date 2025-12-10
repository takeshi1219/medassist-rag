/**
 * Type definitions for MedAssist RAG
 */

// User types
export interface User {
  id: string;
  email: string;
  name: string;
  role: "doctor" | "nurse" | "pharmacist" | "admin";
  organization?: string;
  license_number?: string;
}

// Chat types
export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: Citation[];
  timestamp: Date;
  isStreaming?: boolean;
}

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

export interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  createdAt: Date;
  updatedAt: Date;
}

// Drug types
export interface Drug {
  name: string;
  generic_name?: string;
  brand_names: string[];
  drug_class?: string;
  description?: string;
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

export type InteractionSeverity = DrugInteraction["severity"];

// Medical code types
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

// Query history types
export interface QueryLog {
  id: string;
  query_text: string;
  response_text?: string;
  sources?: Citation[];
  query_type: "chat" | "drug_check" | "code_lookup" | "search";
  response_time_ms: number;
  created_at: string;
}

export interface SavedQuery {
  id: string;
  query_log_id: string;
  title: string;
  notes?: string;
  query: QueryLog;
  created_at: string;
}

// UI state types
export interface AppState {
  user: User | null;
  isAuthenticated: boolean;
  sidebarOpen: boolean;
  theme: "light" | "dark" | "system";
}

// API response types
export interface ApiError {
  detail: string;
  status_code: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  has_more: boolean;
}

