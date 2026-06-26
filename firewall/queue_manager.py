import queue

class QueueManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(QueueManager, cls).__new__(cls)
            cls._instance.q = queue.Queue()
        return cls._instance

    def push(self, item):
        self.q.put(item)
        
    def pop(self, timeout=1.0):
        try:
            return self.q.get(timeout=timeout)
        except queue.Empty:
            return None
            
    def qsize(self):
        return self.q.qsize()

    def empty(self):
        return self.q.empty()
