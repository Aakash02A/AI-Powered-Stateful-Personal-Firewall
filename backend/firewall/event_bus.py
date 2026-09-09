import asyncio
import logging
from typing import Any, Callable

logger = logging.getLogger("EventBus")


class EventBus:
    """
    A simple in-memory publish-subscribe event bus for distributing internal
    events (like Alerts and Blocked Connections) to asynchronous consumers like WebSockets.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventBus, cls).__new__(cls)
            cls._instance.subscribers = {}
            # Use asyncio queues for async consumers
            cls._instance.async_queues = {}
        return cls._instance

    def subscribe(self, topic: str, callback: Callable):
        """Subscribe a synchronous callback to a topic."""
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        self.subscribers[topic].append(callback)

    def subscribe_async(self, topic: str) -> asyncio.Queue:
        """Subscribe an asynchronous queue to a topic. Useful for WebSockets."""
        if topic not in self.async_queues:
            self.async_queues[topic] = []
        queue = asyncio.Queue()
        self.async_queues[topic].append(queue)
        return queue

    def unsubscribe_async(self, topic: str, queue: asyncio.Queue):
        if topic in self.async_queues and queue in self.async_queues[topic]:
            self.async_queues[topic].remove(queue)

    def publish(self, topic: str, message: Any):
        """Publish a message to all subscribers of a topic."""
        # 1. Notify sync subscribers
        if topic in self.subscribers:
            for callback in self.subscribers[topic]:
                try:
                    callback(message)
                except Exception as e:
                    logger.error(
                        f"Error in EventBus subscriber for topic '{topic}': {e}"
                    )

        # 2. Notify async queues
        if topic in self.async_queues:
            for queue in self.async_queues[topic]:
                # Non-blocking put since it's an asyncio.Queue, but note we are calling it from a sync thread
                # so we must use call_soon_threadsafe if there's a running loop, or fallback to putting it directly
                # if asyncio allows cross-thread put_nowait (it typically requires loop.call_soon_threadsafe).
                # Actually, put_nowait is NOT thread-safe. We should check if we have an event loop attached to the queue.
                # However, since standard queues in python asyncio aren't thread safe across threads, we need a slight adjustment
                # to safely bridge the sync thread (IDS engine) and the async thread (FastAPI).
                try:
                    loop = (
                        queue._loop
                        if hasattr(queue, "_loop")
                        else asyncio.get_running_loop()
                    )
                    loop.call_soon_threadsafe(queue.put_nowait, message)
                except RuntimeError:
                    # No running event loop or other issue
                    pass
