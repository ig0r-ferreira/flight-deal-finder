import pytest
from requests.exceptions import HTTPError

from flight_deals.data_manager import DataManager
from flight_deals.settings import SheetAPISettings

SHEET_API_SETTINGS = SheetAPISettings()


def test_get_rows_from_non_existent_sheet() -> None:
    with pytest.raises(HTTPError):
        api = DataManager(spreadsheet_url=SHEET_API_SETTINGS.SPREADSHEET_URL)
        api.get_rows_from_sheet('non-existent-sheet')


def test_get_rows_from_prices_sheet_should_return_an_list_of_dicts_or_None() -> None:
    api = DataManager(spreadsheet_url=SHEET_API_SETTINGS.SPREADSHEET_URL)
    data = api.get_rows_from_sheet('prices')

    assert (
        data is None
        or isinstance(data, list)
        and all(isinstance(row, dict) for row in data)
    )
