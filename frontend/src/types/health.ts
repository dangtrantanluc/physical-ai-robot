/** GET /health response (matches the FastAPI backend). */
export interface HealthResponse {
  status: 'ok' | 'degraded';
  version: string;
  environment: string;
  checks: {
    redis: boolean;
    database: boolean;
  };
}
