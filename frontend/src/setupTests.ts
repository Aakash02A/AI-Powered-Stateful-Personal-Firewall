import '@testing-library/jest-dom';
import { vi } from 'vitest';

// Mock matchMedia for jsdom
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(), // deprecated
    removeListener: vi.fn(), // deprecated
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

// Mock ResizeObserver for Recharts
vi.stubGlobal('ResizeObserver', class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
});

// Mock react-virtual because jsdom has 0 height containers
vi.mock('@tanstack/react-virtual', () => ({
  useVirtualizer: (options: any) => ({
    getVirtualItems: () => Array.from({ length: options.count }).map((_, i) => ({
      index: i,
      size: 50,
      start: i * 50
    })),
    getTotalSize: () => options.count * 50,
  })
}));

import { server } from './mocks/server';
import { beforeAll, afterEach, afterAll } from 'vitest';

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
