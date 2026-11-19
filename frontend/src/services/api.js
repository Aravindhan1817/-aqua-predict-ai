/**
 * Unified API Client for AI-Based Water Quality Prediction System
 */

const rawBaseUrl = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || '';
const BASE_URL = rawBaseUrl.endsWith('/') ? rawBaseUrl.slice(0, -1) : rawBaseUrl;

async function handleResponse(response) {
  if (!response.ok) {
    let errorMsg = `HTTP ${response.status}: ${response.statusText}`;
    try {
      const errorData = await response.json();
      if (errorData.detail) {
        errorMsg = typeof errorData.detail === 'string' 
          ? errorData.detail 
          : JSON.stringify(errorData.detail);
      }
    } catch {
      // ignore json parse errors
    }
    throw new Error(errorMsg);
  }
  return response.json();
}

export const api = {
  // Check backend health
  async checkHealth() {
    try {
      const res = await fetch(`${BASE_URL}/health`);
      return await handleResponse(res);
    } catch (err) {
      // try fallback root
      const res = await fetch(`${BASE_URL}/`);
      return await handleResponse(res);
    }
  },

  // Submit water parameters for ML prediction
  async predict(sampleData) {
    const res = await fetch(`${BASE_URL}/api/predict`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(sampleData),
    });
    return handleResponse(res);
  },

  // Retrieve past prediction records
  async getHistory(limit = 100) {
    const res = await fetch(`${BASE_URL}/api/history?limit=${limit}`);
    return handleResponse(res);
  },

  // Delete a single history item
  async deleteHistoryItem(id) {
    const res = await fetch(`${BASE_URL}/api/history/${id}`, {
      method: 'DELETE',
    });
    return handleResponse(res);
  },

  // Delete all history records
  async clearAllHistory() {
    const res = await fetch(`${BASE_URL}/api/history`, {
      method: 'DELETE',
    });
    return handleResponse(res);
  },

  // Get benchmark ML model performance metrics
  async getModelPerformance() {
    const res = await fetch(`${BASE_URL}/api/model-performance`);
    return handleResponse(res);
  },

  // Get pre-configured sample presets
  async getPresets() {
    const res = await fetch(`${BASE_URL}/api/presets`);
    return handleResponse(res);
  },

  // Get regulatory water quality standards
  async getStandards() {
    const res = await fetch(`${BASE_URL}/api/standards`);
    return handleResponse(res);
  }
};
