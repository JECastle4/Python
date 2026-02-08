import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { useAstronomyData } from '@/composables/useAstronomyData';
import { astronomyApi, ApiError } from '@/services/api';
import type { BatchEarthObservationsResponse } from '@/types/api.types';

// Mock the API module
// TODO (#12): Consider refactoring to use dependency injection or vi.doMock() for better test isolation
// Module-level mocks persist across test files, which can cause test pollution
vi.mock('@/services/api', () => ({
  astronomyApi: {
    getBatchEarthObservations: vi.fn(),
  },
  ApiError: class ApiError extends Error {
    constructor(public status: number, public statusText: string, message: string) {
      super(message);
      this.name = 'ApiError';
    }
  }
}));

describe('useAstronomyData', () => {
    it('should handle cancelSSE when no EventSource', () => {
      const { cancelSSE, error, loading } = useAstronomyData();
      // currentEventSource is null by default
      cancelSSE();
      expect(error.value).toBeNull();
      expect(loading.value).toBe(false);
    });
  const mockResponse: BatchEarthObservationsResponse = {
    frames: [
      {
        datetime: '2026-02-02T00:00:00',
        sun: { altitude: 15.5, azimuth: 120.0, is_visible: true },
        moon: { altitude: 45.2, azimuth: 230.5, is_visible: true },
        moon_phase: { illumination: 0.75, phase_angle: 90.0, phase_name: 'Waxing Gibbous' },
      },
      {
        datetime: '2026-02-02T01:00:00',
        sun: { altitude: 20.0, azimuth: 125.0, is_visible: true },
        moon: { altitude: 40.0, azimuth: 235.0, is_visible: true },
        moon_phase: { illumination: 0.76, phase_angle: 91.0, phase_name: 'Waxing Gibbous' },
      },
    ],
    metadata: {
      location: { latitude: 51.5, longitude: -0.1, elevation: 0 },
      frame_count: 2,
      start_datetime: '2026-02-02T00:00:00',
      end_datetime: '2026-02-02T01:00:00',
      time_span_hours: 1.0,
    },
  };

  it('should handle SSE frame and metadata events', async () => {
    const { fetchBatchObservationsSSE, sseFrames, sseExpectedFrameCount, data, loading, sseProgress } = useAstronomyData();
    // Mock EventSource
    let frameListener: ((event: any) => void) | undefined;
    let metadataListener: ((event: any) => void) | undefined;
    const addEventListener = (type: string, cb: (event: any) => void) => {
      if (type === 'frame') frameListener = cb;
      if (type === 'metadata') metadataListener = cb;
    };
    const origEventSource = globalThis.EventSource;
    class MockEventSource {
      static CONNECTING = 0;
      static OPEN = 1;
      static CLOSED = 2;
      addEventListener = addEventListener;
      close = vi.fn();
      onopen = null;
      onerror = null;
      constructor(_url: string) {}
    }
    globalThis.EventSource = MockEventSource as unknown as typeof EventSource;
    // Prepare params
    const params = {
      latitude: 51.5,
      longitude: -0.1,
      start_date: '2026-02-02',
      start_time: '00:00:00',
      end_date: '2026-02-02',
      end_time: '01:00:00',
      frame_count: 2,
    };
    const promise = fetchBatchObservationsSSE(params);
    // Simulate SSE events
    const frame1 = { datetime: '2026-02-02T00:00:00', sun: {}, moon: {}, moon_phase: {} };
    const frame2 = { datetime: '2026-02-02T01:00:00', sun: {}, moon: {}, moon_phase: {} };
    const metadata = { frame_count: 2, location: { latitude: 51.5, longitude: -0.1, elevation: 0 } };
    await Promise.resolve(); // allow listeners to be set
    if (frameListener) frameListener({ data: JSON.stringify(frame1) });
    expect(sseFrames.value.length).toBe(1);
    expect(sseProgress.value).toBeLessThan(1);
    if (metadataListener) metadataListener({ data: JSON.stringify(metadata) });
    expect(sseExpectedFrameCount.value).toBe(2);
    if (frameListener) frameListener({ data: JSON.stringify(frame2) });
    await promise;
    expect(data.value).not.toBeNull();
    expect(data.value?.frames.length).toBe(2);
    expect(data.value?.metadata.frame_count).toBe(2);
    expect(loading.value).toBe(false);
    expect(sseProgress.value).toBe(1);
    globalThis.EventSource = origEventSource;
  });

  it('should handle SSE error event', async () => {
    const { fetchBatchObservationsSSE, error, loading } = useAstronomyData();
    const origEventSource = globalThis.EventSource;
    let eventSourceInstance: any = null;
    class MockEventSource {
      static CONNECTING = 0;
      static OPEN = 1;
      static CLOSED = 2;
      close = vi.fn();
      onopen = null;
      onerror = null;
      constructor(_url: string) {
        eventSourceInstance = this;
      }
      addEventListener(_type: string, _cb: (event: any) => void) {}
    }
    globalThis.EventSource = MockEventSource as unknown as typeof EventSource;
    const params = {
      latitude: 51.5,
      longitude: -0.1,
      start_date: '2026-02-02',
      start_time: '00:00:00',
      end_date: '2026-02-02',
      end_time: '01:00:00',
      frame_count: 1,
    };
    const promise = fetchBatchObservationsSSE(params);
    await Promise.resolve();
    // Simulate error event by calling onerror on the EventSource instance
    if (eventSourceInstance && typeof eventSourceInstance.onerror === 'function') {
      eventSourceInstance.onerror({});
    }
    await expect(promise).rejects.toThrow('SSE connection error');
    expect(error.value).toBe('SSE connection error');
    expect(loading.value).toBe(false);
    globalThis.EventSource = origEventSource;
  });

  it('should cancel SSE loading', async () => {
    const { fetchBatchObservationsSSE, cancelSSE, error, loading } = useAstronomyData();
    // Mock EventSource
    const mockEventSource: any = {
      addEventListener: vi.fn(),
      close: vi.fn(),
      onopen: null,
      onerror: null,
    };
    const origEventSource = globalThis.EventSource;
    class MockEventSource {
      static CONNECTING = 0;
      static OPEN = 1;
      static CLOSED = 2;
      addEventListener = mockEventSource.addEventListener;
      close = mockEventSource.close;
      onopen = null;
      onerror = null;
      constructor(_url: string) {}
    }
    globalThis.EventSource = MockEventSource as unknown as typeof EventSource;
    const params = {
      latitude: 51.5,
      longitude: -0.1,
      start_date: '2026-02-02',
      start_time: '00:00:00',
      end_date: '2026-02-02',
      end_time: '01:00:00',
      frame_count: 1,
    };
    fetchBatchObservationsSSE(params);
    cancelSSE();
    expect(error.value).toBe('Loading cancelled by user.');
    expect(loading.value).toBe(false);
    globalThis.EventSource = origEventSource;
  });

  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should initialize with correct default state', () => {
    const { data, loading, error, hasData, frameCount } = useAstronomyData();

    expect(data.value).toBeNull();
    expect(loading.value).toBe(false);
    expect(error.value).toBeNull();
    expect(hasData.value).toBe(false);
    expect(frameCount.value).toBe(0);
  });

  it('should successfully fetch batch observations', async () => {
    vi.mocked(astronomyApi.getBatchEarthObservations).mockResolvedValueOnce(mockResponse);

    const { data, loading, error, hasData, frameCount, fetchBatchObservations } = useAstronomyData();

    const params = {
      latitude: 51.5,
      longitude: -0.1,
      start_date: '2026-02-02',
      start_time: '00:00:00',
      end_date: '2026-02-02',
      end_time: '01:00:00',
      frame_count: 2,
    };

    expect(loading.value).toBe(false);

    const fetchPromise = fetchBatchObservations(params);
    
    expect(loading.value).toBe(true);
    
    await fetchPromise;

    expect(loading.value).toBe(false);
    expect(data.value).toEqual(mockResponse);
    expect(error.value).toBeNull();
    expect(hasData.value).toBe(true);
    expect(frameCount.value).toBe(2);
    expect(astronomyApi.getBatchEarthObservations).toHaveBeenCalledWith(params);
  });

  it('should handle ApiError correctly', async () => {
    const apiError = new ApiError(400, 'Bad Request', 'Invalid parameters');
    vi.mocked(astronomyApi.getBatchEarthObservations).mockRejectedValueOnce(apiError);

    const { data, loading, error, hasData, fetchBatchObservations } = useAstronomyData();

    const params = {
      latitude: 91.0, // Invalid
      longitude: -0.1,
      start_date: '2026-02-02',
      start_time: '00:00:00',
      end_date: '2026-02-02',
      end_time: '01:00:00',
      frame_count: 1,
    };

    await fetchBatchObservations(params);

    expect(loading.value).toBe(false);
    expect(data.value).toBeNull();
    expect(error.value).toBe('API Error (400): Invalid parameters');
    expect(hasData.value).toBe(false);
  });

  it('should handle generic Error correctly', async () => {
    const genericError = new Error('Network failure');
    vi.mocked(astronomyApi.getBatchEarthObservations).mockRejectedValueOnce(genericError);

    const { error, fetchBatchObservations } = useAstronomyData();

    await fetchBatchObservations({
      latitude: 51.5,
      longitude: -0.1,
      start_date: '2026-02-02',
      start_time: '00:00:00',
      end_date: '2026-02-02',
      end_time: '01:00:00',
      frame_count: 1,
    });

    expect(error.value).toBe('Network failure');
  });

  it('should handle unknown error type', async () => {
    vi.mocked(astronomyApi.getBatchEarthObservations).mockRejectedValueOnce('string error');

    const { error, fetchBatchObservations } = useAstronomyData();

    await fetchBatchObservations({
      latitude: 51.5,
      longitude: -0.1,
      start_date: '2026-02-02',
      start_time: '00:00:00',
      end_date: '2026-02-02',
      end_time: '01:00:00',
      frame_count: 1,
    });

    expect(error.value).toBe('An unknown error occurred');
  });

  it('should clear data and error', () => {
    const { data, error, clearData } = useAstronomyData();

    // Set some data
    data.value = mockResponse;
    error.value = 'Some error';

    clearData();

    expect(data.value).toBeNull();
    expect(error.value).toBeNull();
  });

  it('should update frameCount when data changes', async () => {
    vi.mocked(astronomyApi.getBatchEarthObservations).mockResolvedValueOnce(mockResponse);

    const { frameCount, fetchBatchObservations } = useAstronomyData();

    expect(frameCount.value).toBe(0);

    await fetchBatchObservations({
      latitude: 51.5,
      longitude: -0.1,
      start_date: '2026-02-02',
      start_time: '00:00:00',
      end_date: '2026-02-02',
      end_time: '01:00:00',
      frame_count: 2,
    });

    expect(frameCount.value).toBe(2);
  });
});
