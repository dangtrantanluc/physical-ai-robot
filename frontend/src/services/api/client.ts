/**
 * Axios instance shared by all API services.
 *
 * - Base URL is resolved lazily per request from the settings store, so changing the
 *   Server URL in Settings takes effect immediately (no app restart, no stale client).
 * - A correlation id is attached to every request (matches the backend's
 *   x-correlation-id tracing).
 * - Errors are normalized to `ApiError` so callers get a consistent shape.
 */
import axios, {AxiosError, type AxiosInstance, type AxiosRequestConfig} from 'axios';
import {useSettingsStore} from '@/store/settingsStore';

export class ApiError extends Error {
  constructor(
    public readonly status: number | null,
    public readonly code: string,
    message: string,
    public readonly correlationId?: string,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

let counter = 0;
const correlationId = (): string => {
  counter = (counter + 1) % 1_000_000;
  return `rc-${Date.now().toString(36)}-${counter.toString(36)}`;
};

const instance: AxiosInstance = axios.create({timeout: 8000});

instance.interceptors.request.use(config => {
  config.baseURL = useSettingsStore.getState().settings.serverUrl;
  config.headers.set('x-correlation-id', correlationId());
  return config;
});

instance.interceptors.response.use(
  response => response,
  (error: AxiosError<{error?: {code?: string; message?: string; correlation_id?: string}}>) => {
    const body = error.response?.data?.error;
    throw new ApiError(
      error.response?.status ?? null,
      body?.code ?? error.code ?? 'NETWORK_ERROR',
      body?.message ?? error.message ?? 'Request failed',
      body?.correlation_id,
    );
  },
);

/** Low-level helpers. Feature services wrap these; screens never call them directly. */
export const http = {
  get: <T>(url: string, config?: AxiosRequestConfig) => instance.get<T>(url, config).then(r => r.data),
  post: <T>(url: string, data?: unknown, config?: AxiosRequestConfig) =>
    instance.post<T>(url, data, config).then(r => r.data),
};

export default instance;
