/**
 * Centralized HTTP Client with Automatic CSRF Token Injection
 * Pattern: Anti-Corruption Layer (Gentleman Programming)
 */
import axios, { AxiosInstance, InternalAxiosRequestConfig } from 'axios';

/**
 * Utility to extract CSRF token from document.cookie
 */
export const getCsrfToken = (): string => {
  if (typeof document === 'undefined') return '';
  const match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
  return match ? decodeURIComponent(match[1]) : '';
};

export const httpClient: AxiosInstance = axios.create({
  baseURL: '/api/chat/',
  timeout: 15000,
  headers: {
    'X-Requested-With': 'XMLHttpRequest',
  },
});

// Request Interceptor: Attach CSRF token on mutating requests
httpClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const method = config.method?.toUpperCase();
    if (method && ['POST', 'PUT', 'PATCH', 'DELETE'].includes(method)) {
      const csrf = getCsrfToken();
      if (csrf) {
        config.headers.set('X-CSRFToken', csrf);
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: Normalized error handling
httpClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error?.response?.status;
    if (status === 403) {
      console.warn('[HTTP Client 403]: Permiso denegado o CSRF inválido.');
    } else if (status === 401) {
      console.warn('[HTTP Client 401]: Sesión no autenticada.');
    }
    return Promise.reject(error);
  }
);

export default httpClient;

