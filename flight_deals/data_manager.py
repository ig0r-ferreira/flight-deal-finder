from typing import Any

from flight_deals.sheet_api import SheetAPI


class DataManager:
    def __init__(self, sheet_name: str, sheet_api: SheetAPI) -> None:
        self.sheet_name = sheet_name
        self.sheet_api = sheet_api
        self.data: list[dict[str, Any]] = []

    def load_data(self) -> None:
        self.data = self.sheet_api.get_rows_from_sheet(self.sheet_name)

    def update_data(self) -> None:
        for record in self.data:
            self.sheet_api.update_sheet_row(
                sheet_name=self.sheet_name,
                row_id=record['id'],
                body=record,
            )
        self.load_data()
