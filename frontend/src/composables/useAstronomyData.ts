import { ref, computed } from 'vue';
import { astronomyApi, ApiError } from '@/services/api';
import type { BatchEarthObservationsResponse } from '@/types/api.types';

/**
 * Composable for fetching and managing astronomy data
 */
export function useAstronomyData() {
  const data = ref<BatchEarthObservationsResponse | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  const hasData = computed(() => data.value !== null);
  const frameCount = computed(() => data.value?.metadata.frame_count ?? 0);

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
      console.error('Failed to fetch astronomy data:', err);
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
    clearData,
  };
}
