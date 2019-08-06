import datetime
import json
from time import strftime

import pytest
from django.urls import reverse
from django_mock_queries.query import MockSet
from rest_framework.exceptions import ValidationError

from garage.models import Car
from garage.serializers import CarSerializer
from garage.views import CarViewSet


class TestCarManager:

    def test_get_cars_by_created(self, mocker):
        expected_results = [
            Car(name='Ferrari',
                code='fr1',
                year=2019,
                created=datetime.datetime.now(),
                modified=datetime.datetime.now())
        ]

        date = strftime('%Y-%m-%d')
        # django-mock-queries nos permite crear Mock QuerySets
        # para omitir el acceso a BD
        qs = MockSet(expected_results[0])

        # Patch el metodo qet_queryset para modificar su comportamiento
        # y que nos retorne nuestro queryset  y asi omitir el acceso
        # a BD
        mocker.patch.object(Car.objects, 'get_queryset', return_value=qs)

        result = list(Car.objects.get_cars_by_created(date))

        assert result == expected_results
        assert str(result[0]) == expected_results[0].code


class TestCarSerializer:

    def test_expected_serialized_json(self):
        expected_results = {
            'id': 1,
            'name': 'Ferrari',
            'code': 'fr1',
            'year': 2019,
            'created': str(datetime.datetime.now()),
            'modified': str(datetime.datetime.now())
        }

        car = Car(**expected_results)

        results = CarSerializer(car).data

        assert results == expected_results

    def test_raise_error_when_missing_required_field(self):
        incomplete_data = {
            'name': 'Ferrari',
            'code': 'fr1',
            'created': str(datetime.datetime.now()),
            'modified': str(datetime.datetime.now())
        }

        serializer = CarSerializer(data=incomplete_data)

        # Este ContextManager nos permite verificar que
        # se ejecute correctamente una Excepcion
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)


class TestViewSet:

    @pytest.mark.urls('garage.urls')
    def test_list(self, rf, mocker):
        #  django-pytest nos permite pasar por inyeccion de dependencia
        # a nuestros tests algunos objetos, en este caso le "INYECTE"
        # el objeto rf que no es mas que el comun RequestFactory
        # y mocker que nos permite hacer patch a objetos y funciones
        url = reverse('car-list')
        request = rf.get(url)

        # usamos la libreria django-mock-queries para crear un Mock
        # de nuestro queryset y omitir el acceso a BD

        queryset = MockSet(
            Car(name='Ferrari', code='fr1', year=2019),
            Car(name='Ferrari', code='fr1', year=2019)
        )

        mocker.patch.object(CarViewSet, 'get_queryset', return_value=queryset)
        response = CarViewSet.as_view({'get': 'list'})(request).render()

        assert response.status_code == 200
        assert len(json.loads(response.content)) == 2

    @pytest.mark.urls('garage.urls')
    def test_create(self, rf, mocker):
        url = reverse('car-list')

        data = {
            'name': 'Ferrari',
            'code': 'fr1',
            'year': 2019
        }

        request = rf.post(url,
                          content_type='application/json',
                          data=json.dumps(data))

        mocker.patch.object(Car, 'save')
        response = CarViewSet.as_view({'post': 'create'})(request).render()
        assert response.status_code == 201
        assert json.loads(response.content).get('name') == 'Ferrari'
        # Verificamos si efectivamente se llamo el metodo save
        assert Car.save.called

    @pytest.mark.urls('garage.urls')
    def test_update(self, rf, mocker):
        url = reverse('car-detail', kwargs={'pk': 1})
        request = rf.patch(url,
                           content_type='application/json',
                           data=json.dumps({'name': 'Enzo'}))
        car = Car(name='Ferrari',
                  code='fr1',
                  id=1,
                  year=2019,
                  created=datetime.datetime.now(),
                  modified=datetime.datetime.now())

        # Patch al metodo get_object de nuestro ViewSet para
        # para omitir el acceso a BD
        # Lo mismo para el motodo save() de nuestro modelo Car

        mocker.patch.object(CarViewSet, 'get_object', return_value=car)
        mocker.patch.object(Car, 'save')

        response = CarViewSet \
            .as_view({'patch': 'partial_update'})(request).render()

        assert response.status_code == 200
        assert json.loads(response.content).get('name') == 'Enzo'
        assert Car.save.called

    @pytest.mark.urls('garage.urls')
    def test_delete(self, rf, mocker):
        url = reverse('car-detail', kwargs={'pk': 1})
        request = rf.delete(url)

        car = Car(name='Ferrari',
                  code='fr1',
                  id=1,
                  year=2019,
                  created=datetime.datetime.now(),
                  modified=datetime.datetime.now())

        # De nuevo hacemos patch al metodo get_object
        # y tambien al delete del objeto.
        mocker.patch.object(CarViewSet, 'get_object', return_value=car)
        mocker.patch.object(Car, 'delete')

        response = CarViewSet \
            .as_view({'delete': 'destroy'})(request).render()

        assert response.status_code == 204
        assert Car.delete.called
