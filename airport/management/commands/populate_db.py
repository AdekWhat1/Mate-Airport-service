from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone

from airport.models import (
    Airplane,
    AirplaneType,
    Airport,
    Crew,
    Flight,
    Route,
)


class Command(BaseCommand):
    help = "Populates the database with initial test data for Airport service"

    def handle(self, *args, **options):
        self.stdout.write("Starting database seeding...")

        # 1. Створення аеропортів
        kbp = Airport.objects.create(name="Boryspil International Airport", closest_big_city="Kyiv")
        lhr = Airport.objects.create(name="Heathrow Airport", closest_big_city="London")
        jfk = Airport.objects.create(name="John F. Kennedy International Airport", closest_big_city="New York")
        cdg = Airport.objects.create(name="Charles de Gaulle Airport", closest_big_city="Paris")

        # 2. Створення маршрутів
        route_kbp_lhr = Route.objects.create(source=kbp, destination=lhr, distance=2134)
        route_lhr_jfk = Route.objects.create(source=lhr, destination=jfk, distance=5541)
        route_cdg_kbp = Route.objects.create(source=cdg, destination=kbp, distance=2025)

        # 3. Створення типів та літаків
        boeing_type = AirplaneType.objects.create(name="Boeing 737")
        airbus_type = AirplaneType.objects.create(name="Airbus A320")

        plane_1 = Airplane.objects.create(name="SkyLiner-01", rows=20, seats_in_row=6, airplane_type=boeing_type)
        plane_2 = Airplane.objects.create(name="AeroJet-02", rows=25, seats_in_row=6, airplane_type=airbus_type)

        # 4. Створення екіпажу
        crew_1 = Crew.objects.create(first_name="John", last_name="Doe")
        crew_2 = Crew.objects.create(first_name="Jane", last_name="Smith")
        crew_3 = Crew.objects.create(first_name="Taras", last_name="Shevchenko")

        # 5. Створення рейсів
        now = timezone.now()

        flight_1 = Flight.objects.create(
            route=route_kbp_lhr,
            airplane=plane_1,
            departure_time=now + timedelta(days=1, hours=2),
            arrival_time=now + timedelta(days=1, hours=5, minutes=30),
        )
        flight_1.crew.set([crew_1, crew_2])

        flight_2 = Flight.objects.create(
            route=route_lhr_jfk,
            airplane=plane_2,
            departure_time=now + timedelta(days=2, hours=4),
            arrival_time=now + timedelta(days=2, hours=12),
        )
        flight_2.crew.set([crew_2, crew_3])

        flight_3 = Flight.objects.create(
            route=route_cdg_kbp,
            airplane=plane_1,
            departure_time=now + timedelta(days=3, hours=1),
            arrival_time=now + timedelta(days=3, hours=4),
        )
        flight_3.crew.set([crew_1, crew_3])

        self.stdout.write(self.style.SUCCESS("Database successfully populated with sample data!"))