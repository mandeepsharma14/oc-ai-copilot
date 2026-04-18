/**
 * Axios API client with auth interceptor and error handling.
 */
import axios from "axios";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const apiClient = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: { "Content-Type": "application/json" },
});

// Attach auth token if available
apiClient.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("oc_access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// Global error handling
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      if (typeof window !== "undefined") {
        localStorage.removeItem("oc_access_token");
        window.location.href = "/login";
      }
    }
    return Promise.reject(
      error.response?.data?.detail || error.message || "An error occurred"
    );
  }
);

export const chatApi = {
  query:      (req: object)    => apiClient.post("/api/v1/chat/query", req),
  history:    (sessionId: string) => apiClient.get(`/api/v1/chat/history/${sessionId}`),
};

export const documentsApi = {
  list:   (streamType: string, domain?: string) =>
    apiClient.get("/api/v1/documents/", { params: { stream_type: streamType, domain } }),
  ingest: (req: object) => apiClient.post("/api/v1/documents/ingest", req),
};

export const adminApi = {
  metrics:       () => apiClient.get("/api/v1/admin/metrics"),
  usageByDomain: () => apiClient.get("/api/v1/admin/usage-by-domain"),
  gaps:          () => apiClient.get("/api/v1/admin/knowledge-gaps"),
  cost:          () => apiClient.get("/api/v1/admin/cost"),
};
