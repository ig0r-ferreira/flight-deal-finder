import pytest
from pydantic import HttpUrl, SecretStr, parse_obj_as
from requests_mock import Mocker

from flight_deals.flight_search import FlightSearch

TEST_URL: str = 'https://flightapi.com/'
TEST_API_KEY: str = '12345'


@pytest.fixture
def flight_search() -> FlightSearch:
    return FlightSearch(
        parse_obj_as(HttpUrl, TEST_URL), SecretStr(TEST_API_KEY)
    )


def test_iata_code_is_par_when_city_name_is_paris(
    flight_search: FlightSearch, requests_mock: Mocker
) -> None:
    city_name = 'Paris'

    requests_mock.get(
        url=f'{flight_search.base_url}locations/query',
        headers=flight_search.headers,
        json={'locations': [{'name': city_name, 'code': 'PAR'}]},
    )
    iata_code = flight_search.get_iata_code_by_city_name(city_name)

    assert iata_code == 'PAR'


def test_iata_code_is_empty_str_when_the_city_is_not_found(
    flight_search: FlightSearch, requests_mock: Mocker
) -> None:
    requests_mock.get(
        url=f'{flight_search.base_url}locations/query',
        headers=flight_search.headers,
        json={'locations': []},
    )
    iata_code = flight_search.get_iata_code_by_city_name('xyz')

    assert iata_code == ''
