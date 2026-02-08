import type { ApiConfig } from '@/types/api.types';

/**
 * API Configuration
 * Uses environment variables for different deployment environments
 */
const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Validate configuration in production mode
if (!import.meta.env.DEV) {
  if (!import.meta.env.VITE_API_BASE_URL) {
    console.warn(
      '⚠️ PRODUCTION WARNING: VITE_API_BASE_URL not set! Using default localhost:8000. ' +
      'This will not work in production. Set VITE_API_BASE_URL in .env.production'
    );
  }
  if (baseUrl.startsWith('http://')) {
    console.warn(
      '⚠️ SECURITY WARNING: API base URL uses insecure http protocol in production! ' +
      `Current URL: ${baseUrl}. Use https for production deployments.`
    );
  }
}

export const API_CONFIG: ApiConfig = {
  baseUrl,
  timeout: 30000,
};

// API Endpoints
export const API_ENDPOINTS = {
  batchEarthObservations: '/api/v1/batch-earth-observations',
  sunPosition: '/api/v1/sun-position',
  moonPosition: '/api/v1/moon-position',
  moonPhase: '/api/v1/moon-phase',
} as const;
