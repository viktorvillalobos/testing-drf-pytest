# Create your views here.
from rest_framework.viewsets import ModelViewSet

from garage.models import Car
from garage.serializers import CarSerializer


class CarViewSet(ModelViewSet):
    serializer_class = CarSerializer
    queryset = Car.objects.all()
