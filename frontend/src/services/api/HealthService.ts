/** HealthService — GET /health. */
import type {HealthResponse} from '@/types';
import {http} from './client';

export const HealthService = {
  getHealth(): Promise<HealthResponse> {
    return http.get<HealthResponse>('/health');
  },
};
