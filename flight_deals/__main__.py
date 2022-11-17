from datetime import date, timedelta

from flight_deals.data_manager import DataManager
from flight_deals.flight_data import FlightItinerary
from flight_deals.flight_search import FlightSearch, FlightSearchParams
from flight_deals.settings import get_settings


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

    sheet_name = 'prices'
    destinations = data_manager.get_rows_from_sheet(sheet_name)

    tomorrow = f'{date.today() + timedelta(days=1):%d/%m/%Y}'
    six_months_from_now = f'{date.today() + timedelta(days=180):%d/%m/%Y}'

    flights_to_notify = []
    for destination in destinations:

        destination_code = flight_search.get_iata_code_by_city_name(
            destination['city']
        )
        if not destination_code:
            continue

        available_itineraries = flight_search.search_flights(
            flight_params=FlightSearchParams(
                fly_from='SSA',
                fly_to=destination_code,
                date_from=tomorrow,
                date_to=six_months_from_now,
                curr='BRL',
                price_to=destination['lowestPrice'],
                max_stopovers=2,
            )
        )
        if not available_itineraries:
            continue

        flights_to_notify.append(
            FlightItinerary.parse_obj(available_itineraries[0])
        )

    print(flights_to_notify)


if __name__ == '__main__':
    main()
