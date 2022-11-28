from typing import Any, Callable, Iterable

from flight_deals.data_manager import DataManager
from flight_deals.email_client import EmailClient, make_message
from flight_deals.flight_data import FlightItinerary


def update_destination_codes(
    destinations: DataManager, get_code_fn: Callable[..., str]
) -> None:
    for row in destinations.data:
        row['iataCode'] = get_code_fn(row['city'])

    destinations.update_data()


def find_cheap_flights(
    destinations: DataManager,
    search_flights_fn: Callable[..., list[dict[str, Any]]],
    search_params: dict[str, Any],
) -> list[FlightItinerary]:

    cheap_flights = []

    for row in destinations.data:
        destination_code = row.get('iataCode', '')
        if not destination_code:
            continue

        search_params.update(
            {'fly_to': destination_code, 'price_to': row.get('lowestPrice')}
        )

        available_flights = search_flights_fn(search_params)
        if not available_flights:
            continue

        cheap_flights.append(FlightItinerary.parse_obj(available_flights[0]))

    return cheap_flights


def notify(
    flights: Iterable[FlightItinerary],
    email_client: EmailClient,
    sender: str,
    recipients: str | list[str],
) -> None:
    for flight in flights:
        email_client.send_message(
            make_message(
                from_address=sender,
                to_address=recipients,
                subject=(
                    'Low price alert! Flight from '
                    f'{flight.departure_city} to {flight.destination_city}'
                ),
                body=str(flight),
            )
        )
