import dotenv
from pydantic import BaseSettings, HttpUrl, SecretStr

dotenv.load_dotenv(dotenv.find_dotenv())


class SheetAPISettings(BaseSettings):
    SPREADSHEET_URL: HttpUrl
    AUTH: SecretStr | None = None

    class Config:
        env_prefix = 'SHEET_API_'


class FlightAPISettings(BaseSettings):
    BASE_URL: HttpUrl
    KEY: SecretStr

    class Config:
        env_prefix = 'FLIGHT_API_'


class EmailSettings(BaseSettings):
    SENDER: str
    RECIPIENTS: str

    class Config:
        env_prefix = 'EMAIL_'


class Settings(BaseSettings):
    SHEET_API: SheetAPISettings = SheetAPISettings()
    FLIGHT_API: FlightAPISettings = FlightAPISettings()
    EMAIL: EmailSettings = EmailSettings()


def get_settings() -> Settings:
    return Settings()
