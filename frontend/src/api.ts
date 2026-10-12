export const getApiBaseUrl = (): string => {
  const meta = import.meta as any;
  const baseUrl = meta.env.VITE_API_BASE_URL;
  if (!baseUrl) {
    if (meta.env.PROD) {
      throw new Error("VITE_API_BASE_URL is not configured for production environment.");
    }
    return "http://localhost:8000"; // fallback for local dev
  }
  return baseUrl;
};

export const fetchApi = async (endpoint: string, options: RequestInit = {}) => {
  const baseUrl = getApiBaseUrl();
  return fetch(`${baseUrl}${endpoint}`, options);
};
