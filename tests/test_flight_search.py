from datetime import date, timedelta
from urllib.parse import urljoin

import pytest
from pydantic import HttpUrl, SecretStr, parse_obj_as
from requests_mock import Mocker

from flight_deals.flight_search import FlightSearch, FlightSearchParams
from flight_deals.settings import get_settings


@pytest.fixture
def flight_search() -> FlightSearch:
    settings = get_settings()
    settings.FLIGHT_API.BASE_URL = parse_obj_as(
        HttpUrl, 'https://flightapi.com/'
    )
    settings.FLIGHT_API.KEY = parse_obj_as(SecretStr, '12345')

    return FlightSearch(settings.FLIGHT_API.BASE_URL, settings.FLIGHT_API.KEY)


def test_iata_code_is_par_when_city_name_is_paris(
    flight_search: FlightSearch, requests_mock: Mocker
) -> None:
    city_name = 'Paris'

    requests_mock.get(
        url=urljoin(flight_search.base_url, 'locations/query'),
        headers=flight_search.headers,
        json={'locations': [{'name': city_name, 'code': 'PAR'}]},
    )
    iata_code = flight_search.get_iata_code_by_city_name(city_name)

    assert iata_code == 'PAR'


def test_iata_code_is_empty_str_when_the_city_is_not_found(
    flight_search: FlightSearch, requests_mock: Mocker
) -> None:
    requests_mock.get(
        url=urljoin(flight_search.base_url, 'locations/query'),
        headers=flight_search.headers,
        json={'locations': []},
    )
    iata_code = flight_search.get_iata_code_by_city_name('xyz')

    assert iata_code == ''


def test_search_flights_must_return_a_list(
    flight_search: FlightSearch,
    requests_mock: Mocker,
) -> None:

    search_params = FlightSearchParams(
        fly_from='SSA',
        fly_to='NYC',
        date_from=f'{date.today() + timedelta(days=1):%d/%m/%Y}',
        date_to=f'{date.today() + timedelta(days=180):%d/%m/%Y}',
        curr='BRL',
        price_to=10_000,
    )

    requests_mock.get(
        url=urljoin(flight_search.base_url, 'v2/search'),
        headers=flight_search.headers,
        json={'data': [{'id': '123456'}]},
    )
    result = flight_search.search_flights(search_params)

    assert isinstance(result, list)
