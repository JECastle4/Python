import { useToast as useToastNotification } from 'vue-toast-notification';
import 'vue-toast-notification/dist/theme-default.css';

/**
 * Composable for displaying toast notifications
 * Wraps vue-toast-notification with consistent API and defaults
 */
export function useToast() {
  const toast = useToastNotification();

  return {
    success: (message: string, duration = 3000) => {
      toast.success(message, {
        duration,
        position: 'top-right',
      });
    },
    error: (message: string, duration = 5000) => {
      toast.error(message, {
        duration,
        position: 'top-right',
      });
    },
    info: (message: string, duration = 3000) => {
      toast.info(message, {
        duration,
        position: 'top-right',
      });
    },
    warning: (message: string, duration = 4000) => {
      toast.warning(message, {
        duration,
        position: 'top-right',
      });
    },
  };
}
