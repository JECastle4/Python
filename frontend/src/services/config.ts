import type { ApiConfig } from '@/types/api.types';

/**
 * API Configuration
 * Uses environment variables for different deployment environments
 */
export const API_CONFIG: ApiConfig = {
  baseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 30000,
};

// API Endpoints
export const API_ENDPOINTS = {
  batchEarthObservations: '/api/v1/batch-earth-observations',
  sunPosition: '/api/v1/sun-position',
  moonPosition: '/api/v1/moon-position',
  moonPhase: '/api/v1/moon-phase',
} as const;
