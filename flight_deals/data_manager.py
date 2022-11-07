from typing import Any

import requests
from pydantic import HttpUrl, parse_obj_as, validate_arguments

Row = dict[str, Any]


class DataManager:
    """This class is responsible for talking to the Google Sheet."""

    @validate_arguments
    def __init__(self, spreadsheet_url: HttpUrl) -> None:
        if not spreadsheet_url.endswith('/'):
            spreadsheet_url = parse_obj_as(HttpUrl, f'{spreadsheet_url}/')

        self.spreadsheet_url = spreadsheet_url

    @validate_arguments
    def get_rows_from_sheet(self, sheet_name: str) -> list[Row] | None:
        response = requests.get(url=f'{self.spreadsheet_url}{sheet_name}')
        response.raise_for_status()
        data = response.json()
        return (isinstance(data, dict) and data.get(sheet_name)) or None
