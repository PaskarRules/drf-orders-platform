import time

from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):
    help = "Wait for the database to be available"

    def add_arguments(self, parser):
        parser.add_argument(
            "--timeout",
            type=int,
            default=30,
            help="Timeout in seconds (default: 30)",
        )

    def handle(self, *args, **options):
        timeout = options["timeout"]
        start = time.monotonic()
        self.stdout.write("Waiting for database...")

        while True:
            try:
                db_conn = connections["default"]
                db_conn.ensure_connection()
                self.stdout.write(self.style.SUCCESS("Database available!"))
                return
            except OperationalError:
                elapsed = time.monotonic() - start
                if elapsed >= timeout:
                    self.stdout.write(self.style.ERROR("Database unavailable after timeout"))
                    raise
                time.sleep(1)
