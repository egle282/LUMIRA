export const getApiBaseUrl = (): string => {
  const meta = import.meta as any;
  const baseUrl = meta.env.VITE_API_BASE_URL;
  if (baseUrl) return baseUrl.replace(/\/$/, "");

  // In production, nginx serves the SPA and proxies /api to the backend.
  // An empty base URL keeps API requests on the same origin.
  if (meta.env.PROD) return "";

  return "http://localhost:8000";
};

export const fetchApi = async (endpoint: string, options: RequestInit = {}) => {
  const baseUrl = getApiBaseUrl();
  return fetch(`${baseUrl}${endpoint}`, options);
};
