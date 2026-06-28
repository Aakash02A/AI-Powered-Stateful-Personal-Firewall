import axios from 'axios';

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': import.meta.env.VITE_API_KEY || 'default_dev_key',
  },
});

// Generic error handler
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // We could trigger global toasts here if needed
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);
