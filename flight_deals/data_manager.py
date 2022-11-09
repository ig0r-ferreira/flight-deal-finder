from typing import Any

import requests
from pydantic import HttpUrl, SecretStr, parse_obj_as, validate_arguments

Row = dict[str, Any]


class DataManager:
    """This class is responsible for talking to the Google Sheet."""

    @validate_arguments
    def __init__(
        self, spreadsheet_url: HttpUrl, auth: SecretStr | None = None
    ) -> None:
        if not spreadsheet_url.endswith('/'):
            spreadsheet_url = parse_obj_as(HttpUrl, f'{spreadsheet_url}/')

        self.spreadsheet_url = spreadsheet_url
        self.auth = auth

    @property
    def headers(self) -> dict[str, Any]:
        if self.auth is None:
            return {}

        return {'Authorization': self.auth.get_secret_value()}

    @validate_arguments
    def get_rows_from_sheet(self, sheet_name: str) -> list[Row] | None:
        response = requests.get(
            url=f'{self.spreadsheet_url}{sheet_name}',
            headers=self.headers,
        )
        response.raise_for_status()
        data = response.json()
        return (isinstance(data, dict) and data.get(sheet_name)) or None

    @validate_arguments
    def update_sheet_row(
        self, sheet_name: str, row_id: int, body: dict[str, Any]
    ) -> dict[str, Any]:
        response = requests.put(
            url=f'{self.spreadsheet_url}{sheet_name}/{row_id}',
            headers=self.headers,
            json=body,
        )
        response.raise_for_status()
        return response.json()
