/**
 * ApiClient - Type-safe, centralized API requests for backend communication
 */
class ApiClient {
  static async getInitialState() {
    const res = await fetch('/api/initial-state');
    if (!res.ok) throw new Error(`HTTP ${res.status}: Failed to fetch initial state`);
    return await res.json();
  }

  static async calculate(state) {
    const res = await fetch('/api/calculate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(state)
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}: Calculation failed`);
    return await res.json();
  }

  static async saveState(state) {
    const res = await fetch('/api/save-state', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(state)
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}: Save failed`);
    return await res.json();
  }

  static async resetState() {
    const res = await fetch('/api/reset-state', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}: Reset failed`);
    return await res.json();
  }

  static async calculateTonnage(payload) {
    const res = await fetch('/api/v1/tonnage/calculate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}: Tonnage calculation failed`);
    return await res.json();
  }

  static async getCurrentTonnage() {
    const res = await fetch('/api/v1/tonnage/current');
    if (!res.ok) throw new Error(`HTTP ${res.status}: Failed to fetch current tonnage`);
    return await res.json();
  }
}

window.apiClient = ApiClient;
