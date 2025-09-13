// lib/api.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001';

export interface LegalAnalysisResult {
  timestamp: string;
  query: string;
  key_terms: string[];
  legal_context: string;
  analysis: Record<string, string>;
  status: 'success' | 'error' | 'no_matches';
  error?: string;
}

export async function analyzeLegalQuery(query: string): Promise<LegalAnalysisResult> {
  try {
    const response = await fetch(`${API_BASE_URL}/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || `HTTP ${response.status}: ${response.statusText}`);
    }

    const result = await response.json();
    return result;
  } catch (error) {
    console.error('Legal Analysis API Error:', error);
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('Failed to analyze legal query');
  }
}