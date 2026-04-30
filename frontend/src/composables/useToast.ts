// @ts-ignore - vue-toast doesn't have TypeScript types
import { createToast } from 'vue-toast';

/**
 * Composable for displaying toast notifications
 * Wraps vue-toast with accessibility-friendly defaults
 */
export function useToast() {
  return {
    success: (message: string, duration = 3000) => {
      createToast(message, {
        type: 'success',
        duration,
        position: 'top-right',
      });
    },
    error: (message: string, duration = 5000) => {
      createToast(message, {
        type: 'error',
        duration,
        position: 'top-right',
      });
    },
    info: (message: string, duration = 3000) => {
      createToast(message, {
        type: 'info',
        duration,
        position: 'top-right',
      });
    },
    warning: (message: string, duration = 4000) => {
      createToast(message, {
        type: 'warning',
        duration,
        position: 'top-right',
      });
    },
  };
}
