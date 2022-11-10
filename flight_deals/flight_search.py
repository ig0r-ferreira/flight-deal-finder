from typing import Any

import requests
from pydantic import HttpUrl, SecretStr, validate_arguments


class FlightSearch:
    # This class is responsible for talking to the Flight Search API.
    @validate_arguments
    def __init__(self, base_url: HttpUrl, api_key: SecretStr) -> None:
        self.base_url = base_url
        self.api_key = api_key

    @property
    def headers(self) -> dict[str, Any]:
        return {'apikey': self.api_key.get_secret_value()}

    @validate_arguments
    def get_iata_code_by_city_name(self, city_name: str) -> str:
        params: dict[str, int | str] = {
            'term': city_name,
            'location_types': 'city',
            'limit': 1,
        }
        response = requests.get(
            url=f'{self.base_url}locations/query',
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
