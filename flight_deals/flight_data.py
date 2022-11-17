from datetime import datetime
from decimal import Decimal
from itertools import dropwhile, takewhile
from typing import Any

from pydantic import BaseModel, Field


class Flight(BaseModel):
    """This class represents the single flight data."""

    departure_location_code: str = Field(..., alias='flyFrom')
    departure_city: str = Field(..., alias='cityFrom')
    departure_city_code: str = Field(..., alias='cityCodeFrom')
    arrival_location_code: str = Field(..., alias='flyTo')
    arrival_city: str = Field(..., alias='cityTo')
    arrival_city_code: str = Field(..., alias='cityCodeTo')
    departure_datetime: datetime = Field(..., alias='local_departure')
    arrival_datetime: datetime = Field(..., alias='local_arrival')
    is_return: bool = Field(..., alias='return')

    def __str__(self) -> str:
        title = (
            '{departure_city} ({departure_city_code})'
            ' ==> '
            '{arrival_city} ({arrival_city_code})'
        )

        return '\n'.join(
            (
                title,
                'Departure on: {departure_datetime:%d/%m/%Y %H:%M:%S}',
                'Arrival on: {arrival_datetime:%d/%m/%Y %H:%M:%S}',
            )
        ).format(**self.dict())


class FlightItinerary(BaseModel):
    """This class represents flight itinerary data."""

    departure_city: str = Field(..., alias='cityFrom')
    departure_city_code: str = Field(..., alias='cityCodeFrom')
    destination_city: str = Field(..., alias='cityTo')
    destination_city_code: str = Field(..., alias='cityCodeTo')
    price: Decimal
    conversion: dict[str, Any]
    days_of_stay: int = Field(..., alias='nightsInDest')
    route: list[Flight] = Field(..., min_items=2)

    @property
    def currency(self) -> str:
        return next(iter(self.conversion))

    @property
    def departing_route(self) -> list[Flight]:
        return list(takewhile(lambda flight: not flight.is_return, self.route))

    @property
    def return_route(self) -> list[Flight]:
        return list(dropwhile(lambda flight: not flight.is_return, self.route))

    def __str__(self) -> str:
        details = (
            f'{self.departure_city} ({self.departure_city_code})'
            ' ==> '
            f'{self.destination_city} ({self.destination_city_code})\n'
            f'Price: {self.price:.2f} {self.currency}\n'
            f'Stay: {self.days_of_stay} days'
        )

        for type_route, flights in (
            ('>>> Departing', self.departing_route),
            ('<<< Returning', self.return_route),
        ):
            details += '\n\n'.join((f'\n\n{type_route}:', *map(str, flights)))

        return details
