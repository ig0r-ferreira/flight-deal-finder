from pydantic import BaseSettings, HttpUrl, SecretStr


class SheetAPISettings(BaseSettings):
    SPREADSHEET_URL: HttpUrl
    AUTH: SecretStr | None = None

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
