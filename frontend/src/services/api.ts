import { API_CONFIG, API_ENDPOINTS } from './config';
// ...existing code...
export { API_CONFIG };
import type { BatchEarthObservationsResponse } from '@/types/api.types';

/**
 * API Client for astronomy data
 */

export class ApiError extends Error {
  constructor(
    public status: number,
    public statusText: string,
    message: string
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

interface BatchObservationsParams {
  latitude: number;
  longitude: number;
  start_date: string;
  start_time: string;
  end_date: string;
  end_time: string;
  frame_count: number;
  elevation?: number;
}

export class AstronomyApiClient {
  private baseUrl: string;
  private timeout: number;

  constructor() {
    this.baseUrl = API_CONFIG.baseUrl;
    this.timeout = API_CONFIG.timeout;
  }

  /**
   * Fetch batch earth observations for animation
   */
  async getBatchEarthObservations(
    params: BatchObservationsParams
  ): Promise<BatchEarthObservationsResponse> {
    const url = `${this.baseUrl}${API_ENDPOINTS.batchEarthObservations}`;

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(params),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorText = await response.text();
        throw new ApiError(
          response.status,
          response.statusText,
          errorText || `API request failed: ${response.statusText}`
        );
      }

      return await response.json();
    } catch (error) {
      clearTimeout(timeoutId);

      if (error instanceof ApiError) {
        throw error;
      }

      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          throw new Error('Request timeout');
        }
        throw new Error(`Network error: ${error.message}`);
      }

      throw new Error('Unknown error occurred');
    }
  }
}

// Export singleton instance
export const astronomyApi = new AstronomyApiClient();
