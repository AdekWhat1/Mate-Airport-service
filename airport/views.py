from datetime import datetime

from django.db.models import F, Count
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from airport.models import (
    Airport,
    Route,
    AirplaneType,
    Airplane,
    Crew, Flight,
    Order,
    Ticket
)
from airport.serializers import (
    AirportSerializer,
    RouteSerializer,
    AirplaneTypeSerializer,
    AirplaneSerializer,
    FlightSerializer,
    OrderSerializer,
    CrewSerializer,
    RouteListSerializer,
    AirplaneListSerializer,
    FlightListSerializer,
    FlightDetailSerializer,
    OrderListSerializer, AirplaneImageSerializer
)


class OrderPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100

class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer

    def get_queryset(self):
        queryset = self.queryset
        name = self.request.query_params.get("name")
        closest_big_city = self.request.query_params.get("closest_big_city")

        if name:
            queryset = queryset.filter(name__icontains=name)
        if closest_big_city:
            queryset = queryset.filter(closest_big_city__icontains=closest_big_city)

        return queryset


@extend_schema_view(
    list=extend_schema(
        summary="List routes",
        description="Retrieve all routes with optional filtering by source or destination airport.",
        parameters=[
            OpenApiParameter(
                name="source",
                type=OpenApiTypes.STR,
                description="Filter by source airport name",
            ),
            OpenApiParameter(
                name="destination",
                type=OpenApiTypes.STR,
                description="Filter by destination airport name",
            ),
        ],
    )
)
class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.select_related("source", "destination")
    serializer_class = RouteSerializer

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return RouteListSerializer
        return RouteSerializer

    def get_queryset(self):
        queryset = self.queryset
        source = self.request.query_params.get("source")
        destination = self.request.query_params.get("destination")

        if source:
            queryset = queryset.filter(source__name__icontains=source)
        if destination:
            queryset = queryset.filter(destination__name__icontains=destination)

        return queryset


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneListSerializer
        if self.action == "upload_image":
            return AirplaneImageSerializer
        return AirplaneSerializer

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAdminUser],
    )
    def upload_image(self, request, pk=None):
        airplane = self.get_object()
        serializer = self.get_serializer(airplane, data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


@extend_schema_view(
    list=extend_schema(
        summary="List flights",
        description="Retrieve all flights with optional filtering by departure/arrival city and date.",
        parameters=[
            OpenApiParameter(
                name="from",
                type=OpenApiTypes.STR,
                description="Filter by departure city name (case-insensitive)",
            ),
            OpenApiParameter(
                name="to",
                type=OpenApiTypes.STR,
                description="Filter by destination city name (case-insensitive)",
            ),
            OpenApiParameter(
                name="date",
                type=OpenApiTypes.DATE,
                description="Filter by departure date (format: YYYY-MM-DD)",
            ),
        ],
    )
)
class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer

    def get_queryset(self):
        queryset = self.queryset

        if self.action == "list":
            queryset = (
                queryset
                .select_related("route__source", "route__destination", "airplane")
                .annotate(
                    tickets_available=(
                            F("airplane__rows") * F("airplane__seats_in_row")
                            - Count("tickets")
                    )
                )
            )

        if self.action == "retrieve":
            queryset = (
                queryset
                .select_related("route__source", "route__destination", "airplane__airplane_type")
                .prefetch_related("crew", "tickets")
            )

        from_city = self.request.query_params.get("from")
        to_city = self.request.query_params.get("to")
        departure_date = self.request.query_params.get("date")

        if from_city:
            queryset = queryset.filter(route__source__name__icontains=from_city)
        if to_city:
            queryset = queryset.filter(route__destination__name__icontains=to_city)
        if departure_date:
            date_obj = datetime.strptime(departure_date, "%Y-%m-%d").date()
            queryset = queryset.filter(departure_time__date=date_obj)

        return queryset.order_by("id")

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        if self.action == "retrieve":
            return FlightDetailSerializer
        return FlightSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.prefetch_related(
        "tickets__flight__route__source",
        "tickets__flight__route__destination",
        "tickets__flight__airplane",
    )
    serializer_class = OrderSerializer
    pagination_class = OrderPagination
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return OrderListSerializer
        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)