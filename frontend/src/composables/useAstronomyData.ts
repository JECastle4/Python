import { ref, computed } from 'vue';
import { astronomyApi, ApiError } from '@/services/api';
import { API_CONFIG } from '@/services/config';
import type { BatchEarthObservationsResponse } from '@/types/api.types';

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

/**
 * Composable for fetching and managing astronomy data
 */
export function useAstronomyData() {
  const data = ref<BatchEarthObservationsResponse | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  const hasData = computed(() => data.value !== null);
  const frameCount = computed(() => data.value?.metadata.frame_count ?? 0);

  const sseFrames = ref<any[]>([]);
  const sseExpectedFrameCount = ref<number>(0);
  const sseProgress = computed(() => {
    if (sseExpectedFrameCount.value === 0) return 0;
    return sseFrames.value.length / sseExpectedFrameCount.value;
  });

  let currentEventSource: EventSource | null = null;

  /**
   * Fetch batch earth observations via SSE
   */
  async function fetchBatchObservationsSSE(params: BatchObservationsParams) {
    loading.value = true;
    error.value = null;
    data.value = null;
    sseFrames.value = [];
    sseExpectedFrameCount.value = params.frame_count;
    let metadata: any = null;

    return new Promise<void>((resolve, reject) => {
      // Build query string for GET request
      const paramsObj = {
        start_date: params.start_date,
        start_time: params.start_time,
        end_date: params.end_date,
        end_time: params.end_time,
        frame_count: params.frame_count,
        latitude: params.latitude,
        longitude: params.longitude,
        elevation: params.elevation ?? 0.0,
      };
      const query = new URLSearchParams(paramsObj as any).toString();
      const url = `${API_CONFIG.baseUrl}/api/v1/batch-earth-observations-stream?${query}`;
      const eventSource = new EventSource(url);
      currentEventSource = eventSource;

      eventSource.onopen = null; // Remove POST fetch logic, not needed for GET

      eventSource.addEventListener('frame', (event: MessageEvent) => {
        const frame = JSON.parse(event.data);
        sseFrames.value = [...sseFrames.value, frame];
        checkCompletion();
      });

      eventSource.addEventListener('metadata', (event: MessageEvent) => {
        metadata = JSON.parse(event.data);
        sseExpectedFrameCount.value = metadata.frame_count;
        checkCompletion();
      });

      eventSource.onerror = (_event) => {
        error.value = 'SSE connection error';
        loading.value = false;
        eventSource.close();
        currentEventSource = null;
        reject(new Error('SSE connection error'));
      };

      function checkCompletion() {
        if (metadata && sseFrames.value.length === sseExpectedFrameCount.value) {
          data.value = { frames: sseFrames.value, metadata };
          loading.value = false;
          eventSource.close();
          currentEventSource = null;
          resolve();
        }
      }
    });
  }

  function cancelSSE() {
    if (currentEventSource) {
      currentEventSource.close();
      currentEventSource = null;
      loading.value = false;
      error.value = 'Loading cancelled by user.';
    }
  }

  async function fetchBatchObservations(params: {
    latitude: number;
    longitude: number;
    start_date: string;
    start_time: string;
    end_date: string;
    end_time: string;
    frame_count: number;
    elevation?: number;
  }) {
    loading.value = true;
    error.value = null;

    try {
      const response = await astronomyApi.getBatchEarthObservations(params);
      data.value = response;
    } catch (err) {
      if (err instanceof ApiError) {
        error.value = `API Error (${err.status}): ${err.message}`;
      } else if (err instanceof Error) {
        error.value = err.message;
      } else {
        error.value = 'An unknown error occurred';
      }
      // Console logging only in development - see issue #13 for production error monitoring
      if (import.meta.env.DEV) {
        console.error('Failed to fetch astronomy data:', err);
      }
    } finally {
      loading.value = false;
    }
  }

  function clearData() {
    data.value = null;
    error.value = null;
  }

  return {
    data,
    loading,
    error,
    hasData,
    frameCount,
    fetchBatchObservations,
    fetchBatchObservationsSSE,
    cancelSSE,
    clearData,
    sseFrames,
    sseExpectedFrameCount,
    sseProgress,
  };
}
