# This file tests the monitoring worker.
# It verifies that the worker executes the monitoring service
# without testing the continuous infinite loop.

from app.monitoring.service import MonitoringService
from app.monitoring.worker import MonitoringWorker


class FakeMonitoringService:
    """Test service that records whether it was executed."""

    def __init__(self):
        self.check_count = 0

    def check(self):
        self.check_count += 1


def test_worker_runs_one_check():

    service = FakeMonitoringService()

    worker = MonitoringWorker(
        service=service,
        interval_seconds=300,
    )

    worker.run_once()

    assert service.check_count == 1