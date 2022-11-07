from typing import Any
from unittest.mock import Mock

import pytest
from pydantic import HttpUrl, parse_obj_as
from requests.exceptions import HTTPError

from flight_deals.data_manager import DataManager

TEST_URL: str = 'https://myapi.com/projects/mysheet/'


@pytest.fixture
def fake_data_manager() -> DataManager:
    return DataManager(spreadsheet_url=parse_obj_as(HttpUrl, TEST_URL))


def test_receive_spreadsheet_url_without_slash_at_the_end_and_add_slash() -> None:
    data_manager = DataManager(
        spreadsheet_url=parse_obj_as(HttpUrl, TEST_URL.strip('/'))
    )
    assert data_manager.spreadsheet_url.endswith('/')


def test_get_rows_from_non_existent_sheet(
    fake_data_manager: DataManager, mocker: Mock
) -> None:
    mocker.patch('requests.get', side_effect=HTTPError)
    with pytest.raises(HTTPError):
        fake_data_manager.get_rows_from_sheet('non-existent-sheet')


def test_get_rows_from_prices_sheet_should_return_an_list_of_dicts(
    fake_data_manager: DataManager, mocker: Mock
) -> None:
    def json_as_dict() -> dict[str, Any]:
        return {'prices': [{'key1': 25.50}, {'key2': 30.00}]}

    mock_requests = mocker.patch('requests.get')
    mock_requests.return_value.json = json_as_dict

    rows = fake_data_manager.get_rows_from_sheet('prices')

    assert isinstance(rows, list) and all(
        isinstance(row, dict) for row in rows
    )


def test_get_rows_from_prices_sheet_should_return_none_if_json_response_for_none(
    fake_data_manager: DataManager, mocker: Mock
) -> None:
    def json_as_none() -> None:
        return None

    mock_requests = mocker.patch('requests.get')
    mock_requests.return_value.json = json_as_none

    rows = fake_data_manager.get_rows_from_sheet('prices')

    assert rows is None
