import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { AstronomyApiClient, ApiError } from '@/services/api';
import type { BatchEarthObservationsResponse } from '@/types/api.types';

describe('AstronomyApiClient', () => {
  let client: AstronomyApiClient;
  let fetchMock: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    client = new AstronomyApiClient();
    fetchMock = vi.fn();
    global.fetch = fetchMock;
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('getBatchEarthObservations', () => {
    it('should successfully fetch batch observations', async () => {
      const mockResponse: BatchEarthObservationsResponse = {
        frames: [
          {
            datetime: '2026-02-02T00:00:00',
            sun: { altitude: 15.5, azimuth: 120.0, is_visible: true },
            moon: { altitude: 45.2, azimuth: 230.5, is_visible: true },
            moon_phase: { illumination: 0.75, phase_angle: 90.0, phase_name: 'Waxing Gibbous' },
          },
        ],
        metadata: {
          location: { latitude: 51.5, longitude: -0.1, elevation: 0 },
          frame_count: 1,
          start_datetime: '2026-02-02T00:00:00',
          end_datetime: '2026-02-02T01:00:00',
          time_span_hours: 1.0,
        },
      };

      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const params = {
        latitude: 51.5,
        longitude: -0.1,
        start_date: '2026-02-02',
        start_time: '00:00:00',
        end_date: '2026-02-02',
        end_time: '01:00:00',
        frame_count: 1,
      };

      const result = await client.getBatchEarthObservations(params);

      expect(result).toEqual(mockResponse);
      expect(fetchMock).toHaveBeenCalledOnce();
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/batch-earth-observations'),
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
          body: JSON.stringify(params),
        })
      );
    });

    it('should handle API errors with status codes', async () => {
      const createErrorResponse = () => ({
        ok: false,
        status: 400,
        statusText: 'Bad Request',
        text: vi.fn().mockResolvedValue('Invalid parameters'),
      } as any);
      
      // Mock twice because we make two separate calls in the expects
      fetchMock.mockResolvedValueOnce(createErrorResponse());
      fetchMock.mockResolvedValueOnce(createErrorResponse());

      const params = {
        latitude: 91.0, // Invalid latitude
        longitude: -0.1,
        start_date: '2026-02-02',
        start_time: '00:00:00',
        end_date: '2026-02-02',
        end_time: '01:00:00',
        frame_count: 1,
      };

      await expect(client.getBatchEarthObservations(params)).rejects.toThrow(ApiError);
      await expect(client.getBatchEarthObservations(params)).rejects.toThrow('Invalid parameters');
    });

    it('should handle network errors', async () => {
      fetchMock.mockRejectedValueOnce(new Error('Network failure'));

      const params = {
        latitude: 51.5,
        longitude: -0.1,
        start_date: '2026-02-02',
        start_time: '00:00:00',
        end_date: '2026-02-02',
        end_time: '01:00:00',
        frame_count: 1,
      };

      await expect(client.getBatchEarthObservations(params)).rejects.toThrow('Network error');
    });

    it('should handle request timeout', async () => {
      // Create a client with a shorter timeout for testing
      const shortTimeoutClient = new AstronomyApiClient();
      (shortTimeoutClient as any).timeout = 100; // 100ms timeout

      // Mock fetch to properly handle abort signal
      fetchMock.mockImplementationOnce((_url: string, options: any) => {
        return new Promise((resolve, reject) => {
          const signal = options?.signal as AbortSignal;
          if (signal) {
            // Listen for the abort event from the timeout
            signal.addEventListener('abort', () => {
              const error = new Error('The operation was aborted');
              error.name = 'AbortError';
              reject(error);
            });
          }
          // Never resolve to simulate a long-running request
        });
      });

      const params = {
        latitude: 51.5,
        longitude: -0.1,
        start_date: '2026-02-02',
        start_time: '00:00:00',
        end_date: '2026-02-02',
        end_time: '01:00:00',
        frame_count: 1,
      };

      await expect(shortTimeoutClient.getBatchEarthObservations(params)).rejects.toThrow('Request timeout');
    });

    it('should include optional elevation parameter when provided', async () => {
      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ frames: [], metadata: {} }),
      });

      const params = {
        latitude: 51.5,
        longitude: -0.1,
        start_date: '2026-02-02',
        start_time: '00:00:00',
        end_date: '2026-02-02',
        end_time: '01:00:00',
        frame_count: 1,
        elevation: 100.5,
      };

      await client.getBatchEarthObservations(params);

      expect(fetchMock).toHaveBeenCalledWith(
        expect.anything(),
        expect.objectContaining({
          body: JSON.stringify(params),
        })
      );
    });
  });

  describe('ApiError', () => {
    it('should create error with correct properties', () => {
      const error = new ApiError(404, 'Not Found', 'Resource not found');

      expect(error).toBeInstanceOf(Error);
      expect(error).toBeInstanceOf(ApiError);
      expect(error.status).toBe(404);
      expect(error.statusText).toBe('Not Found');
      expect(error.message).toBe('Resource not found');
      expect(error.name).toBe('ApiError');
    });
  });
});
