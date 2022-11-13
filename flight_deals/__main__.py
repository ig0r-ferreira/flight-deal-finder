from flight_deals.data_manager import DataManager
from flight_deals.flight_search import FlightSearch
from flight_deals.settings import get_settings


def fill_iata_code_column(
    data_manager: DataManager, flight_search: FlightSearch
) -> None:
    sheet_name = 'prices'
    rows = data_manager.get_rows_from_sheet(sheet_name) or []

    for row in rows:
        if row['iataCode']:
            continue

        iata_code = flight_search.get_iata_code_by_city_name(row['city'])
        row['iataCode'] = iata_code

        data_manager.update_sheet_row(sheet_name, row['id'], {'price': row})


def main() -> None:
    settings = get_settings()

    data_manager = DataManager(
        spreadsheet_url=settings.SHEET_API.SPREADSHEET_URL,
        auth=settings.SHEET_API.AUTH,
    )
    flight_search = FlightSearch(
        base_url=settings.FLIGHT_API.BASE_URL,
        api_key=settings.FLIGHT_API.KEY,
    )

    fill_iata_code_column(data_manager, flight_search)


if __name__ == '__main__':
    main()
