from datetime import date, timedelta
from smtplib import SMTP

from flight_deals.controller import (
    find_cheap_flights,
    notify,
    update_destination_codes,
)
from flight_deals.data_manager import DataManager
from flight_deals.email_client import EmailClient
from flight_deals.flight_search import FlightSearch
from flight_deals.settings import EMAIL, FLIGHT_API, SHEET_API, SMTP_SERVER
from flight_deals.sheet_api import SheetAPI


def main() -> None:
    sheet_api = SheetAPI(
        spreadsheet_url=SHEET_API.SPREADSHEET_URL,
        auth=SHEET_API.AUTH,
    )
    flight_search = FlightSearch(
        base_url=FLIGHT_API.BASE_URL,
        api_key=FLIGHT_API.KEY,
    )
    email_client = EmailClient(
        smtp_server=SMTP(host=f'{SMTP_SERVER.HOST}:{SMTP_SERVER.PORT}'),
        credentials=(
            SMTP_SERVER.USERNAME.get_secret_value(),
            SMTP_SERVER.PASSWORD.get_secret_value(),
        ),
    )

    destinations = DataManager('prices', sheet_api)
    destinations.load_data()
    update_destination_codes(
        destinations, flight_search.get_iata_code_by_city_name
    )

    tomorrow = f'{date.today() + timedelta(days=1):%d/%m/%Y}'
    six_months_from_now = f'{date.today() + timedelta(days=180):%d/%m/%Y}'

    cheap_flights = find_cheap_flights(
        destinations,
        flight_search.search_flights,
        {
            'fly_from': 'SSA',
            'date_from': tomorrow,
            'date_to': six_months_from_now,
            'curr': 'BRL',
            'max_stopovers': 2,
        },
    )

    notify(cheap_flights, email_client, EMAIL.SENDER, EMAIL.RECIPIENTS)


if __name__ == '__main__':
    main()
