const API_BASE_URL = '/api/v1';

export async function apiGet<T>(path: string): Promise<T> {
  const token = localStorage.getItem('accessToken');
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `API error: ${response.statusText}`);
  }

  return response.json();
}

export async function apiPost<T>(path: string, body: any): Promise<T> {
  const token = localStorage.getItem('accessToken');
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `API error: ${response.statusText}`);
  }

  return response.json();
}
