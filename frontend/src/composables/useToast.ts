import { useToast as useToastNotification } from 'vue-toast-notification';
import type { ActiveToast } from 'vue-toast-notification';

/**
 * Composable for displaying toast notifications.
 * Wraps vue-toast-notification with consistent defaults.
 * All methods return ActiveToast so callers can dismiss any notification
 * programmatically (e.g. clearing a success toast on scene transition).
 */
export function useToast() {
  const toast = useToastNotification();

  return {
    success: (message: string, duration = 3000): ActiveToast => {
      return toast.success(message, {
        duration,
        position: 'top-right',
      });
    },
    error: (message: string, duration = 5000): ActiveToast => {
      return toast.error(message, {
        duration,
        position: 'top-right',
      });
    },
    info: (message: string, duration = 3000): ActiveToast => {
      return toast.info(message, {
        duration,
        position: 'top-right',
      });
    },
    warning: (message: string, duration = 4000): ActiveToast => {
      return toast.warning(message, {
        duration,
        position: 'top-right',
      });
    },
  };
}
