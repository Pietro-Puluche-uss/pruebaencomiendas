import time

from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):
    help = "Waits until the default database is available."

    def handle(self, *args, **options):
        self.stdout.write("Waiting for database...")

        while True:
            try:
                connection = connections["default"]
                connection.ensure_connection()
                break
            except OperationalError:
                self.stdout.write("Database unavailable, retrying in 2 seconds...")
                time.sleep(2)

        self.stdout.write(self.style.SUCCESS("Database is available."))
