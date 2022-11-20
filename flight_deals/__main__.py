from datetime import date, timedelta
from smtplib import SMTP

from flight_deals.data_manager import DataManager
from flight_deals.email_client import EmailClient, make_message
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
    email_client = EmailClient(
        smtp_server=SMTP(
            host=f'{settings.SMTP_SERVER.HOST}:{settings.SMTP_SERVER.PORT}'
        ),
        credentials=(
            settings.SMTP_SERVER.USERNAME.get_secret_value(),
            settings.SMTP_SERVER.PASSWORD.get_secret_value(),
        ),
    )

    sheet_name = 'prices'
    destinations = data_manager.get_rows_from_sheet(sheet_name)

    tomorrow = f'{date.today() + timedelta(days=1):%d/%m/%Y}'
    six_months_from_now = f'{date.today() + timedelta(days=180):%d/%m/%Y}'

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

        flight = FlightItinerary.parse_obj(available_itineraries[0])

        email_client.send_message(
            make_message(
                from_address=settings.EMAIL.SENDER,
                to_address=settings.EMAIL.RECIPIENTS,
                subject=(
                    'Low price alert! Flight from '
                    f'{flight.departure_city} to {flight.destination_city}'
                ),
                body=str(flight),
            )
        )


if __name__ == '__main__':
    main()
