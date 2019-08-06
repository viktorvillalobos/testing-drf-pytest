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
        qs = MockSet(expected_results[0])
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

        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)


class TestViewSet:

    @pytest.mark.urls('garage.urls')
    def test_list(self, rf, mocker):
        url = reverse('car-list')
        request = rf.get(url)

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

        mocker.patch.object(CarViewSet, 'get_object', return_value=car)
        mocker.patch.object(Car, 'delete')

        response = CarViewSet \
            .as_view({'delete': 'destroy'})(request).render()

        assert response.status_code == 204
        assert Car.delete.called
