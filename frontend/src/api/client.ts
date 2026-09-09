import axios from 'axios';

const apiKey = import.meta.env.VITE_API_KEY;
if (!apiKey) {
  throw new Error('VITE_API_KEY environment variable is required');
}

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': apiKey,
  },
});

// Generic error handler
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    return Promise.reject(error);
  }
);
