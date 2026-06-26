import pytest
from firewall.queue_manager import QueueManager


def test_queue_singleton():
    q1 = QueueManager()
    q2 = QueueManager()
    assert q1 is q2


def test_queue_push_pop():
    q = QueueManager()
    while q.qsize() > 0:
        q.pop()

    q.push("item1")
    q.push("item2")

    assert q.qsize() == 2
    assert q.pop() == "item1"
    assert q.pop() == "item2"
    assert q.qsize() == 0
    assert q.pop(timeout=0.1) is None
