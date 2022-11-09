from typing import Callable

import pytest
from mypy_extensions import DefaultArg
from pydantic import HttpUrl, SecretStr, parse_obj_as
from requests.exceptions import HTTPError
from requests_mock import Mocker

from flight_deals.data_manager import DataManager

TEST_URL: str = 'https://myapi.com/projects/mysheet/'
TEST_AUTH: str = 'Bearer 123456'
TEST_SHEET_NAME = 'example'
DataManagerFactory = Callable[[str, DefaultArg(str | None, None)], DataManager]


@pytest.fixture
def make_data_manager() -> DataManagerFactory:
    def _make_data_manager(url: str, auth: str | None = None) -> DataManager:
        return DataManager(
            spreadsheet_url=parse_obj_as(HttpUrl, url),
            auth=SecretStr(auth) if auth is not None else auth,
        )

    return _make_data_manager


def test_data_manager_add_slash_at_end_of_url_when_started_without_trailing_slash(
    make_data_manager: DataManagerFactory,
) -> None:
    data_manager = make_data_manager(TEST_URL.strip('/'), TEST_AUTH)

    assert data_manager.spreadsheet_url.endswith('/')


def test_data_manager_headers_are_empty_when_started_without_authorization(
    make_data_manager: DataManagerFactory,
) -> None:
    data_manager = make_data_manager(TEST_URL)

    assert not data_manager.headers


def test_get_rows_from_sheet_with_invalid_auth_key(
    make_data_manager: DataManagerFactory, requests_mock: Mocker
) -> None:

    data_manager = make_data_manager(TEST_URL, 'invalid_auth')

    requests_mock.get(
        url=f'{data_manager.spreadsheet_url}{TEST_SHEET_NAME}',
        headers=data_manager.headers,
        status_code=401,
    )

    with pytest.raises(HTTPError) as exc_info:
        data_manager.get_rows_from_sheet(TEST_SHEET_NAME)

    assert exc_info.match('401 Client Error')


def test_get_rows_from_sheet_to_a_non_existent_sheet(
    make_data_manager: DataManagerFactory, requests_mock: Mocker
) -> None:

    data_manager = make_data_manager(TEST_URL, TEST_AUTH)
    sheet_name = 'non-existent-sheet'

    requests_mock.get(
        url=f'{data_manager.spreadsheet_url}{sheet_name}',
        headers=data_manager.headers,
        status_code=404,
    )

    with pytest.raises(HTTPError) as exc_info:
        data_manager.get_rows_from_sheet(sheet_name)

    assert exc_info.match('404 Client Error')


def test_get_rows_from_sheet_should_return_a_list_of_dicts(
    make_data_manager: DataManagerFactory, requests_mock: Mocker
) -> None:

    data_manager = make_data_manager(TEST_URL, TEST_AUTH)

    requests_mock.get(
        url=f'{data_manager.spreadsheet_url}{TEST_SHEET_NAME}',
        headers=data_manager.headers,
        status_code=200,
        json={TEST_SHEET_NAME: [{'key1': 25.50}, {'key2': 30.00}]},
    )

    rows = data_manager.get_rows_from_sheet(TEST_SHEET_NAME)

    assert isinstance(rows, list) and all(
        isinstance(row, dict) for row in rows
    )


def test_get_rows_from_sheet_should_return_none_when_response_json_is_empty_dict(
    make_data_manager: DataManagerFactory, requests_mock: Mocker
) -> None:

    data_manager = make_data_manager(TEST_URL, TEST_AUTH)

    requests_mock.get(
        url=f'{data_manager.spreadsheet_url}{TEST_SHEET_NAME}',
        headers=data_manager.headers,
        status_code=200,
        json={},
    )

    rows = data_manager.get_rows_from_sheet(TEST_SHEET_NAME)

    assert rows is None
