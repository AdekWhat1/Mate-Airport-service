import time
from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError
from psycopg2 import OperationalError as Psycopg2OpError


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write("Waiting for database...")
        db_conn = None
        while not db_conn:
            try:
                db_conn = connections["default"]
                db_conn.cursor()
            except (Psycopg2OpError, OperationalError):
                self.stdout.write("Database unavailable, waiting 1 s")
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS("Database available!"))