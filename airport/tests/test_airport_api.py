from datetime import timedelta
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Airplane, AirplaneType, Airport, Flight, Order, Route, Ticket, Crew

FLIGHTS_URL = reverse("airport:flight-list")
ORDERS_URL = reverse("airport:order-list")


def sample_airport(**params) -> Airport:
    defaults = {
        "name": "Boryspil",
        "closest_big_city": "Kyiv",
    }
    defaults.update(params)
    return Airport.objects.create(**defaults)


def sample_airplane(**params) -> Airplane:
    airplane_type = params.pop("airplane_type", None)
    if not airplane_type:
        airplane_type = AirplaneType.objects.create(name="Boeing 737")

    defaults = {
        "name": "Sky-01",
        "rows": 10,
        "seats_in_row": 6,
        "airplane_type": airplane_type,
    }
    defaults.update(params)
    return Airplane.objects.create(**defaults)


def sample_flight(**params) -> Flight:
    if "route" not in params:
        source = sample_airport(name="Source Airport")
        destination = sample_airport(name="Destination Airport")
        params["route"] = Route.objects.create(
            source=source, destination=destination, distance=1000
        )
    if "airplane" not in params:
        params["airplane"] = sample_airplane()

    now = timezone.now()
    defaults = {
        "departure_time": now + timedelta(days=1),
        "arrival_time": now + timedelta(days=1, hours=3),
    }
    defaults.update(params)
    return Flight.objects.create(**defaults)


class UnauthenticatedAirportApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required_for_orders(self):
        res = self.client.get(ORDERS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_auth_required_for_flights(self):
        sample_flight()
        res = self.client.get(FLIGHTS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAirportApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@user.com",
            password="password123",
        )
        self.client.force_authenticate(self.user)

    def test_flights_list_tickets_available_calculation(self):
        flight = sample_flight()
        order = Order.objects.create(user=self.user)
        Ticket.objects.create(row=1, seat=1, flight=flight, order=order)

        res = self.client.get(FLIGHTS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        results = res.data["results"] if isinstance(res.data, dict) and "results" in res.data else res.data
        expected_available = flight.airplane.capacity - 1
        self.assertEqual(results[0]["tickets_available"], expected_available)

    def test_filter_flights_by_source_city(self):
        kbp = sample_airport(name="Boryspil", closest_big_city="Kyiv")
        lhr = sample_airport(name="Heathrow", closest_big_city="London")
        route1 = Route.objects.create(source=kbp, destination=lhr, distance=2000)
        route2 = Route.objects.create(source=lhr, destination=kbp, distance=2000)

        flight_kbp = sample_flight(route=route1)
        sample_flight(route=route2)

        res = self.client.get(FLIGHTS_URL, {"from": "Boryspil"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        results = res.data["results"] if isinstance(res.data, dict) and "results" in res.data else res.data
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], flight_kbp.id)

    def test_ticket_validation_out_of_bounds(self):
        airplane = sample_airplane(rows=10, seats_in_row=6)
        flight = sample_flight(airplane=airplane)

        payload = {
            "tickets": [
                {"row": 11, "seat": 1, "flight": flight.id},
            ]
        }
        res = self.client.post(ORDERS_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_regular_user_cannot_create_flight(self):
        route = Route.objects.create(
            source=sample_airport(name="A1"),
            destination=sample_airport(name="A2"),
            distance=500,
        )
        airplane = sample_airplane()
        payload = {
            "route": route.id,
            "airplane": airplane.id,
            "departure_time": timezone.now() + timedelta(days=1),
            "arrival_time": timezone.now() + timedelta(days=1, hours=2),
            "crew": [],
        }
        res = self.client.post(FLIGHTS_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirportApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = get_user_model().objects.create_superuser(
            email="admin@airport.com",
            password="adminpassword123",
        )
        self.client.force_authenticate(self.admin)

    def test_admin_can_create_flight(self):
        route = Route.objects.create(
            source=sample_airport(name="Src"),
            destination=sample_airport(name="Dst"),
            distance=800,
        )
        airplane = sample_airplane()
        crew = Crew.objects.create(first_name="John", last_name="Doe")

        now = timezone.now()
        payload = {
            "route": route.id,
            "airplane": airplane.id,
            "departure_time": (now + timedelta(days=2)).isoformat(),
            "arrival_time": (now + timedelta(days=2, hours=4)).isoformat(),
            "crew": [crew.id],
        }
        res = self.client.post(FLIGHTS_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED, res.data)
        flight = Flight.objects.get(id=res.data["id"])
        self.assertIn(crew, flight.crew.all())