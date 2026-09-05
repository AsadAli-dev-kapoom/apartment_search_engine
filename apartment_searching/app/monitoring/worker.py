# This file implements the monitoring worker.
# It repeatedly executes the monitoring service at a configured interval
# and supports graceful shutdown.

import time

from app.monitoring.service import MonitoringService


class MonitoringWorker:
    """Repeatedly execute the monitoring service."""

    def __init__(
        self,
        service: MonitoringService,
        interval_seconds: int = 300,
    ):
        self.service = service
        self.interval_seconds = interval_seconds
        self._running = False

    def run_once(self) -> None:
        """Run one monitoring cycle."""

        self.service.check()

    def run(self) -> None:
        """Run monitoring continuously."""
        print("[WORKER] Monitoring worker started.")

        self._running = True

        while self._running:
            self.run_once()

            if self._running:
                time.sleep(self.interval_seconds)

    def stop(self) -> None:
        """Stop the monitoring loop."""

        self._running = False
        print("[WORKER] Monitoring worker stopped.")