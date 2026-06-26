import { apiClient } from './client';
import { describe, it, expect } from 'vitest';

describe('API Client', () => {
  it('is configured correctly', () => {
    expect(apiClient.defaults.baseURL).toBeDefined();
    expect(apiClient.interceptors.request).toBeDefined();
  });
});
