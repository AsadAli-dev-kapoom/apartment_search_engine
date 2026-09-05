# This file is the application entry point.
# It loads configuration and wires together the source, storage,
# monitoring, notification, and application lifecycle components.

from app.application import Application
from app.config import load_settings
from app.monitoring import (
    ApartmentListingMonitor,
    MonitoringService,
    MonitoringWorker,
)
from app.notifications.email import EmailNotificationService
from app.sources.saga import SagaSource
from app.storage.sqlite import SQLiteListingRepository


def create_application() -> Application:
    """Create and wire the application components."""

    settings = load_settings()

    source = SagaSource(
        url=settings.saga_url,
        headless=False,
    )

    repository = SQLiteListingRepository(
        settings.database_path
    )

    monitor = ApartmentListingMonitor(
        source=source,
        repository=repository,
    )
    # if settings.bootstrap_mode:
    #     print("[APP] Bootstrap mode enabled.")
    #     monitor.bootstrap()
    #     print("[APP] Existing listings stored.")

    notification_service = EmailNotificationService(
        api_key=settings.email_api_key,
        sender=settings.email_from,
        recipient=settings.notification_recipient,
    )   

    service = MonitoringService(
        monitor=monitor,
        notification_service=notification_service,
    )

    worker = MonitoringWorker(
        service=service,
        interval_seconds=settings.monitoring_interval_seconds,
    )

    return Application(
        source=source,
        monitor=monitor,
        worker=worker,
        # bootstrap_mode=settings.bootstrap_mode,

    )


def main() -> None:
    """Start the apartment monitoring application."""

    application = create_application()

    try:
        application.run()
    except KeyboardInterrupt:
        print("\n[APP] Shutting down...")
        application.stop()


if __name__ == "__main__":
    main()