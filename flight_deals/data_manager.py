import posixpath
from typing import Any
from urllib.parse import urljoin

import requests
from pydantic import HttpUrl, SecretStr, validate_arguments

Row = dict[str, Any]


class DataManager:
    """This class is responsible for talking to the Google Sheet."""

    @validate_arguments
    def __init__(
        self, spreadsheet_url: HttpUrl, auth: SecretStr | None = None
    ) -> None:
        self.spreadsheet_url = spreadsheet_url
        self.auth = auth

    @property
    def headers(self) -> dict[str, Any]:
        if self.auth is None:
            return {}

        return {'Authorization': self.auth.get_secret_value()}

    @validate_arguments
    def get_rows_from_sheet(self, sheet_name: str) -> list[Row]:
        response = requests.get(
            url=urljoin(self.spreadsheet_url, sheet_name),
            headers=self.headers,
        )
        response.raise_for_status()
        return response.json().get(sheet_name, [])

    @validate_arguments
    def update_sheet_row(
        self, sheet_name: str, row_id: int, body: dict[str, Any]
    ) -> dict[str, Any]:
        response = requests.put(
            url=urljoin(
                self.spreadsheet_url, posixpath.join(sheet_name, str(row_id))
            ),
            headers=self.headers,
            json=body,
        )
        response.raise_for_status()
        return response.json()
