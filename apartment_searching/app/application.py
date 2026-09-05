# This file manages the application lifecycle.
# It starts long-lived components such as apartment sources
# and runs the monitoring worker.

from app.monitoring import ApartmentListingMonitor, MonitoringWorker
from app.sources.saga import SagaSource


class Application:
    """Manage the lifecycle of the apartment monitoring application."""

    def __init__(
        self,
        source: SagaSource,
        monitor: ApartmentListingMonitor,
        worker: MonitoringWorker,
    ):
        self.source = source
        self.monitor = monitor
        self.worker = worker

    def run(self) -> None:
        """Start components and run monitoring."""

        print("[APP] Starting SAGA source...")
        self.source.start()
        print("[APP] SAGA source started.")

        try:
            print("[APP] Starting monitoring worker...")
            self.worker.run()

        finally:
            self.source.close()

    def stop(self) -> None:
        """Stop the monitoring worker."""

        self.worker.stop()