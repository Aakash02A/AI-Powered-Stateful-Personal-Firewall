import time
from analytics.scheduler import JobScheduler


def test_scheduler():
    scheduler = JobScheduler()
    test_val = [0]

    def my_job():
        test_val[0] += 1

    scheduler.register_job(my_job, interval_seconds=1)
    scheduler.start()

    # Wait for interval to trigger
    time.sleep(1.5)
    scheduler.stop()

    assert test_val[0] >= 1
