export const getApiBaseUrl = (): string => {
  const env = (typeof import.meta !== "undefined" && import.meta && (import.meta as any).env) || {};
  const baseUrl = env.VITE_API_BASE_URL;
  if (baseUrl) return baseUrl.replace(/\/$/, "");

  if (env.PROD) return "";

  return "http://localhost:8001";
};

export const fetchApi = async (endpoint: string, options: RequestInit = {}) => {
  const baseUrl = getApiBaseUrl();
  return fetch(`${baseUrl}${endpoint}`, options);
};
