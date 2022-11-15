from typing import Any
from urllib.parse import urljoin

import requests
from pydantic import (
    BaseModel,
    HttpUrl,
    PositiveInt,
    SecretStr,
    validate_arguments,
)


class FlightSearchParams(BaseModel):
    fly_from: str
    fly_to: str
    date_from: str
    date_to: str
    curr: str
    nights_in_dst_from: PositiveInt = 7
    nights_in_dst_to: PositiveInt = 14
    flight_type: str = 'round'
    price_from: PositiveInt | None = None
    price_to: PositiveInt | None = None
    limit: PositiveInt = 100


class FlightSearch:
    """This class is responsible for talking to the Flight Search API."""

    @validate_arguments
    def __init__(self, base_url: HttpUrl, api_key: SecretStr) -> None:
        self.base_url = base_url
        self.api_key = api_key

    @property
    def headers(self) -> dict[str, Any]:
        return {
            'apikey': self.api_key.get_secret_value(),
            'Content-Type': 'application/json',
        }

    @validate_arguments
    def get_iata_code_by_city_name(self, city_name: str) -> str:
        params: dict[str, int | str] = {
            'term': city_name,
            'location_types': 'city',
            'limit': 1,
        }
        response = requests.get(
            url=urljoin(self.base_url, 'locations/query'),
            headers=self.headers,
            params=params,
        )
        response.raise_for_status()

        locations = response.json().get('locations')
        if (
            not locations
            or locations[0].get('name', '').lower() != city_name.lower()
        ):
            return ''

        return locations[0].get('code', '')

    @validate_arguments
    def search_flights(
        self, flight_params: FlightSearchParams
    ) -> dict[str, Any]:
        response = requests.get(
            url=urljoin(self.base_url, 'v2/search'),
            headers=self.headers,
            params=flight_params.dict(),
        )
        response.raise_for_status()

        data = response.json().get('data', [])

        return data
