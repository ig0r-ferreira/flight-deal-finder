from pydantic import BaseSettings, HttpUrl, SecretStr


class SheetAPISettings(BaseSettings):
    SPREADSHEET_URL: HttpUrl
    AUTH: SecretStr | None = None

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


class FlightAPISettings(BaseSettings):
    BASE_URL: HttpUrl
    KEY: SecretStr

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        env_prefix = 'FLIGHT_API_'
