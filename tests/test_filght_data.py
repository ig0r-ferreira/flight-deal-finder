import pytest

from flight_deals.flight_data import Flight, FlightItinerary


@pytest.fixture
def flight() -> Flight:
    return Flight.parse_obj(
        {
            'flyFrom': 'GRU',
            'flyTo': 'EWR',
            'cityFrom': 'São Paulo',
            'cityCodeFrom': 'SAO',
            'cityTo': 'New York',
            'cityCodeTo': 'NYC',
            'return': 0,
            'local_arrival': '2023-04-18T05:40:00.000Z',
            'utc_arrival': '2023-04-18T09:40:00.000Z',
            'local_departure': '2023-04-17T21:00:00.000Z',
            'utc_departure': '2023-04-18T00:00:00.000Z',
        }
    )


@pytest.fixture
def flight_itinerary(flight: Flight) -> FlightItinerary:
    return FlightItinerary.parse_obj(
        {
            'cityFrom': 'São Paulo',
            'cityCodeFrom': 'SAO',
            'cityTo': 'New York',
            'cityCodeTo': 'NYC',
            'price': 4206,
            'conversion': {'BRL': 4206, 'EUR': 745.429063},
            'nightsInDest': 7,
            'route': [
                flight.dict(by_alias=True),
                {
                    'flyFrom': 'EWR',
                    'flyTo': 'GRU',
                    'cityFrom': 'New York',
                    'cityCodeFrom': 'NYC',
                    'cityTo': 'São Paulo',
                    'cityCodeTo': 'SAO',
                    'airline': 'UA',
                    'return': 1,
                    'local_arrival': '2023-04-26T08:50:00.000Z',
                    'utc_arrival': '2023-04-26T11:50:00.000Z',
                    'local_departure': '2023-04-25T22:10:00.000Z',
                    'utc_departure': '2023-04-26T02:10:00.000Z',
                },
            ],
        }
    )


def test_flight_as_str(flight: Flight) -> None:
    flight_as_str = (
        'São Paulo (SAO) ==> New York (NYC)\n'
        'Departure on: 17/04/2023 21:00:00\n'
        'Arrival on: 18/04/2023 05:40:00'
    )
    assert str(flight) == flight_as_str


def test_flight_itinerary_as_str(flight_itinerary: FlightItinerary) -> None:
    flight_itinerary_as_str = (
        'São Paulo (SAO) ==> New York (NYC)\n'
        'Price: 4206.00 BRL\n'
        'Stay: 7 days\n\n'
        '>>> Departing:\n\n'
        'São Paulo (SAO) ==> New York (NYC)\n'
        'Departure on: 17/04/2023 21:00:00\n'
        'Arrival on: 18/04/2023 05:40:00\n\n'
        '<<< Returning:\n\n'
        'New York (NYC) ==> São Paulo (SAO)\n'
        'Departure on: 25/04/2023 22:10:00\n'
        'Arrival on: 26/04/2023 08:50:00'
    )

    assert str(flight_itinerary) == flight_itinerary_as_str
