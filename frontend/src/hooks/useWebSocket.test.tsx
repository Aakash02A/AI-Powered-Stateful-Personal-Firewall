import { renderHook, act } from '@testing-library/react';
import { useWebSocket } from './useWebSocket';
import { describe, it, expect, vi, beforeEach } from 'vitest';

describe('useWebSocket', () => {
  let mockWebSocket: any;

  beforeEach(() => {
    mockWebSocket = {
      send: vi.fn(),
      close: vi.fn(),
      readyState: 1,
    };
    
    vi.stubGlobal('WebSocket', class {
      static OPEN = 1;
      static CLOSED = 3;
      constructor() {
        return mockWebSocket;
      }
    });
  });

  it('connects to websocket on mount', () => {
    const { result, unmount } = renderHook(() => useWebSocket());
    
    act(() => {
      if (mockWebSocket.onopen) mockWebSocket.onopen();
    });
    
    expect(result.current.isConnected).toBe(true);

    act(() => {
      const msg = { topic: 'alert', data: { severity: 'LOW' } };
      if (mockWebSocket.onmessage) mockWebSocket.onmessage({ data: JSON.stringify(msg) });
    });

    expect(result.current.lastMessage).toEqual({ topic: 'alert', data: { severity: 'LOW' } });
    
    unmount();
  });
});
